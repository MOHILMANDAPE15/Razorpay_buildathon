"""Cost-weighted Evaluator for RTO fraud detection hypotheses."""

import time
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from app.core.config import CostModelConfig, cost_config
from app.core.sandbox import execute_rule_sandboxed, SecurityError, RuleExecutionError, RuleTimeoutError
from app.data.schema import extract_features_and_labels, sanitize_features
from app.engine.types import (
    CostMetrics,
    DiagnosticOrder,
    EvaluationReport,
    RuleHypothesis,
    StandardMetrics,
)


class CostWeightedEvaluator:
    """Evaluates fraud detection rules using both standard statistical metrics
    and domain-calibrated per-order financial fitness."""

    def __init__(self, config: Optional[CostModelConfig] = None):
        self.config = config or cost_config

    def evaluate_hypothesis(
        self,
        hypothesis: RuleHypothesis,
        df: pd.DataFrame,
        top_k_diagnostics: int = 5,
    ) -> EvaluationReport:
        """Executes a hypothesis in a sandbox and evaluates its statistical and financial performance.
        
        Args:
            hypothesis: The RuleHypothesis to evaluate.
            df: Input dataset (e.g. validation split).
            top_k_diagnostics: Number of top false positive and false negative cases to extract.
            
        Returns:
            EvaluationReport: Full metrics and failure diagnostics.
        """
        start_time = time.perf_counter()
        
        # Split into features, labels, and order values with strict sanitization
        try:
            sanitized_features, y_true, order_values = extract_features_and_labels(df)
        except Exception as e:
            return EvaluationReport(
                hypothesis_id=hypothesis.id,
                hypothesis_name=hypothesis.name,
                is_valid=False,
                error_message=f"Dataset preparation error: {str(e)}",
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )

        # Execute rule inside security sandbox
        try:
            y_pred = execute_rule_sandboxed(
                code_str=hypothesis.code,
                df_features=sanitized_features,
                timeout_sec=self.config.rule_timeout_sec,
            )
        except (SecurityError, RuleExecutionError, RuleTimeoutError, SyntaxError) as e:
            return EvaluationReport(
                hypothesis_id=hypothesis.id,
                hypothesis_name=hypothesis.name,
                is_valid=False,
                error_message=f"{type(e).__name__}: {str(e)}",
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )

        execution_time_ms = (time.perf_counter() - start_time) * 1000

        # Calculate metrics and extract failure cases
        return self._compute_evaluation_report(
            hypothesis_id=hypothesis.id,
            hypothesis_name=hypothesis.name,
            y_pred=y_pred,
            y_true=y_true,
            order_values=order_values,
            sanitized_features=sanitized_features,
            execution_time_ms=execution_time_ms,
            top_k_diagnostics=top_k_diagnostics,
        )

    def evaluate_predictions(
        self,
        y_pred: np.ndarray,
        y_true: np.ndarray,
        order_values: np.ndarray,
        sanitized_features: pd.DataFrame,
        hypothesis_id: str = "direct_eval",
        hypothesis_name: str = "Direct Predictions",
        top_k_diagnostics: int = 5,
    ) -> EvaluationReport:
        """Evaluates pre-computed binary predictions directly (e.g. from an ensemble or baseline model)."""
        return self._compute_evaluation_report(
            hypothesis_id=hypothesis_id,
            hypothesis_name=hypothesis_name,
            y_pred=y_pred,
            y_true=y_true,
            order_values=order_values,
            sanitized_features=sanitized_features,
            execution_time_ms=0.0,
            top_k_diagnostics=top_k_diagnostics,
        )

    def _compute_evaluation_report(
        self,
        hypothesis_id: str,
        hypothesis_name: str,
        y_pred: np.ndarray,
        y_true: np.ndarray,
        order_values: np.ndarray,
        sanitized_features: pd.DataFrame,
        execution_time_ms: float,
        top_k_diagnostics: int,
    ) -> EvaluationReport:
        """Computes statistical metrics, per-order cost models, and failure diagnostics."""
        y_pred = np.asarray(y_pred).astype(int)
        y_true = np.asarray(y_true).astype(int)
        order_values = np.asarray(order_values).astype(float)
        
        n_total = len(y_true)
        if n_total == 0:
            return EvaluationReport(
                hypothesis_id=hypothesis_id,
                hypothesis_name=hypothesis_name,
                is_valid=False,
                error_message="Empty dataset provided for evaluation.",
            )

        # Confusion matrix elements
        tp_mask = (y_pred == 1) & (y_true == 1)
        fp_mask = (y_pred == 1) & (y_true == 0)
        tn_mask = (y_pred == 0) & (y_true == 0)
        fn_mask = (y_pred == 0) & (y_true == 1)

        tp_count = int(np.sum(tp_mask))
        fp_count = int(np.sum(fp_mask))
        tn_count = int(np.sum(tn_mask))
        fn_count = int(np.sum(fn_mask))
        flagged_count = tp_count + fp_count

        # Standard metrics
        precision = float(tp_count / flagged_count) if flagged_count > 0 else 0.0
        actual_positives = tp_count + fn_count
        recall = float(tp_count / actual_positives) if actual_positives > 0 else 0.0
        f1 = (
            float(2 * (precision * recall) / (precision + recall))
            if (precision + recall) > 0
            else 0.0
        )
        accuracy = float((tp_count + tn_count) / n_total)
        flag_rate = float(flagged_count / n_total)

        standard_metrics = StandardMetrics(
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1=round(f1, 4),
            accuracy=round(accuracy, 4),
            total_orders=n_total,
            flagged_orders=flagged_count,
            flag_rate=round(flag_rate, 4),
            true_positives=tp_count,
            false_positives=fp_count,
            true_negatives=tn_count,
            false_negatives=fn_count,
        )

        # Cost-weighted metrics
        # 1. True Positive Value: Rs. 250 (avoided loss) per prevented RTO
        avoided_rto_loss = float(tp_count * self.config.avoided_rto_cost_inr)

        # 2. False Positive Cost: Sum of (order_value * margin) per wrongly-blocked customer
        fp_order_values = order_values[fp_mask]
        fp_insult_costs = fp_order_values * self.config.fp_margin_loss_rate
        total_fp_cost = float(np.sum(fp_insult_costs))
        avg_fp_cost = float(np.mean(fp_insult_costs)) if fp_count > 0 else 0.0

        # 3. Net Financial Impact
        net_savings = avoided_rto_loss - total_fp_cost
        cost_efficiency = (
            avoided_rto_loss / max(total_fp_cost, 1.0)
            if total_fp_cost > 0
            else avoided_rto_loss
        )

        cost_metrics = CostMetrics(
            avoided_rto_loss_inr=round(avoided_rto_loss, 2),
            false_positive_insult_cost_inr=round(total_fp_cost, 2),
            net_financial_savings_inr=round(net_savings, 2),
            cost_efficiency_ratio=round(cost_efficiency, 2),
            avg_fp_insult_cost_inr=round(avg_fp_cost, 2),
        )

        # Extract Diagnostic Failure Cases for LLM Reflector
        top_fps = self._extract_diagnostic_cases(
            mask=fp_mask,
            error_type="FALSE_POSITIVE",
            order_values=order_values,
            sanitized_features=sanitized_features,
            y_true=y_true,
            y_pred=y_pred,
            top_k=top_k_diagnostics,
        )

        top_fns = self._extract_diagnostic_cases(
            mask=fn_mask,
            error_type="FALSE_NEGATIVE",
            order_values=order_values,
            sanitized_features=sanitized_features,
            y_true=y_true,
            y_pred=y_pred,
            top_k=top_k_diagnostics,
        )

        return EvaluationReport(
            hypothesis_id=hypothesis_id,
            hypothesis_name=hypothesis_name,
            is_valid=True,
            execution_time_ms=round(execution_time_ms, 2),
            standard_metrics=standard_metrics,
            cost_metrics=cost_metrics,
            top_false_positives=top_fps,
            top_false_negatives=top_fns,
        )

    def _extract_diagnostic_cases(
        self,
        mask: np.ndarray,
        error_type: str,
        order_values: np.ndarray,
        sanitized_features: pd.DataFrame,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        top_k: int,
    ) -> List[DiagnosticOrder]:
        """Extracts top misclassified cases sorted by financial impact."""
        indices = np.where(mask)[0]
        if len(indices) == 0:
            return []

        # Sort indices by cost impact
        if error_type == "FALSE_POSITIVE":
            # Sort by highest insult cost: order_value * margin
            impact_scores = order_values[indices] * self.config.fp_margin_loss_rate
        else:
            # Sort by highest missed order value
            impact_scores = order_values[indices]

        # Get top-K indices
        sorted_order = np.argsort(impact_scores)[::-1][:top_k]
        selected_indices = indices[sorted_order]

        diagnostics: List[DiagnosticOrder] = []
        for idx in selected_indices:
            row_dict = sanitized_features.iloc[idx].to_dict()
            order_id = str(row_dict.get("order_id", f"row_{idx}"))
            val = float(order_values[idx])
            
            if error_type == "FALSE_POSITIVE":
                cost_impact = round(val * self.config.fp_margin_loss_rate, 2)
                reason = (
                    f"Genuine customer order falsely flagged. High merchant profit insult cost (₹{cost_impact}) "
                    f"on order value ₹{val}."
                )
            else:
                cost_impact = round(self.config.avoided_rto_cost_inr, 2)
                reason = (
                    f"RTO fraud missed by rule. ₹{self.config.avoided_rto_cost_inr} reverse logistics loss incurred "
                    f"on order value ₹{val}."
                )

            diagnostics.append(
                DiagnosticOrder(
                    order_id=order_id,
                    order_value=val,
                    true_label=int(y_true[idx]),
                    predicted_label=int(y_pred[idx]),
                    cost_impact_inr=cost_impact,
                    error_type=error_type,
                    features=row_dict,
                    diagnostic_reason=reason,
                )
            )

        return diagnostics
