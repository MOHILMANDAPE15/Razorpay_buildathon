"""Regression Suite (Gate 1) for anti-catastrophic-forgetting verification.

Gate Architecture:
- Gate 1: Regression Suite (historical validation re-check against baseline with noise tolerance)
- Gate 2: Held-Out Test Split Single-Touch Verification (final frozen ensemble proof)
- Gate 3: Defense-Only Audit Gate (keyword scanning + LLM adversarial intent judge)
"""

from typing import List, Optional, Tuple
import pandas as pd

from app.engine.evaluator import CostWeightedEvaluator
from app.engine.types import EvaluationReport, RegressionReport, RuleHypothesis


class RegressionHarness:
    """Gate 1: Re-validates newly generated or mutated hypotheses on historical validation data
    to prevent regressions (catastrophic forgetting) before promotion."""

    def __init__(
        self,
        evaluator: Optional[CostWeightedEvaluator] = None,
        max_recall_drop_tolerance: float = 0.03,    # Max 3% recall degradation allowed
        max_cost_drop_tolerance_inr: float = 500.0, # Rs. 500 noise buffer tolerance band (avoids zero-tolerance sampling jitter)
    ):
        self.evaluator = evaluator or CostWeightedEvaluator()
        self.max_recall_drop_tolerance = max_recall_drop_tolerance
        self.max_cost_drop_tolerance_inr = max_cost_drop_tolerance_inr

    def evaluate_candidate(
        self,
        candidate_hypothesis: RuleHypothesis,
        df_validation: pd.DataFrame,
        baseline_report: Optional[EvaluationReport] = None,
        baseline_ci_lower_inr: Optional[float] = None,
    ) -> Tuple[bool, RegressionReport, EvaluationReport]:
        """Runs candidate through Gate 1 regression testing.
        
        Args:
            candidate_hypothesis: The proposed or mutated hypothesis to test.
            df_validation: The validation dataset split.
            baseline_report: Evaluation report of current active baseline (if any).
            baseline_ci_lower_inr: Optional bootstrap CI lower bound of baseline net savings.
                                   If provided, candidate must not fall below this lower bound.
            
        Returns:
            Tuple[bool, RegressionReport, EvaluationReport]:
                - passed (bool): True if candidate passed Gate 1
                - regression_report (RegressionReport): Details of regression check
                - candidate_eval_report (EvaluationReport): Full evaluation report of candidate
        """
        # Step 1: Run candidate evaluation on validation split
        candidate_eval = self.evaluator.evaluate_hypothesis(
            hypothesis=candidate_hypothesis,
            df=df_validation,
        )

        if not candidate_eval.is_valid:
            reasons = [f"Rule failed execution: {candidate_eval.error_message}"]
            report = RegressionReport(
                gate_name="Gate 1: Regression Suite",
                status="FAILED",
                candidate_hypothesis_id=candidate_hypothesis.id,
                baseline_net_savings_inr=baseline_report.cost_metrics.net_financial_savings_inr if baseline_report and baseline_report.cost_metrics else 0.0,
                candidate_net_savings_inr=0.0,
                delta_net_savings_inr=0.0,
                baseline_recall=baseline_report.standard_metrics.recall if baseline_report and baseline_report.standard_metrics else 0.0,
                candidate_recall=0.0,
                delta_recall=0.0,
                regressed_order_count=0,
                reasons=reasons,
                details=f"Gate 1 FAILED: Rule execution error for hypothesis '{candidate_hypothesis.id}'.",
            )
            return False, report, candidate_eval

        # Step 2: Compare against baseline if one exists
        if baseline_report is None or not baseline_report.is_valid or baseline_report.cost_metrics is None or baseline_report.standard_metrics is None:
            # First generation or cold-start: pass if candidate generates positive or neutral net value
            candidate_net = candidate_eval.cost_metrics.net_financial_savings_inr
            candidate_recall = candidate_eval.standard_metrics.recall

            passed = candidate_net >= 0.0
            reasons = []
            if not passed:
                reasons.append(
                    f"Candidate produces negative net financial impact (₹{candidate_net})."
                )

            report = RegressionReport(
                gate_name="Gate 1: Regression Suite",
                status="PASSED" if passed else "FAILED",
                candidate_hypothesis_id=candidate_hypothesis.id,
                baseline_net_savings_inr=0.0,
                candidate_net_savings_inr=candidate_net,
                delta_net_savings_inr=candidate_net,
                baseline_recall=0.0,
                candidate_recall=candidate_recall,
                delta_recall=candidate_recall,
                regressed_order_count=0,
                reasons=reasons,
                details="Initial cold-start evaluation without prior baseline.",
            )
            return passed, report, candidate_eval

        # Compare metrics with existing baseline
        base_net = baseline_report.cost_metrics.net_financial_savings_inr
        cand_net = candidate_eval.cost_metrics.net_financial_savings_inr
        delta_net = cand_net - base_net

        base_recall = baseline_report.standard_metrics.recall
        cand_recall = candidate_eval.standard_metrics.recall
        delta_recall = cand_recall - base_recall

        reasons: List[str] = []
        passed = True

        # Check 1: Financial Degradation Check (respects bootstrap CI lower bound if provided, else Rs. 500 buffer)
        if baseline_ci_lower_inr is not None:
            if cand_net < baseline_ci_lower_inr:
                passed = False
                reasons.append(
                    f"Candidate net savings (₹{cand_net:.2f}) fell below baseline bootstrap 95% CI lower bound (₹{baseline_ci_lower_inr:.2f})."
                )
        elif delta_net < -self.max_cost_drop_tolerance_inr:
            passed = False
            reasons.append(
                f"Net financial savings regressed by ₹{abs(round(delta_net, 2))} "
                f"(Baseline: ₹{base_net} vs Candidate: ₹{cand_net}, tolerance: ₹{self.max_cost_drop_tolerance_inr})."
            )

        # Check 2: Catastrophic Recall Drop Check
        if delta_recall < -self.max_recall_drop_tolerance:
            passed = False
            reasons.append(
                f"Recall degraded significantly by {abs(round(delta_recall * 100, 2))}% "
                f"(Baseline: {round(base_recall * 100, 2)}% vs Candidate: {round(cand_recall * 100, 2)}%)."
            )

        report = RegressionReport(
            gate_name="Gate 1: Regression Suite",
            status="PASSED" if passed else "FAILED",
            candidate_hypothesis_id=candidate_hypothesis.id,
            baseline_net_savings_inr=base_net,
            candidate_net_savings_inr=cand_net,
            delta_net_savings_inr=round(delta_net, 2),
            baseline_recall=base_recall,
            candidate_recall=cand_recall,
            delta_recall=round(delta_recall, 4),
            regressed_order_count=max(0, baseline_report.standard_metrics.true_positives - candidate_eval.standard_metrics.true_positives),
            reasons=reasons,
            details="Gate 1 verification complete against active baseline.",
        )

        return passed, report, candidate_eval
