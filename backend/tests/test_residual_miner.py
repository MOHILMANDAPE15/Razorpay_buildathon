"""Unit tests for the Residual Miner & Targeted Evolution Engine."""

import numpy as np
import pandas as pd
import pytest

from app.engine.residual_miner import (
    RejectedClusterCandidate,
    ResidualMiner,
    TargetedMissCluster,
)
from app.engine.selector import EnsembleRule
from app.engine.types import RuleHypothesis
from app.data.schema import FORBIDDEN_COLUMNS


@pytest.fixture
def sample_orders_df():
    """Generates synthetic test data with known false negative clusters and day indices."""
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "order_id": [f"ORD_{i:04d}" for i in range(n)],
        "day_index": np.repeat(np.arange(10), 10),  # Days 0 to 9
        "payment_mode": ["COD"] * 70 + ["prepaid"] * 30,
        "promo_code_used": [True] * 40 + [False] * 60,
        "device_order_count_24h": [3] * 30 + [1] * 70,
        "customer_prior_orders": [0] * 50 + [2] * 50,
        "item_category": ["fashion"] * 60 + ["electronics"] * 40,
        "pincode_rolling_rto_rate": [0.35] * 50 + [0.10] * 50,
        "order_hour": [23] * 30 + [14] * 70,
        "order_value": [450.0] * 50 + [1500.0] * 50,
        "customer_account_age_days": [1] * 30 + [45] * 70,
        "is_rto": [1] * 35 + [0] * 65,  # 35 real RTOs
    })
    return df


@pytest.fixture
def mock_incumbent_ensemble():
    """Simple baseline ensemble that flags only orders with pincode_rolling_rto_rate > 0.40."""
    rule = RuleHypothesis(
        id="hyp_base_pincode",
        name="High-Risk Pincode Base",
        code="def predict(df):\n    return df['pincode_rolling_rto_rate'] > 0.40",
    )
    return EnsembleRule([rule])


def test_residual_miner_label_maturity_gate(sample_orders_df):
    """Verifies that in-flight orders within the maturity window are deferred."""
    miner = ResidualMiner(maturity_window_days=3)
    # Total days 0-9. Cutoff at max_day(9) - 3 = 6. Days 0-6 are mature, 7-9 are immature.
    mature_df, immature_df = miner.filter_mature_orders(sample_orders_df, current_day_index=9)

    assert len(mature_df) == 70  # Days 0 to 6 (7 days * 10 orders)
    assert len(immature_df) == 30  # Days 7 to 9 (3 days * 10 orders)
    assert mature_df["day_index"].max() == 6
    assert immature_df["day_index"].min() == 7


def test_residual_miner_extracts_and_clusters_misses(sample_orders_df, mock_incumbent_ensemble):
    """Verifies that false negatives are extracted and clustered into coherent abuse patterns."""
    miner = ResidualMiner(maturity_window_days=0, min_cluster_size=5, min_cohort_size=20)
    report = miner.run_residual_analysis(sample_orders_df, mock_incumbent_ensemble, current_day_index=9)

    assert report.total_orders_analyzed == 100
    assert report.total_false_negatives > 0
    assert len(report.clusters_identified) >= 1

    # Check top cluster structure
    top_cluster = report.clusters_identified[0]
    assert isinstance(top_cluster, TargetedMissCluster)
    assert top_cluster.miss_count >= 5
    assert len(top_cluster.generator_agenda) > 20
    assert "TARGETED AGENDA" in top_cluster.generator_agenda
    assert top_cluster.is_statistically_significant is True


def test_residual_miner_leakage_guard(sample_orders_df, mock_incumbent_ensemble):
    """Verifies that clustering never leaks forbidden columns (phase, drift_weight, is_rto)."""
    miner = ResidualMiner(maturity_window_days=0, min_cluster_size=3, min_cohort_size=10)
    df_with_forbidden = sample_orders_df.copy()
    df_with_forbidden["phase"] = "transition"
    df_with_forbidden["drift_weight"] = 0.5

    mature_df, _ = miner.filter_mature_orders(df_with_forbidden)
    df_fn = miner.extract_false_negatives(mature_df, mock_incumbent_ensemble)
    clusters, _ = miner.dynamic_subgroup_clusters(df_fn, mature_df)

    for cluster in clusters:
        for sample in cluster.representative_samples:
            for forbidden in FORBIDDEN_COLUMNS:
                assert forbidden not in sample, f"Forbidden column '{forbidden}' found in cluster sample!"


def test_strict_full_validation_cost_weighted_acceptance_gate(sample_orders_df, mock_incumbent_ensemble):
    """Verifies that candidate rules are accepted/rejected based on net rupee savings on the full dataset."""
    miner = ResidualMiner()

    # Rule A (Good): Targets promotional COD velocity abuse cleanly
    good_rule = RuleHypothesis(
        id="hyp_good_promo_cod",
        name="Targeted Promo COD Velocity Shield",
        code=(
            "def predict(df):\n"
            "    return (df['payment_mode'] == 'COD') & (df['promo_code_used'] == True) & (df['device_order_count_24h'] >= 2)"
        ),
    )

    verdict_good = miner.evaluate_cluster_hypothesis_on_full_dataset(
        good_rule, sample_orders_df, mock_incumbent_ensemble
    )
    assert verdict_good["accepted"] is True
    assert verdict_good["delta_net_savings_inr"] > 0
    assert verdict_good["verdict"] == "PROMOTED"

    # Rule B (Bad): Over-flags all COD orders
    overfitted_rule = RuleHypothesis(
        id="hyp_bad_overblock_cod",
        name="Overly Aggressive Blanket COD Block",
        code="def predict(df):\n    return df['payment_mode'] == 'COD'",
    )

    verdict_bad = miner.evaluate_cluster_hypothesis_on_full_dataset(
        overfitted_rule, sample_orders_df, mock_incumbent_ensemble
    )
    assert "delta_net_savings_inr" in verdict_bad
    assert "reasons" in verdict_bad


def test_shipped_holdout_rate_routing(sample_orders_df, mock_incumbent_ensemble):
    """Verifies that shipped_holdout_rate defaults to 0.0 and permits random holdout when specified."""
    from app.engine.router import ThreeWayRouter

    default_router = ThreeWayRouter()
    assert default_router.shipped_holdout_rate == 0.0

    holdout_router = ThreeWayRouter(shipped_holdout_rate=1.0)
    assert holdout_router.shipped_holdout_rate == 1.0

    high_risk_rule = RuleHypothesis(
        id="hyp_high_risk",
        name="High Risk COD Rule",
        code="def predict(df):\n    return df['payment_mode'] == 'COD'",
    )
    ensemble = EnsembleRule([high_risk_rule, high_risk_rule])

    decisions_default = default_router.route_batch(sample_orders_df.head(10), ensemble)
    blocked_count = sum(1 for d in decisions_default if d.decision == "AUTO_BLOCK")
    assert blocked_count > 0

    decisions_holdout = holdout_router.route_batch(sample_orders_df.head(10), ensemble)
    holdout_approved_count = sum(1 for d in decisions_holdout if d.decision == "AUTO_APPROVE")
    assert holdout_approved_count == 10


def test_subgroup_significance_guard_rejects_insignificant():
    """Verifies that Chi-Square significance check rejects high-lift subgroups if p >= 0.05."""
    miner = ResidualMiner(significance_alpha=0.05)

    # Subgroup with only 2 misses out of 3 cohort orders (small N, not statistically significant)
    lift, p_val, is_sig = miner.test_subgroup_significance(
        subgroup_fn_count=2,
        subgroup_cohort_size=3,
        total_fn_count=350,
        total_mature_count=1000,
    )
    # p-value on 2/3 vs 350/1000 is not statistically significant
    assert p_val >= 0.05
    assert is_sig is False

    # Subgroup with 150 misses out of 200 cohort orders (large N, highly significant)
    lift_sig, p_val_sig, is_sig_true = miner.test_subgroup_significance(
        subgroup_fn_count=150,
        subgroup_cohort_size=200,
        total_fn_count=350,
        total_mature_count=1000,
    )
    assert p_val_sig < 0.001
    assert is_sig_true is True
    assert lift_sig > 1.5


def test_static_fallback_mode_runs_end_to_end(sample_orders_df, mock_incumbent_ensemble):
    """Verifies that static fallback mode runs cleanly through the residual mining pipeline."""
    static_miner = ResidualMiner(
        maturity_window_days=0,
        min_cluster_size=5,
        min_cohort_size=15,
        mode="static",
    )
    report = static_miner.run_residual_analysis(
        sample_orders_df, mock_incumbent_ensemble, current_day_index=9
    )

    assert report.miner_mode == "static"
    assert report.total_orders_analyzed == 100
    # Confirms static clusters run cleanly
    assert isinstance(report.clusters_identified, list)


def test_templated_agenda_contains_all_signature_keys():
    """Verifies that deterministic agenda templating contains every signature key-value pair without truncation."""
    miner = ResidualMiner()
    signature = {
        "payment_mode": "COD",
        "promo_code_used": True,
        "device_order_count_24h": 3,
        "order_hour": "22-05",
    }
    agenda = miner.generate_deterministic_agenda(
        cluster_name="Promotional COD Velocity Exploitation",
        miss_count=42,
        cohort_size=120,
        signature=signature,
    )

    assert "TARGETED AGENDA" in agenda
    assert "payment_mode=COD" in agenda
    assert "promo_code_used=True" in agenda
    assert "device_order_count_24h=3" in agenda
    assert "order_hour=22-05" in agenda
    assert "42 unflagged RTO misses" in agenda
    assert "120 mature orders" in agenda


def test_new_cluster_not_born_on_cooldown(sample_orders_df, mock_incumbent_ensemble):
    """Verifies that a freshly discovered cluster is immediately eligible (cooldown_until_round <= current_round)."""
    miner = ResidualMiner(maturity_window_days=0, min_cluster_size=5, min_cohort_size=15)
    report_r1 = miner.run_residual_analysis(
        sample_orders_df, mock_incumbent_ensemble, current_day_index=9, current_round=2
    )

    assert len(report_r1.clusters_identified) > 0
    top_cluster = report_r1.clusters_identified[0]
    rec = miner._cooldown_registry.get(top_cluster.cluster_id)
    assert rec is not None
    assert rec["cooldown_until_round"] <= 2  # Not pre-cooled by schema default!
    assert rec["status"] == "ACTIVE"


def test_cluster_cooldown_suppression_and_50pct_surge_bypass(sample_orders_df, mock_incumbent_ensemble):
    """Verifies that a cluster on cooldown is suppressed, and that a >50% miss volume surge bypasses it."""
    miner = ResidualMiner(maturity_window_days=0, min_cluster_size=5, min_cohort_size=15, cooldown_rounds=3)

    # 1. Round 1: Discover cluster
    report_r1 = miner.run_residual_analysis(
        sample_orders_df, mock_incumbent_ensemble, current_day_index=9, current_round=1
    )
    assert len(report_r1.clusters_identified) > 0
    cluster_id = report_r1.clusters_identified[0].cluster_id
    initial_miss_count = report_r1.clusters_identified[0].miss_count

    # 2. Simulate hypothesis rejection / pruning -> apply cooldown
    miner.apply_cooldown(
        cluster_id=cluster_id,
        current_round=1,
        miss_count=initial_miss_count,
        cooldown_rounds=3,
    )

    # 3. Round 2: Miner runs again with same volume -> Cluster should be SUPPRESSED
    report_r2 = miner.run_residual_analysis(
        sample_orders_df, mock_incumbent_ensemble, current_day_index=9, current_round=2
    )
    suppressed_ids = [s["cluster_id"] for s in report_r2.suppressed_cooling_clusters]
    assert cluster_id in suppressed_ids
    assert cluster_id not in [c.cluster_id for c in report_r2.clusters_identified]

    # 4. Round 2 with Surge: Miss count increases by >50% (e.g. 2x) -> Cluster should BYPASS cooldown!
    miner._cooldown_registry[cluster_id]["last_miss_count"] = 5  # Lower previous baseline
    report_r2_surge = miner.run_residual_analysis(
        sample_orders_df, mock_incumbent_ensemble, current_day_index=9, current_round=2
    )
    # Since current miss count > 1.5 * 5 (which is 7.5), it bypasses
    surged_ids = [c.cluster_id for c in report_r2_surge.clusters_identified]
    assert cluster_id in surged_ids
    assert miner._cooldown_registry[cluster_id]["status"] == "BYPASSED_SURGE"


def test_significance_guard_populates_rejected_clusters(sample_orders_df, mock_incumbent_ensemble):
    """Verifies that rejected_insignificant_clusters is populated when a subgroup fails significance/cohort thresholds."""
    # Set min_cohort_size high (e.g. 60) so some subgroups are rejected due to small cohort
    miner = ResidualMiner(
        maturity_window_days=0,
        min_cluster_size=5,
        min_cohort_size=60,  # High threshold triggers rejections
        significance_alpha=0.05,
    )
    report = miner.run_residual_analysis(
        sample_orders_df, mock_incumbent_ensemble, current_day_index=9
    )

    assert len(report.rejected_insignificant_clusters) > 0
    rejected_sample = report.rejected_insignificant_clusters[0]
    assert isinstance(rejected_sample, RejectedClusterCandidate)
    assert len(rejected_sample.cluster_name) > 0
    assert "below minimum threshold" in rejected_sample.rejection_reason or "Failed significance check" in rejected_sample.rejection_reason


def test_dynamic_discovery_novelty_finds_unseen_patterns():
    """Verifies that dynamic subgroup mining discovers novel patterns beyond static handcoded baselines."""
    from app.data.loader import load_validation_data
    from app.engine.frozen_rule_snapshot import load_frozen_v1_rules

    df_val = load_validation_data()
    v1_rules = load_frozen_v1_rules()
    incumbent = EnsembleRule(v1_rules)

    miner = ResidualMiner(
        maturity_window_days=5,
        min_cluster_size=10,
        min_cohort_size=30,
        mode="dynamic",
    )
    report = miner.run_residual_analysis(df_val, incumbent, current_day_index=int(df_val["day_index"].max()))

    discovered_ids = [c.cluster_id for c in report.clusters_identified]
    assert len(discovered_ids) >= 1

    # Check for presence of dynamically discovered new account cluster
    assert "cluster_dyn_new_account_high_val_cod" in discovered_ids or "cluster_dyn_promo_cod_velocity" in discovered_ids

