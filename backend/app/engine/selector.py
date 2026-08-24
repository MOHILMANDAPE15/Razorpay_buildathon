"""Cost-Weighted Diversity Selector and Rule Pruning Engine.

Selects the optimal compact ensemble of non-redundant evolved rules using submodular
forward greedy selection and Jaccard redundancy pruning.
"""

from typing import Callable, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from app.core.sandbox import (
    RuleExecutionError,
    RuleTimeoutError,
    SecurityError,
    execute_rule_sandboxed,
)
from app.engine.evaluator import CostWeightedEvaluator
from app.engine.types import EvaluationReport, RuleHypothesis


class EnsembleSelectionResult(BaseModel):
    """Result of forward greedy ensemble selection and pruning."""
    selected_rules: List[RuleHypothesis]
    pruned_rules: List[RuleHypothesis]
    total_selected: int
    total_pruned: int
    baseline_single_best_net_inr: float
    ensemble_net_savings_inr: float
    ensemble_precision: float
    ensemble_recall: float
    ensemble_f1: float
    marginal_gains_inr: List[float] = Field(default_factory=list)
    selection_trace: List[str] = Field(default_factory=list)


class EnsembleRule:
    """Compiled ensemble of multiple fraud rules combined with boolean OR logic."""

    def __init__(self, rules: List[RuleHypothesis]):
        self.rules = rules

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Executes all rules in the ensemble and returns their boolean OR union."""
        if not self.rules:
            return np.zeros(len(df), dtype=bool)

        combined_flags = np.zeros(len(df), dtype=bool)
        for r in self.rules:
            flags = execute_rule_sandboxed(r.code, df)
            combined_flags = combined_flags | flags

        return combined_flags

    def explain_order(self, order_series: pd.Series) -> List[str]:
        """Returns which rules in the ensemble flagged a specific order."""
        df_single = pd.DataFrame([order_series])
        triggered = []
        for r in self.rules:
            try:
                flag = bool(execute_rule_sandboxed(r.code, df_single)[0])
                if flag:
                    triggered.append(f"[{r.id}] {r.name}")
            except Exception:
                pass
        return triggered


class RulePruner:
    """Prunes dead, negative-value, and duplicate/overlapping rules."""

    def __init__(self, jaccard_threshold: float = 0.80, min_precision: float = 0.20):
        self.jaccard_threshold = jaccard_threshold
        self.min_precision = min_precision

    def calculate_jaccard_similarity(self, flags_a: np.ndarray, flags_b: np.ndarray) -> float:
        """Calculates Jaccard overlap between two boolean prediction vectors."""
        intersection = np.sum(flags_a & flags_b)
        union = np.sum(flags_a | flags_b)
        if union == 0:
            return 0.0
        return float(intersection / union)

    def prune_candidates(
        self,
        candidates: List[RuleHypothesis],
        df_eval: pd.DataFrame,
        evaluator: CostWeightedEvaluator,
    ) -> Tuple[List[RuleHypothesis], List[RuleHypothesis], Dict[str, str]]:
        """Filters out non-viable rules and highly overlapping duplicates.
        
        Returns:
            (retained_rules, pruned_rules, prune_reasons)
        """
        valid_rules: List[Tuple[RuleHypothesis, EvaluationReport, np.ndarray]] = []
        pruned_rules: List[RuleHypothesis] = []
        prune_reasons: Dict[str, str] = {}

        # 1. First pass: filter out runtime errors, negative net savings, and poor precision
        for cand in candidates:
            try:
                flags = execute_rule_sandboxed(cand.code, df_eval)
                report = evaluator.evaluate_flags(flags, df_eval, cand.id, cand.name)

                if report.cost_metrics.net_financial_savings_inr <= 0:
                    cand.status = "pruned"
                    pruned_rules.append(cand)
                    prune_reasons[cand.id] = (
                        f"Non-positive financial impact (Rs. {report.cost_metrics.net_financial_savings_inr:,.2f})"
                    )
                    continue

                if report.standard_metrics.precision < self.min_precision:
                    cand.status = "pruned"
                    pruned_rules.append(cand)
                    prune_reasons[cand.id] = (
                        f"Low precision ({report.standard_metrics.precision*100:.1f}% < {self.min_precision*100:.0f}%)"
                    )
                    continue

                valid_rules.append((cand, report, flags))

            except (RuleExecutionError, SecurityError, RuleTimeoutError, Exception) as e:
                cand.status = "dead"
                pruned_rules.append(cand)
                prune_reasons[cand.id] = f"Execution error: {e}"

        # 2. Second pass: sort by Net Financial Savings descending
        valid_rules.sort(
            key=lambda x: x[1].cost_metrics.net_financial_savings_inr,
            reverse=True,
        )

        # 3. Third pass: pairwise Jaccard redundancy pruning
        retained: List[RuleHypothesis] = []
        retained_flags: List[np.ndarray] = []

        for cand, rep, flags in valid_rules:
            is_redundant = False
            for prev_cand, prev_flags in zip(retained, retained_flags):
                jaccard = self.calculate_jaccard_similarity(flags, prev_flags)
                if jaccard >= self.jaccard_threshold:
                    is_redundant = True
                    cand.status = "pruned"
                    pruned_rules.append(cand)
                    prune_reasons[cand.id] = (
                        f"Redundant with superior rule [{prev_cand.id}] (Jaccard similarity: {jaccard*100:.1f}%)"
                    )
                    break

            if not is_redundant:
                cand.status = "alive"
                retained.append(cand)
                retained_flags.append(flags)

        return retained, pruned_rules, prune_reasons


class CostWeightedSelector:
    """Submodular forward greedy selector that builds the optimal fraud rule ensemble."""

    def __init__(
        self,
        evaluator: Optional[CostWeightedEvaluator] = None,
        pruner: Optional[RulePruner] = None,
    ):
        self.evaluator = evaluator or CostWeightedEvaluator()
        self.pruner = pruner or RulePruner()

    def select_ensemble(
        self,
        candidates: List[RuleHypothesis],
        df_eval: pd.DataFrame,
        max_ensemble_size: int = 4,
        min_marginal_gain_inr: float = 250.0,
    ) -> EnsembleSelectionResult:
        """Executes forward greedy selection to build the optimal synergistic ensemble.
        
        Args:
            candidates: Pool of candidate hypotheses.
            df_eval: Evaluation dataset DataFrame.
            max_ensemble_size: Maximum rules in selected ensemble.
            min_marginal_gain_inr: Minimum incremental net ₹ savings required to include an extra rule.
        """
        # 1. Prune redundant & low-quality rules
        retained, pruned, prune_reasons = self.pruner.prune_candidates(
            candidates, df_eval, self.evaluator
        )

        if not retained:
            return EnsembleSelectionResult(
                selected_rules=[],
                pruned_rules=pruned,
                total_selected=0,
                total_pruned=len(pruned),
                baseline_single_best_net_inr=0.0,
                ensemble_net_savings_inr=0.0,
                ensemble_precision=0.0,
                ensemble_recall=0.0,
                ensemble_f1=0.0,
                selection_trace=["No viable rules survived pruning."],
            )

        # Pre-compute prediction flags for each retained rule
        rule_flags_map = {r.id: execute_rule_sandboxed(r.code, df_eval) for r in retained}

        # 2. Pick initial champion rule (highest individual net savings)
        best_initial_rule = None
        best_initial_report = None
        best_initial_savings = -float("inf")

        for r in retained:
            flags = rule_flags_map[r.id]
            rep = self.evaluator.evaluate_flags(flags, df_eval, r.id, r.name)
            if rep.cost_metrics.net_financial_savings_inr > best_initial_savings:
                best_initial_savings = rep.cost_metrics.net_financial_savings_inr
                best_initial_rule = r
                best_initial_report = rep

        selected: List[RuleHypothesis] = [best_initial_rule]
        remaining: List[RuleHypothesis] = [r for r in retained if r.id != best_initial_rule.id]
        current_combined_flags = rule_flags_map[best_initial_rule.id].copy()
        current_net_savings = best_initial_savings
        current_report = best_initial_report

        marginal_gains = [best_initial_savings]
        trace = [
            f"Selected initial rule [{best_initial_rule.id}] '{best_initial_rule.name}' "
            f"-> Net Rs. {best_initial_savings:,.2f}"
        ]

        # 3. Forward greedy iteration
        while remaining and len(selected) < max_ensemble_size:
            best_cand = None
            best_cand_gain = -float("inf")
            best_cand_combined_flags = None
            best_cand_report = None

            for cand in remaining:
                cand_flags = rule_flags_map[cand.id]
                new_combined = current_combined_flags | cand_flags
                new_rep = self.evaluator.evaluate_flags(new_combined, df_eval, cand.id, cand.name)
                marginal_gain = (
                    new_rep.cost_metrics.net_financial_savings_inr - current_net_savings
                )

                if marginal_gain > best_cand_gain:
                    best_cand_gain = marginal_gain
                    best_cand = cand
                    best_cand_combined_flags = new_combined
                    best_cand_report = new_rep

            if best_cand is not None and best_cand_gain >= min_marginal_gain_inr:
                selected.append(best_cand)
                remaining.remove(best_cand)
                current_combined_flags = best_cand_combined_flags
                current_net_savings = best_cand_report.cost_metrics.net_financial_savings_inr
                current_report = best_cand_report
                marginal_gains.append(best_cand_gain)
                trace.append(
                    f"Added [{best_cand.id}] '{best_cand.name}' "
                    f"(Marginal Lift: +Rs. {best_cand_gain:,.2f} -> Total Net: Rs. {current_net_savings:,.2f})"
                )
            else:
                trace.append(
                    f"Stopping: Best remaining marginal gain was Rs. {best_cand_gain:,.2f} "
                    f"(below threshold Rs. {min_marginal_gain_inr:,.2f})"
                )
                break

        # Mark unselected rules as candidate/pruned
        for r in remaining:
            r.status = "candidate"

        for r in selected:
            r.status = "champion"

        return EnsembleSelectionResult(
            selected_rules=selected,
            pruned_rules=pruned,
            total_selected=len(selected),
            total_pruned=len(pruned),
            baseline_single_best_net_inr=best_initial_savings,
            ensemble_net_savings_inr=current_net_savings,
            ensemble_precision=current_report.standard_metrics.precision,
            ensemble_recall=current_report.standard_metrics.recall,
            ensemble_f1=current_report.standard_metrics.f1,
            marginal_gains_inr=marginal_gains,
            selection_trace=trace,
        )
