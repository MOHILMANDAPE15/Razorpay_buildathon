"""Unit tests for Static v1 LightGBM Baseline (Sec 4.8), Frozen LLM Rule Ensemble (Sec 4.7),
Cost-Weighted Ensemble Selector, and Rule Pruner."""

import pytest
import numpy as np
import pandas as pd

from app.data.loader import load_train_data, load_validation_data
from app.engine.baseline import StaticV1Baseline, generate_and_save_v1_snapshot, SNAPSHOT_PATH
from app.engine.frozen_rule_snapshot import (
    FrozenRuleEnsemble,
    MOCK_SNAPSHOT_PATH,
    generate_frozen_rule_snapshot,
)
from app.engine.selector import CostWeightedSelector, EnsembleRule, RulePruner
from app.engine.types import RuleHypothesis


def test_v1_baseline_training_and_snapshot_on_actual_data():
    """Verifies that StaticV1Baseline trains on actual train data and produces valid snapshot."""
    df_train = load_train_data()
    df_val = load_validation_data()

    assert len(df_train) == 10807
    assert len(df_val) == 3885

    baseline = StaticV1Baseline()
    baseline.train(df_train)

    probas = baseline.predict_proba(df_val)
    assert len(probas) == len(df_val)
    assert np.all((probas >= 0.0) & (probas <= 1.0))

    val_report = baseline.evaluate(df_val)
    assert val_report.standard_metrics.total_orders == len(df_val)
    assert 0.0 <= val_report.standard_metrics.precision <= 1.0
    assert 0.0 <= val_report.standard_metrics.recall <= 1.0

    # Test snapshot file generation -- regenerates with corrected class_weight
    snapshot = generate_and_save_v1_snapshot()
    assert SNAPSHOT_PATH.exists(), f"LightGBM snapshot not found at {SNAPSHOT_PATH}"
    assert "performance_train_pre_drift" in snapshot
    assert "performance_validation_drift" in snapshot
    # Recall should now be healthy (>= 10%) with class_weight='balanced'
    assert snapshot["performance_train_pre_drift"]["recall"] >= 0.10, (
        f"LightGBM recall on train is suspiciously low: "
        f"{snapshot['performance_train_pre_drift']['recall']:.4f}. "
        "Check class_weight='balanced' was applied."
    )


def test_frozen_rule_ensemble_mock_evaluates_train_and_val():
    """Section 4.7: Verifies frozen rule ensemble (MOCK path) evaluates on both splits.

    This test uses the MOCK snapshot only -- never the live submission artifact.
    It confirms:
      1. MOCK snapshot is generated without API calls.
      2. FrozenRuleEnsemble.evaluate(df_train) produces a valid report.
      3. FrozenRuleEnsemble.evaluate(df_val)   produces a valid report.
      4. Both reports are non-error EvaluationReports.
    """
    # Generate (or regenerate) the MOCK snapshot -- no API calls
    snapshot = generate_frozen_rule_snapshot(live=False)
    assert snapshot["snapshot_type"] == "MOCK_CI_FIXTURE"
    assert MOCK_SNAPSHOT_PATH.exists()

    # Load the MOCK frozen ensemble
    ensemble = FrozenRuleEnsemble(snapshot_path=MOCK_SNAPSHOT_PATH).load()
    assert len(ensemble.rules) >= 1

    df_train = load_train_data()
    df_val = load_validation_data()

    # Evaluate on train (pre-drift)
    train_report = ensemble.evaluate(df_train, split_name="train")
    assert train_report.is_valid, f"Frozen ensemble eval on train failed: {train_report.error_message}"
    assert train_report.standard_metrics.total_orders == len(df_train)

    # Evaluate on validation (post-drift exposure)
    val_report = ensemble.evaluate(df_val, split_name="val")
    assert val_report.is_valid, f"Frozen ensemble eval on val failed: {val_report.error_message}"
    assert val_report.standard_metrics.total_orders == len(df_val)

    # Both should have financial metrics
    assert train_report.cost_metrics is not None
    assert val_report.cost_metrics is not None

    print("\n[Sec 4.7 MOCK] Frozen Ensemble -- Train vs Val:")
    print(f"  Train Net Rs.: {train_report.cost_metrics.net_financial_savings_inr:,.2f}")
    print(f"  Val   Net Rs.: {val_report.cost_metrics.net_financial_savings_inr:,.2f}")

def test_rule_pruner_detects_redundancy_and_negative_value():
    """Verifies that RulePruner removes negative-value rules and duplicate Jaccard overlaps."""
    df_val = load_validation_data()
    pruner = RulePruner(jaccard_threshold=0.80, min_precision=0.20)
    from app.engine.evaluator import CostWeightedEvaluator
    evaluator = CostWeightedEvaluator()

    # Rule 1: High net value (Device reuse >= 3)
    r1 = RuleHypothesis(
        id="hyp_good_1",
        name="Device Abuse >= 3",
        code="def predict(df): return df['device_order_count_24h'] >= 3",
    )

    # Rule 2: Near duplicate of Rule 1 with identical flags (Device reuse > 2)
    r2 = RuleHypothesis(
        id="hyp_duplicate_2",
        name="Device Abuse > 2",
        code="def predict(df): return df['device_order_count_24h'] > 2",
    )

    # Rule 3: Negative net value (Overblocks all COD orders indiscriminately)
    r3 = RuleHypothesis(
        id="hyp_negative_3",
        name="All COD",
        code="def predict(df): return df['payment_mode'] == 'COD'",
    )

    retained, pruned, reasons = pruner.prune_candidates([r1, r2, r3], df_val, evaluator)

    retained_ids = [r.id for r in retained]
    pruned_ids = [r.id for r in pruned]

    assert "hyp_good_1" in retained_ids
    assert "hyp_duplicate_2" in pruned_ids  # Pruned due to high Jaccard overlap
    assert "hyp_negative_3" in pruned_ids   # Pruned due to negative net savings / poor precision


def test_cost_weighted_forward_selector_combines_synergistic_rules():
    """Verifies that forward greedy selector combines complementary rules to maximize net savings."""
    df_val = load_validation_data()
    selector = CostWeightedSelector()

    # Rule A: Flags device abuse
    r_dev = RuleHypothesis(
        id="hyp_device",
        name="Device Abuse Filter",
        code="def predict(df): return df['device_order_count_24h'] >= 3",
    )

    # Rule B: Flags promo stacking on new low-value accounts
    r_promo = RuleHypothesis(
        id="hyp_promo",
        name="Promo Stacking Filter",
        code=(
            "def predict(df):\n"
            "    return (df['promo_code_used'] == True) & "
            "           (df['is_first_time_customer'] == 1) & "
            "           (df['order_value'] < 2000)"
        ),
    )

    # Rule C: Low value negative rule
    r_bad = RuleHypothesis(
        id="hyp_bad",
        name="Bad Heuristic",
        code="def predict(df): return df['order_hour'] == 3",
    )

    candidates = [r_dev, r_promo, r_bad]
    result = selector.select_ensemble(
        candidates=candidates,
        df_eval=df_val,
        max_ensemble_size=3,
        min_marginal_gain_inr=500.0,
    )

    # The ensemble of r_dev + r_promo should produce higher net savings than r_dev alone
    assert result.total_selected >= 2
    assert result.ensemble_net_savings_inr > result.baseline_single_best_net_inr
    assert result.ensemble_precision > 0.40

    # Test compiled EnsembleRule
    ensemble_rule = EnsembleRule(result.selected_rules)
    flags = ensemble_rule.predict(df_val)
    assert len(flags) == len(df_val)
    assert np.sum(flags) > 0

    # Test order explanation
    sample_flagged_order = df_val.iloc[np.where(flags)[0][0]]
    reasons = ensemble_rule.explain_order(sample_flagged_order)
    assert len(reasons) >= 1
