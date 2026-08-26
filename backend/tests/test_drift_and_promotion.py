"""Unit tests for Realized Outcome Drift Detector and Champion Promotion/Rollback Engine."""

import numpy as np
import pandas as pd
import pytest

from app.engine.drift_detector import OutcomeDriftDetector
from app.engine.promotion import PromotionManager
from app.engine.types import RuleHypothesis


@pytest.fixture
def sample_validation_df():
    """Generates synthetic validation data for promotion testing."""
    np.random.seed(42)
    n = 200
    return pd.DataFrame({
        "order_id": [f"ORD_{i:04d}" for i in range(n)],
        "customer_id": [f"CUST_{i%50:04d}" for i in range(n)],
        "order_value": np.random.uniform(500.0, 3000.0, size=n),
        "payment_mode": np.random.choice(["COD", "Prepaid"], size=n, p=[0.7, 0.3]),
        "is_first_time_customer": np.random.choice([True, False], size=n, p=[0.6, 0.4]),
        "customer_account_age_days": np.random.randint(1, 100, size=n),
        "customer_prior_orders": np.random.choice([0, 1, 2, 5], size=n, p=[0.5, 0.2, 0.2, 0.1]),
        "pincode": ["110001"] * n,
        "pincode_rolling_rto_rate": np.random.uniform(0.1, 0.5, size=n),
        "promo_code_used": np.random.choice([True, False], size=n, p=[0.4, 0.6]),
        "device_id": [f"DEV_{i%40:04d}" for i in range(n)],
        "device_order_count_24h": np.random.choice([1, 2, 4], size=n, p=[0.7, 0.2, 0.1]),
        "order_hour": np.random.randint(0, 24, size=n),
        "item_category": np.random.choice(["fashion", "electronics", "grocery"], size=n),
        "is_rto": np.random.choice([1, 0], size=n, p=[0.25, 0.75]),
    })


# ---------------------------------------------------------------------------
# OutcomeDriftDetector Tests (Sep 2)
# ---------------------------------------------------------------------------

def test_outcome_drift_detector_normal_stream():
    """Verifies that normal stream within expected precision and RTO rate does not trigger drift."""
    detector = OutcomeDriftDetector(window_size=30, baseline_precision=0.30, baseline_rto_rate=0.20)

    # 30 orders with ~30% precision and ~20% RTO rate
    for i in range(30):
        is_rto = 1 if i % 5 == 0 else 0  # 20% RTO
        pred_flag = True if i % 5 == 0 or i % 7 == 0 else False
        sig = detector.record_outcome(
            order_id=f"ord_{i}",
            predicted_flag=pred_flag,
            ground_truth_is_rto=is_rto,
            order_value=800.0,
        )

    assert sig.drift_detected is False
    assert sig.severity == "NORMAL"


def test_outcome_drift_detector_precision_collapse():
    """Verifies that severe drop in realized precision triggers PRECISION_COLLAPSE drift."""
    detector = OutcomeDriftDetector(window_size=30, baseline_precision=0.40, min_precision_ratio=0.50)

    # Inject 25 false positive misclassifications (predicted flag=True, but genuine delivery=0)
    for i in range(25):
        sig = detector.record_outcome(
            order_id=f"fp_{i}",
            predicted_flag=True,
            ground_truth_is_rto=0,  # 0% precision
            order_value=1200.0,
        )

    assert sig.drift_detected is True
    assert sig.trigger_type in ["PRECISION_COLLAPSE", "FINANCIAL_DEGRADATION"]
    assert sig.severity == "CRITICAL"


def test_outcome_drift_detector_rto_surge():
    """Verifies that high surge in realized RTO rate triggers RTO_RATE_SURGE drift."""
    detector = OutcomeDriftDetector(window_size=30, baseline_rto_rate=0.15, max_rto_surge_sigma=1.5)

    # Inject 25 high RTO orders (actual RTO = 1)
    for i in range(25):
        sig = detector.record_outcome(
            order_id=f"rto_{i}",
            predicted_flag=False,
            ground_truth_is_rto=1,  # 100% RTO
            order_value=900.0,
        )

    assert sig.drift_detected is True
    assert sig.trigger_type == "RTO_RATE_SURGE"
    assert sig.severity == "CRITICAL"


# ---------------------------------------------------------------------------
# PromotionManager & Rollback Tests (Sep 3)
# ---------------------------------------------------------------------------

def test_promotion_manager_champion_challenger_lifecycle(sample_validation_df):
    """Verifies the complete Champion promotion, challenger regression rejection, and rollback lifecycle."""
    mgr = PromotionManager()

    # 1. Initial Champion Candidate
    rule_v1 = RuleHypothesis(
        id="hyp_v1_seed",
        name="Seed COD High Pincode Rule",
        code="def predict(df):\n    return (df['payment_mode'] == 'COD') & (df['pincode_rolling_rto_rate'] >= 0.35)",
        rationale="Detects high risk COD deliveries in volatile pincodes.",
    )
    dec1 = mgr.evaluate_and_promote([rule_v1], sample_validation_df, "Initial v1 promotion")
    assert dec1.promoted is True
    assert dec1.version == 1
    assert mgr.current_champion.version == 1

    # 2. Superior Challenger Candidate (Promoted to v2)
    rule_v2 = RuleHypothesis(
        id="hyp_v2_improved",
        name="Improved Causal COD Defense",
        code=(
            "def predict(df):\n"
            "    return (df['payment_mode'] == 'COD') & (df['pincode_rolling_rto_rate'] >= 0.30) & (df['order_value'] <= 1500)"
        ),
        rationale="Refined order value cap to minimize false positive insult cost.",
    )
    dec2 = mgr.evaluate_and_promote([rule_v2], sample_validation_df, "Promoted improved rule")
    assert dec2.promoted is True
    assert dec2.version == 2
    assert mgr.current_champion.version == 2
    assert len(mgr.champion_history) == 1
    assert mgr.champion_history[0].version == 1

    # 3. Regressed Candidate (Over-blocking high order values -> Rejected by Gate 1)
    bad_rule = RuleHypothesis(
        id="hyp_bad_regression",
        name="Bad Overblocking Rule",
        code="def predict(df):\n    return (df['order_value'] >= 500)",  # Flags almost everything -> massive FP loss
        rationale="Overly aggressive blanket rule.",
    )
    dec3 = mgr.evaluate_and_promote([bad_rule], sample_validation_df, "Testing regression reject")
    assert dec3.promoted is False
    assert mgr.current_champion.version == 2  # Unchanged

    # 4. Malicious / Non-compliant Candidate (Rejected by Gate 3 Defense Audit)
    evasion_rule = RuleHypothesis(
        id="hyp_evasion_advise",
        name="Evasion Advise Rule",
        code="def predict(df):\n    return df['payment_mode'] == 'COD'",
        rationale="Bypass fraud filters by splitting cart checkout into micro transactions.",
    )
    dec4 = mgr.evaluate_and_promote([evasion_rule], sample_validation_df, "Testing safety gate")
    assert dec4.promoted is False
    assert dec4.gate_3_passed is False


def test_promotion_manager_automated_rollback():
    """Verifies that active champion rollback restores the previous champion snapshot."""
    mgr = PromotionManager()

    # Stable v1 Champion
    r1 = RuleHypothesis(
        id="r1_stable",
        name="Stable Rule",
        code="def predict(df):\n    return (df['payment_mode'] == 'COD') & (df['order_value'] <= 800)",
        rationale="Defense against micro-order COD fraud.",
    )
    df_val = pd.DataFrame({
        "order_id": ["O1", "O2", "O3", "O4", "O5"],
        "payment_mode": ["COD", "COD", "Prepaid", "COD", "COD"],
        "order_value": [500.0, 600.0, 1000.0, 700.0, 750.0],
        "pincode_rolling_rto_rate": [0.3, 0.4, 0.1, 0.35, 0.28],
        "is_rto": [1, 1, 0, 1, 1],
    })
    mgr.evaluate_and_promote([r1], df_val)
    assert mgr.current_champion.version == 1

    # Promoted v2 Challenger
    r2 = RuleHypothesis(
        id="r2_aggressive",
        name="Aggressive Rule",
        code="def predict(df):\n    return df['payment_mode'] == 'COD'",
        rationale="Aggressive COD flag.",
    )
    mgr.evaluate_and_promote([r2], df_val)
    assert mgr.current_champion.version == 2
    assert len(mgr.champion_history) == 1

    # Simulated degraded rolling outcomes (High false positives on genuine customers)
    df_degraded_outcomes = pd.DataFrame({
        "order_id": [f"ORD_DEG_{i}" for i in range(10)],
        "payment_mode": ["COD"] * 10,
        "order_value": [2500.0] * 10,  # High insult cost
        "pincode_rolling_rto_rate": [0.10] * 10,
        "is_rto": [0] * 10,  # 100% false positives
    })

    rollback_dec = mgr.check_and_rollback_on_outcomes(df_degraded_outcomes, dataset_name="rolling_realized_outcomes")
    assert rollback_dec.rolled_back is True
    assert rollback_dec.active_version_before == 2
    assert rollback_dec.restored_version == 1
    assert mgr.current_champion.version == 1


def test_promotion_manager_single_touch_isolation_guard():
    """Verifies that rollback check explicitly blocks held_out_test.csv access."""
    mgr = PromotionManager()
    dummy_df = pd.DataFrame({"order_id": ["O1"], "is_rto": [1]})

    with pytest.raises(RuntimeError, match="CRITICAL METHODOLOGICAL VIOLATION"):
        mgr.check_and_rollback_on_outcomes(dummy_df, dataset_name="held_out_test.csv")