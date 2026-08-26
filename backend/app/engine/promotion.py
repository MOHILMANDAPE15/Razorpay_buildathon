"""Promotion & Rollback Engine (Sep 3 Milestone).

Manages the Champion/Challenger deployment state machine, Gate 1 & 3 promotion checks,
and automated rollback if post-promotion monitoring reveals degradation.

METHODOLOGICAL GUARANTEE:
Rollback and post-promotion verification check strictly against rolling realized-outcome data
(from the OutcomeDriftDetector or streaming validation telemetry), NEVER held_out_test.csv.
Held-out test is reserved exclusively for single-touch final evaluation in Step 3.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from app.core.config import cost_config
from app.data.schema import sanitize_features
from app.engine.defense_audit import DefenseOnlyAuditGate
from app.engine.evaluator import CostWeightedEvaluator
from app.engine.regression import RegressionHarness
from app.engine.selector import EnsembleRule
from app.engine.types import EvaluationReport, RegressionReport, RuleHypothesis


class ChampionSnapshot(BaseModel):
    """Immutable versioned snapshot of a deployed champion ensemble."""
    version: int
    champion_id: str
    rules: List[RuleHypothesis]
    promoted_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    validation_net_savings_inr: float
    validation_precision: float
    validation_recall: float
    gate_1_status: str = "PASSED"
    gate_3_status: str = "PASSED"
    notes: str = ""


class PromotionDecision(BaseModel):
    """Result of evaluating a challenger ensemble for production promotion."""
    promoted: bool
    version: int
    challenger_id: str
    gate_1_passed: bool
    gate_3_passed: bool
    baseline_net_savings_inr: float
    challenger_net_savings_inr: float
    delta_net_savings_inr: float
    reasons: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RollbackDecision(BaseModel):
    """Result of automated rollback verification."""
    rolled_back: bool
    active_version_before: int
    restored_version: Optional[int] = None
    reason: str
    realized_net_savings_inr: float
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PromotionManager:
    """Manages active champion deployment, gate verification, and automated rollback."""

    def __init__(
        self,
        evaluator: Optional[CostWeightedEvaluator] = None,
        regression_harness: Optional[RegressionHarness] = None,
        defense_gate: Optional[DefenseOnlyAuditGate] = None,
    ):
        self.evaluator = evaluator or CostWeightedEvaluator()
        self.regression_harness = regression_harness or RegressionHarness(evaluator=self.evaluator)
        self.defense_gate = defense_gate or DefenseOnlyAuditGate(use_llm_judge=False)
        self.current_champion: Optional[ChampionSnapshot] = None
        self.champion_history: List[ChampionSnapshot] = []
        self.promotion_decisions: List[PromotionDecision] = []
        self.rollback_decisions: List[RollbackDecision] = []
        self.version_counter: int = 0

    def get_active_ensemble(self) -> Optional[EnsembleRule]:
        """Returns the currently active champion ensemble for scoring."""
        if not self.current_champion or not self.current_champion.rules:
            return None
        return EnsembleRule(self.current_champion.rules)

    def evaluate_and_promote(
        self,
        challenger_rules: List[RuleHypothesis],
        df_validation: pd.DataFrame,
        notes: str = "",
    ) -> PromotionDecision:
        """Evaluates challenger rules through Gate 1 & Gate 3 and promotes if superior."""
        challenger_ensemble = EnsembleRule(challenger_rules)
        sanitized_val = sanitize_features(df_validation)
        flags = challenger_ensemble.predict(sanitized_val)
        challenger_eval = self.evaluator.evaluate_flags(
            flags, df_validation, "challenger_eval", "Challenger Ensemble"
        )

        reasons: List[str] = []

        # Gate 3: Defense-Only Safety Audit
        gate_3_passed = True
        for rule in challenger_rules:
            audit = self.defense_gate.audit(rule)
            if not audit.is_defense_only:
                gate_3_passed = False
                reasons.append(f"Gate 3 safety violation in rule [{rule.id}]: {audit.details}")

        # Baseline comparison
        baseline_savings = (
            self.current_champion.validation_net_savings_inr if self.current_champion else 0.0
        )
        challenger_savings = challenger_eval.cost_metrics.net_financial_savings_inr
        delta_savings = challenger_savings - baseline_savings

        # Gate 1: Regression check (must not catastrophically regress below baseline tolerance buffer)
        gate_1_passed = True
        if self.current_champion:
            if delta_savings < -self.regression_harness.max_cost_drop_tolerance_inr:
                gate_1_passed = False
                reasons.append(
                    f"Gate 1 regression: Challenger net savings (₹{challenger_savings:,.2f}) "
                    f"is ₹{-delta_savings:,.2f} below champion (₹{baseline_savings:,.2f})."
                )

        promoted = False
        new_version = self.version_counter

        if gate_1_passed and gate_3_passed and (challenger_savings >= baseline_savings or not self.current_champion):
            promoted = True
            self.version_counter += 1
            new_version = self.version_counter

            # Snapshot previous champion if exists
            if self.current_champion:
                self.champion_history.append(self.current_champion)

            # Deploy new champion
            challenger_id = f"champ_v{new_version}_{datetime.now(timezone.utc).strftime('%H%M%S')}"
            self.current_champion = ChampionSnapshot(
                version=new_version,
                champion_id=challenger_id,
                rules=challenger_rules,
                validation_net_savings_inr=round(challenger_savings, 2),
                validation_precision=round(challenger_eval.standard_metrics.precision, 4),
                validation_recall=round(challenger_eval.standard_metrics.recall, 4),
                notes=notes,
            )
            reasons.append(f"Promoted to active Champion v{new_version} (+₹{delta_savings:,.2f} vs baseline).")
        else:
            if not gate_1_passed:
                reasons.append("Promotion rejected: Gate 1 regression.")
            if not gate_3_passed:
                reasons.append("Promotion rejected: Gate 3 safety breach.")
            if challenger_savings < baseline_savings:
                reasons.append(f"Promotion rejected: Net savings lower than active champion (₹{challenger_savings:,.2f} < ₹{baseline_savings:,.2f}).")

        decision = PromotionDecision(
            promoted=promoted,
            version=new_version,
            challenger_id=f"challenger_{len(challenger_rules)}_rules",
            gate_1_passed=gate_1_passed,
            gate_3_passed=gate_3_passed,
            baseline_net_savings_inr=round(baseline_savings, 2),
            challenger_net_savings_inr=round(challenger_savings, 2),
            delta_net_savings_inr=round(delta_savings, 2),
            reasons=reasons,
        )
        self.promotion_decisions.append(decision)
        return decision

    def check_and_rollback_on_outcomes(
        self,
        df_realized_outcomes: pd.DataFrame,
        dataset_name: str = "rolling_realized_outcomes",
    ) -> RollbackDecision:
        """Evaluates active champion against rolling realized delivery outcomes.
        
        CRITICAL METHODOLOGICAL GUARANTEE:
        This check operates STRICTLY on the rolling outcome stream (realized delivery logs or validation stream).
        Under NO circumstances does it access or touch held_out_test.csv.
        """
        # Explicit guard against held-out test contamination
        if "held_out" in dataset_name.lower() or "test.csv" in dataset_name.lower():
            raise RuntimeError(
                "[CRITICAL METHODOLOGICAL VIOLATION] Rollback check attempted on held_out_test.csv. "
                "Rollback logic must only evaluate against rolling realized outcomes or validation stream."
            )

        if not self.current_champion or not self.champion_history:
            return RollbackDecision(
                rolled_back=False,
                active_version_before=self.current_champion.version if self.current_champion else 0,
                reason="No previous champion history available for rollback.",
                realized_net_savings_inr=0.0,
            )

        # Evaluate active champion on realized outcome slice
        active_ensemble = EnsembleRule(self.current_champion.rules)
        sanitized = sanitize_features(df_realized_outcomes)
        flags = active_ensemble.predict(sanitized)
        rep = self.evaluator.evaluate_flags(flags, df_realized_outcomes, "rollback_eval", "Rollback Check")

        realized_savings = rep.cost_metrics.net_financial_savings_inr
        active_version = self.current_champion.version

        # Rollback Trigger Condition:
        # If realized net savings turns negative OR precision collapses by > 50% relative to promotion
        precision_collapse = (
            rep.standard_metrics.precision < (self.current_champion.validation_precision * 0.50)
            if rep.standard_metrics.flagged_orders >= 5 else False
        )
        negative_savings = realized_savings < 0.0 and rep.standard_metrics.flagged_orders >= 5

        if negative_savings or precision_collapse:
            previous_champ = self.champion_history.pop()
            restored_version = previous_champ.version
            self.current_champion = previous_champ

            reason = (
                f"Automated Rollback Triggered: Active Champion v{active_version} degraded "
                f"(Realized Net: ₹{realized_savings:,.2f}, Precision: {rep.standard_metrics.precision*100:.1f}%). "
                f"Restored Champion v{restored_version}."
            )
            decision = RollbackDecision(
                rolled_back=True,
                active_version_before=active_version,
                restored_version=restored_version,
                reason=reason,
                realized_net_savings_inr=round(realized_savings, 2),
            )
            self.rollback_decisions.append(decision)
            return decision

        return RollbackDecision(
            rolled_back=False,
            active_version_before=active_version,
            reason="Active champion performance stable on realized outcomes.",
            realized_net_savings_inr=round(realized_savings, 2),
        )