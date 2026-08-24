"""Frozen LLM Rule Ensemble Snapshot for Section 4.7 Thesis Proof.

This module implements TWO distinct and NEVER interchangeable paths:

  MOCK / CI path  (live=False):
    generate_frozen_rule_snapshot(live=False)
    -> Writes: v1_frozen_rules_snapshot.MOCK.json
    -> Uses a hardcoded seed rule. Fast, no API calls.
    -> Referenced ONLY in pytest fixtures, never in submission results.

  Live / Submission path  (live=True):
    generate_frozen_rule_snapshot(live=True, n_rounds=N)
    -> Writes: v1_frozen_rules_snapshot.json
    -> Runs Generator -> Evaluator -> Reflector -> Selector on orders_train (pre-drift).
    -> This is the actual "frozen v1 rule ensemble" for Section 4.7 comparison.
    -> Run intentionally once when ready. Budget N rounds of Gemini API calls.

Section 4.7 Comparison (the thesis proof):
    FrozenRuleEnsemble.evaluate(df_train) -> strong performance (pre-drift, trained on this)
    FrozenRuleEnsemble.evaluate(df_val)   -> degraded performance (drift exposure proof)
    EvolvedEnsemble.evaluate(df_val)      -> recovered performance (self-evolution payoff)
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.core.config import cost_config
from app.data.loader import load_train_data
from app.data.schema import sanitize_features
from app.engine.evaluator import CostWeightedEvaluator
from app.engine.types import EvaluationReport, RuleHypothesis


# ---------------------------------------------------------------------------
# Snapshot file paths -- NEVER swap these two
# ---------------------------------------------------------------------------
_ENGINE_DIR = Path(__file__).resolve().parent

MOCK_SNAPSHOT_PATH = _ENGINE_DIR / "v1_frozen_rules_snapshot.MOCK.json"
LIVE_SNAPSHOT_PATH = _ENGINE_DIR / "v1_frozen_rules_snapshot.json"

# A known good, manually-verified seed rule used only by the MOCK/CI path.
# This is a test fixture, NOT a research artifact.
_MOCK_SEED_RULE = {
    "id": "mock_r1_seed_0001",
    "name": "Mock Seed: COD High-Value First-Timer Rule",
    "code": (
        "def predict(df):\n"
        "    return (\n"
        "        (df['payment_mode'] == 'COD') &\n"
        "        (df['order_value'] > 1500) &\n"
        "        (df['is_first_time_customer'] == True)\n"
        "    ).values\n"
    ),
    "description": "Test fixture seed rule. MOCK only -- not a research artifact.",
    "rationale": "COD first-time customers ordering high value are high RTO risk.",
    "target_signal": "cod_high_value",
    "generation_round": 0,
    "parent_ids": [],
    "status": "champion",
}


# ---------------------------------------------------------------------------
# FrozenRuleEnsemble: replays pre-drift rules frozen (never re-evolves)
# ---------------------------------------------------------------------------
class FrozenRuleEnsemble:
    """Loads a frozen pre-drift rule snapshot and evaluates it on any DataFrame.

    IMPORTANT: This class NEVER re-evolves or modifies rules.
    It is a read-only replay of rules frozen before drift was observed.

    Usage:
        # For CI tests:
        ensemble = FrozenRuleEnsemble(snapshot_path=MOCK_SNAPSHOT_PATH).load()
        # For submission:
        ensemble = FrozenRuleEnsemble().load()  # uses LIVE_SNAPSHOT_PATH
    """

    def __init__(self, snapshot_path: Optional[Path] = None):
        self.snapshot_path = snapshot_path or LIVE_SNAPSHOT_PATH
        self.snapshot: Optional[Dict[str, Any]] = None
        self.rules: List[RuleHypothesis] = []
        self.evaluator = CostWeightedEvaluator()
        self._loaded = False

    def load(self) -> "FrozenRuleEnsemble":
        """Loads the frozen snapshot from disk."""
        if not self.snapshot_path.exists():
            raise FileNotFoundError(
                f"Frozen rule snapshot not found at: {self.snapshot_path}\n"
                f"Run generate_frozen_rule_snapshot(live=False) for MOCK or "
                f"generate_frozen_rule_snapshot(live=True) for submission artifact."
            )
        with open(self.snapshot_path, "r", encoding="utf-8") as f:
            self.snapshot = json.load(f)

        self.rules = [
            RuleHypothesis(**rule_data)
            for rule_data in self.snapshot.get("selected_rules", [])
        ]
        self._loaded = True
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Returns boolean OR union of all frozen rules' flags on input DataFrame."""
        if not self._loaded:
            self.load()
        if not self.rules:
            return np.zeros(len(df), dtype=bool)

        from app.core.sandbox import execute_rule_sandboxed

        combined = np.zeros(len(df), dtype=bool)
        sanitized = sanitize_features(df)
        for rule in self.rules:
            try:
                flags = execute_rule_sandboxed(rule.code, sanitized)
                combined = combined | flags.astype(bool)
            except Exception as e:
                print(f"[FrozenRuleEnsemble] Warning: rule [{rule.id}] failed: {e}")
        return combined

    def evaluate(self, df: pd.DataFrame, split_name: str = "unknown") -> EvaluationReport:
        """Evaluates the frozen ensemble on any DataFrame WITHOUT re-evolving.

        Section 4.7 usage:
            .evaluate(df_train, 'train')  -> strong pre-drift performance
            .evaluate(df_val,   'val')    -> degraded post-drift performance (thesis proof)
        """
        if not self._loaded:
            self.load()
        flags = self.predict(df)
        return self.evaluator.evaluate_flags(
            flags=flags,
            df=df,
            hypothesis_id=f"frozen_v1_ensemble_{split_name}",
            hypothesis_name=f"Frozen v1 Rule Ensemble [Section 4.7] ({split_name})",
        )


# ---------------------------------------------------------------------------
# Snapshot Generation
# ---------------------------------------------------------------------------
def generate_frozen_rule_snapshot(
    live: bool = False,
    n_rounds: int = 2,
    hypotheses_per_round: int = 2,
) -> Dict[str, Any]:
    """Generates the frozen pre-drift LLM rule ensemble snapshot.

    Args:
        live: If False -> MOCK/CI path (hardcoded seed, writes .MOCK.json, no API calls).
              If True  -> submission path (real Generator+Selector on orders_train).
        n_rounds: Evolution rounds (live=True only).
        hypotheses_per_round: Candidates per round (live=True only).

    Returns:
        Snapshot dict written to disk.

    Output files:
        live=False -> v1_frozen_rules_snapshot.MOCK.json  (test fixture only)
        live=True  -> v1_frozen_rules_snapshot.json        (submission artifact)
    """
    if not live:
        return _generate_mock_snapshot()
    return _generate_live_snapshot(n_rounds=n_rounds, hypotheses_per_round=hypotheses_per_round)


def _generate_mock_snapshot() -> Dict[str, Any]:
    """MOCK/CI path: hardcoded seed rule, no API calls.

    Output: v1_frozen_rules_snapshot.MOCK.json
    NEVER reference this file in submission results or video.
    """
    print("[FrozenSnapshot MOCK] Generating mock snapshot (no API calls)...")
    df_train = load_train_data()
    evaluator = CostWeightedEvaluator()
    seed_rule = RuleHypothesis(**_MOCK_SEED_RULE)

    from app.core.sandbox import execute_rule_sandboxed

    sanitized = sanitize_features(df_train)
    try:
        flags = execute_rule_sandboxed(seed_rule.code, sanitized)
        report = evaluator.evaluate_flags(flags, df_train, seed_rule.id, seed_rule.name)
    except Exception as e:
        raise RuntimeError(f"Mock seed rule failed execution on orders_train: {e}")

    snapshot: Dict[str, Any] = {
        "snapshot_type": "MOCK_CI_FIXTURE",
        "warning": (
            "TEST FIXTURE ONLY. Not a research artifact. "
            "Do NOT reference in results, reports, or video."
        ),
        "section": "4.7 Frozen Rule Ensemble",
        "training_data": "orders_train (10,807 orders, Days 0-55)",
        "generation_mode": "mock_seed",
        "n_rounds": 0,
        "selected_rules": [_MOCK_SEED_RULE],
        "performance_train_pre_drift": {
            "total_orders": report.standard_metrics.total_orders,
            "precision": report.standard_metrics.precision,
            "recall": report.standard_metrics.recall,
            "f1_score": report.standard_metrics.f1,
            "net_financial_savings_inr": report.cost_metrics.net_financial_savings_inr,
        },
    }

    with open(MOCK_SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
    print(f"[FrozenSnapshot MOCK] Saved to {MOCK_SNAPSHOT_PATH}")
    print(
        f"  -> Train Net Savings: Rs. {report.cost_metrics.net_financial_savings_inr:,.2f} "
        f"(Precision: {report.standard_metrics.precision*100:.1f}%, "
        f"Recall: {report.standard_metrics.recall*100:.1f}%)"
    )
    return snapshot


def _generate_live_snapshot(n_rounds: int, hypotheses_per_round: int) -> Dict[str, Any]:
    """Live/Submission path: Generator -> Reflector -> Selector on orders_train only.

    Output: v1_frozen_rules_snapshot.json
    This IS the real Section 4.7 frozen v1 ensemble. Reference in results and video.
    API budget: ~n_rounds * hypotheses_per_round * 2 Gemini calls.
    """
    print(
        f"[FrozenSnapshot LIVE] Starting {n_rounds}-round evolution on "
        f"orders_train ONLY (no validation data touched)..."
    )
    api_estimate = n_rounds * hypotheses_per_round * 2
    print(f"  API budget: ~{api_estimate} Gemini calls.")

    df_train = load_train_data()
    df_sample = sanitize_features(df_train.head(20))

    from app.agents.generator import HypothesisGenerator
    from app.agents.reflector import HypothesisReflector
    from app.engine.notepad import Notepad
    from app.engine.selector import CostWeightedSelector

    generator = HypothesisGenerator()
    reflector = HypothesisReflector()
    evaluator = CostWeightedEvaluator()
    notepad = Notepad()
    selector = CostWeightedSelector(evaluator=evaluator)

    for r in range(1, n_rounds + 1):
        print(f"\n[FrozenSnapshot LIVE] === Round {r}/{n_rounds} ===")
        history = notepad.get_history_summary_for_generator()
        candidates = generator.generate_hypotheses(
            n_hypotheses=hypotheses_per_round,
            notepad_summary=history,
            generation_round=r,
            df_sample=df_sample,
        )
        print(f"  Generator produced {len(candidates)} candidates.")

        for cand in candidates:
            notepad.add_hypothesis(cand)
            report = evaluator.evaluate_hypothesis(cand, df_train)
            notepad.record_evaluation(report)

            if report.is_valid and report.cost_metrics and report.standard_metrics:
                sm = report.standard_metrics
                cm = report.cost_metrics
                print(
                    f"  [{cand.id}] Precision: {sm.precision*100:.1f}% | "
                    f"Recall: {sm.recall*100:.1f}% | Net: Rs. {cm.net_financial_savings_inr:,.2f}"
                )
                mutated = reflector.reflect_and_mutate(
                    cand, report, generation_round=r, df_sample=df_sample
                )
                if mutated:
                    notepad.add_hypothesis(mutated)
                    mut_report = evaluator.evaluate_hypothesis(mutated, df_train)
                    notepad.record_evaluation(mut_report)
                    if mut_report.is_valid and mut_report.cost_metrics:
                        print(
                            f"  Mutated [{mutated.id}] Net: "
                            f"Rs. {mut_report.cost_metrics.net_financial_savings_inr:,.2f}"
                        )

    # Select optimal ensemble from train performance
    all_candidates = notepad.get_all_hypotheses()
    print(f"\n[FrozenSnapshot LIVE] Selecting ensemble from {len(all_candidates)} candidates...")
    result = selector.select_ensemble(all_candidates, df_train, max_ensemble_size=4)

    if not result.selected_rules:
        raise RuntimeError(
            "No viable rules survived pruning during live snapshot generation. "
            "Try increasing n_rounds or hypotheses_per_round."
        )

    # Evaluate the final frozen ensemble on train to record its pre-drift baseline
    from app.core.sandbox import execute_rule_sandboxed

    sanitized_train = sanitize_features(df_train)
    final_flags = np.zeros(len(df_train), dtype=bool)
    for rule in result.selected_rules:
        flags = execute_rule_sandboxed(rule.code, sanitized_train)
        final_flags = final_flags | flags.astype(bool)

    final_report = evaluator.evaluate_flags(
        final_flags, df_train, "frozen_v1_train", "Frozen v1 Rule Ensemble [Section 4.7] (train)"
    )

    snapshot: Dict[str, Any] = {
        "snapshot_type": "LIVE_SUBMISSION_ARTIFACT",
        "warning": (
            "This is the real Section 4.7 frozen v1 ensemble. "
            "Reference in results, reports, and video."
        ),
        "section": "4.7 Frozen Rule Ensemble",
        "training_data": "orders_train (10,807 orders, Days 0-55) -- pre-drift only",
        "generation_mode": "live_llm",
        "n_rounds": n_rounds,
        "hypotheses_evaluated": len(notepad.registry),
        "selected_rules": [r.model_dump() for r in result.selected_rules],
        "ensemble_size": result.total_selected,
        "pruned_count": result.total_pruned,
        "performance_train_pre_drift": {
            "total_orders": final_report.standard_metrics.total_orders,
            "precision": final_report.standard_metrics.precision,
            "recall": final_report.standard_metrics.recall,
            "f1_score": final_report.standard_metrics.f1,
            "net_financial_savings_inr": final_report.cost_metrics.net_financial_savings_inr,
        },
    }

    with open(LIVE_SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    print(f"\n[FrozenSnapshot LIVE] Saved to {LIVE_SNAPSHOT_PATH}")
    print(f"  -> Ensemble: {result.total_selected} rules selected, {result.total_pruned} pruned")
    print(f"  -> Train Precision: {final_report.standard_metrics.precision*100:.1f}%")
    print(f"  -> Train Recall:    {final_report.standard_metrics.recall*100:.1f}%")
    print(f"  -> Train Net Rs:    {final_report.cost_metrics.net_financial_savings_inr:,.2f}")
    return snapshot


if __name__ == "__main__":
    import sys

    live = "--live" in sys.argv
    n = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--rounds=")), "2"))
    print("=" * 60)
    print(f"Frozen Rule Snapshot Generator [live={live}, rounds={n}]")
    print("=" * 60)
    generate_frozen_rule_snapshot(live=live, n_rounds=n)
