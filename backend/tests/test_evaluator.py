"""Unit tests for the Cost-Weighted Evaluator, feature isolation, and dataset loader."""

import numpy as np
import pandas as pd
import pytest

from app.core.config import CostModelConfig
from app.data.loader import (
    HeldOutTestAlreadyAccessedError,
    evaluate_on_held_out_test,
    is_held_out_test_accessed,
    load_train_data,
    load_validation_data,
    reset_held_out_access_guard_for_testing,
)
from app.data.schema import FORBIDDEN_COLUMNS, extract_features_and_labels, sanitize_features
from app.engine.evaluator import CostWeightedEvaluator
from app.engine.types import RuleHypothesis


@pytest.fixture
def mock_dataset():
    """Constructs a controlled dataset with known labels and order values."""
    data = {
        "order_id": [f"ord_{i}" for i in range(10)],
        "order_value": [
            1000.0,  # 0: TP
            2000.0,  # 1: TP
            3000.0,  # 2: TP
            4000.0,  # 3: FP (Insult cost: 4000 * 0.15 = 600)
            500.0,   # 4: FP (Insult cost: 500 * 0.15 = 75)
            1500.0,  # 5: TN
            800.0,   # 6: TN
            1200.0,  # 7: TN
            2500.0,  # 8: FN (Missed RTO fraud)
            3500.0,  # 9: FN (Missed RTO fraud)
        ],
        "payment_mode": ["COD"] * 10,
        "is_first_time_customer": [1] * 10,
        "pincode_rolling_rto_rate": [0.35] * 10,
        "phase": ["pre_drift"] * 10,       # FORBIDDEN
        "drift_weight": [0.0] * 10,        # FORBIDDEN
        "is_rto": [1, 1, 1, 0, 0, 0, 0, 0, 1, 1],  # Ground truth (5 RTO, 5 Genuine)
    }
    return pd.DataFrame(data)


def test_cost_weighted_evaluation_formula(mock_dataset):
    """Verifies that cost-weighted formulas match hand-calculated numbers."""
    evaluator = CostWeightedEvaluator(
        config=CostModelConfig(avoided_rto_cost_inr=250.0, fp_margin_loss_rate=0.15)
    )

    # Rule flags orders 0, 1, 2, 3, 4
    # Predictions:
    # 0, 1, 2: True Positives (3 TP)
    # 3, 4: False Positives (2 FP)
    # 5, 6, 7: True Negatives (3 TN)
    # 8, 9: False Negatives (2 FN)
    rule_code = """
def predict(df):
    return df['order_id'].isin(['ord_0', 'ord_1', 'ord_2', 'ord_3', 'ord_4'])
"""
    hyp = RuleHypothesis(id="hyp_test_01", name="Test Rule", code=rule_code)
    report = evaluator.evaluate_hypothesis(hyp, mock_dataset)

    assert report.is_valid is True
    assert report.standard_metrics is not None
    assert report.cost_metrics is not None

    # Standard metrics verification
    # TP = 3, FP = 2, TN = 3, FN = 2, Total = 10
    sm = report.standard_metrics
    assert sm.true_positives == 3
    assert sm.false_positives == 2
    assert sm.true_negatives == 3
    assert sm.false_negatives == 2
    assert sm.precision == pytest.approx(3 / 5, abs=1e-3)
    assert sm.recall == pytest.approx(3 / 5, abs=1e-3)
    assert sm.accuracy == pytest.approx(6 / 10, abs=1e-3)

    # Financial metrics verification:
    # Avoided Loss = 3 * 250 = 750.0
    # FP Insult Cost = (4000 * 0.15) + (500 * 0.15) = 600 + 75 = 675.0
    # Net Savings = 750 - 675 = 75.0
    cm = report.cost_metrics
    assert cm.avoided_rto_loss_inr == 750.0
    assert cm.false_positive_insult_cost_inr == 675.0
    assert cm.net_financial_savings_inr == 75.0
    assert cm.cost_efficiency_ratio == pytest.approx(750.0 / 675.0, abs=1e-2)


def test_forbidden_columns_are_stripped_from_rule_access(mock_dataset):
    """Verifies that rules attempting to read phase or is_rto raise a KeyError."""
    evaluator = CostWeightedEvaluator()

    rule_attempting_leak_access = """
def predict(df):
    # Trying to cheat using forbidden ground-truth label
    return df['is_rto'] == 1
"""
    hyp = RuleHypothesis(id="hyp_cheat", name="Cheat Rule", code=rule_attempting_leak_access)
    report = evaluator.evaluate_hypothesis(hyp, mock_dataset)

    # Must fail execution because 'is_rto' was stripped from features
    assert report.is_valid is False
    assert "is_rto" in report.error_message


def test_sanitization_removes_all_forbidden_columns(mock_dataset):
    """Directly verifies the schema sanitization utility."""
    clean_df = sanitize_features(mock_dataset)
    for col in FORBIDDEN_COLUMNS:
        assert col not in clean_df.columns
    assert "order_id" in clean_df.columns
    assert "order_value" in clean_df.columns


def test_diagnostic_failure_case_extraction(mock_dataset):
    """Verifies that top false positive and false negative cases are extracted for Reflector."""
    evaluator = CostWeightedEvaluator(
        config=CostModelConfig(avoided_rto_cost_inr=250.0, fp_margin_loss_rate=0.15)
    )

    rule_code = """
def predict(df):
    return df['order_id'].isin(['ord_0', 'ord_1', 'ord_2', 'ord_3', 'ord_4'])
"""
    hyp = RuleHypothesis(id="hyp_test_diag", name="Diag Test", code=rule_code)
    report = evaluator.evaluate_hypothesis(hyp, mock_dataset, top_k_diagnostics=2)

    # 2 FPs: ord_3 (val 4000) and ord_4 (val 500)
    assert len(report.top_false_positives) == 2
    # Highest insult cost (ord_3) must come first
    assert report.top_false_positives[0].order_id == "ord_3"
    assert report.top_false_positives[0].cost_impact_inr == 600.0
    assert "phase" not in report.top_false_positives[0].features
    assert "is_rto" not in report.top_false_positives[0].features

    # 2 FNs: ord_8 (val 2500) and ord_9 (val 3500)
    assert len(report.top_false_negatives) == 2
    # Highest order value (ord_9) must come first
    assert report.top_false_negatives[0].order_id == "ord_9"


def test_real_dataset_loading():
    """Verifies that train.csv and validation.csv load with valid shapes and schemas."""
    df_train = load_train_data()
    assert len(df_train) == 10807
    assert "is_rto" in df_train.columns

    df_val = load_validation_data()
    assert len(df_val) == 3885
    assert "is_rto" in df_val.columns


def test_held_out_test_single_touch_guarantee():
    """Verifies that held_out_test.csv can be evaluated strictly once and blocks subsequent calls."""
    reset_held_out_access_guard_for_testing()
    assert is_held_out_test_accessed() is False

    # First call: Should succeed
    result_1 = evaluate_on_held_out_test(lambda df: len(df))
    assert result_1 == 2641
    assert is_held_out_test_accessed() is True

    # Second call: Must raise HeldOutTestAlreadyAccessedError
    with pytest.raises(HeldOutTestAlreadyAccessedError) as exc_info:
        evaluate_on_held_out_test(lambda df: len(df))

    assert "already been accessed" in str(exc_info.value)
    
    # Cleanup guard
    reset_held_out_access_guard_for_testing()
