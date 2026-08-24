"""Unit tests for the Gate 1 Regression Suite / Harness."""

import pandas as pd
import pytest

from app.core.config import CostModelConfig
from app.engine.evaluator import CostWeightedEvaluator
from app.engine.regression import RegressionHarness
from app.engine.types import CostMetrics, EvaluationReport, RuleHypothesis, StandardMetrics


@pytest.fixture
def mock_validation_dataset():
    """Constructs a mock validation dataset for regression checks."""
    data = {
        "order_id": [f"val_{i}" for i in range(20)],
        "order_value": [1000.0] * 20,
        "payment_mode": ["COD"] * 20,
        "is_first_time_customer": [1] * 10 + [0] * 10,
        "pincode_rolling_rto_rate": [0.40] * 10 + [0.05] * 10,
        "promo_code_used": [1] * 5 + [0] * 15,
        "device_order_count_24h": [3] * 5 + [0] * 15,
        "phase": ["transition"] * 20,
        "drift_weight": [0.5] * 20,
        "is_rto": [1] * 8 + [0] * 12,  # 8 RTO frauds, 12 genuine
    }
    return pd.DataFrame(data)


def test_cold_start_candidate_passes_with_positive_savings(mock_validation_dataset):
    """Verifies that an initial candidate passes Gate 1 when generating positive net savings."""
    harness = RegressionHarness()

    rule_code = """
def predict(df):
    # Flags first 6 orders (all 6 are actual RTOs)
    return df['order_id'].isin(['val_0', 'val_1', 'val_2', 'val_3', 'val_4', 'val_5'])
"""
    hyp = RuleHypothesis(id="hyp_cold_start", name="Good Initial Rule", code=rule_code)
    passed, reg_report, eval_report = harness.evaluate_candidate(
        candidate_hypothesis=hyp,
        df_validation=mock_validation_dataset,
        baseline_report=None,
    )

    assert passed is True
    assert reg_report.status == "PASSED"
    assert reg_report.candidate_net_savings_inr > 0


def test_candidate_passes_when_improving_on_baseline(mock_validation_dataset):
    """Verifies that candidate passes Gate 1 when it matches or beats baseline metrics."""
    harness = RegressionHarness()

    # Baseline: 4 TPs, 0 FPs -> Net savings = 4 * 250 = 1000.0, Recall = 4/8 = 0.50
    baseline_eval = EvaluationReport(
        hypothesis_id="hyp_v1",
        hypothesis_name="Baseline v1",
        is_valid=True,
        standard_metrics=StandardMetrics(
            precision=1.0,
            recall=0.50,
            f1=0.667,
            accuracy=0.80,
            total_orders=20,
            flagged_orders=4,
            flag_rate=0.20,
            true_positives=4,
            false_positives=0,
            true_negatives=12,
            false_negatives=4,
        ),
        cost_metrics=CostMetrics(
            avoided_rto_loss_inr=1000.0,
            false_positive_insult_cost_inr=0.0,
            net_financial_savings_inr=1000.0,
            cost_efficiency_ratio=1000.0,
            avg_fp_insult_cost_inr=0.0,
        ),
    )

    # Candidate: 6 TPs, 0 FPs -> Net savings = 6 * 250 = 1500.0, Recall = 6/8 = 0.75
    candidate_code = """
def predict(df):
    return df['order_id'].isin(['val_0', 'val_1', 'val_2', 'val_3', 'val_4', 'val_5'])
"""
    cand_hyp = RuleHypothesis(id="hyp_v2", name="Improved v2", code=candidate_code)
    passed, reg_report, eval_report = harness.evaluate_candidate(
        candidate_hypothesis=cand_hyp,
        df_validation=mock_validation_dataset,
        baseline_report=baseline_eval,
    )

    assert passed is True
    assert reg_report.status == "PASSED"
    assert reg_report.delta_net_savings_inr == 500.0
    assert reg_report.delta_recall == 0.25


def test_candidate_fails_on_catastrophic_financial_regression(mock_validation_dataset):
    """Verifies that a rule triggering massive false positives fails Gate 1."""
    harness = RegressionHarness()

    baseline_eval = EvaluationReport(
        hypothesis_id="hyp_v1",
        hypothesis_name="Baseline v1",
        is_valid=True,
        standard_metrics=StandardMetrics(
            precision=1.0,
            recall=0.50,
            f1=0.667,
            accuracy=0.80,
            total_orders=20,
            flagged_orders=4,
            flag_rate=0.20,
            true_positives=4,
            false_positives=0,
            true_negatives=12,
            false_negatives=4,
        ),
        cost_metrics=CostMetrics(
            avoided_rto_loss_inr=1000.0,
            false_positive_insult_cost_inr=0.0,
            net_financial_savings_inr=1000.0,
            cost_efficiency_ratio=1000.0,
            avg_fp_insult_cost_inr=0.0,
        ),
    )

    # Candidate flags everything (12 FPs @ Rs. 150 insult cost = Rs. 1800 loss vs 8 TP @ Rs. 250 = Rs. 2000 => Net = 200)
    # Net drops from 1000 to 200 (delta = -800)
    overflagging_code = """
def predict(df):
    return [1] * len(df)
"""
    cand_hyp = RuleHypothesis(id="hyp_overflag", name="Overflagging Rule", code=overflagging_code)
    passed, reg_report, eval_report = harness.evaluate_candidate(
        candidate_hypothesis=cand_hyp,
        df_validation=mock_validation_dataset,
        baseline_report=baseline_eval,
    )

    assert passed is False
    assert reg_report.status == "FAILED"
    assert "Net financial savings regressed" in reg_report.reasons[0]


def test_candidate_fails_on_execution_error(mock_validation_dataset):
    """Verifies that broken rule code immediately fails Gate 1."""
    harness = RegressionHarness()

    broken_code = """
def predict(df):
    return 1 / 0
"""
    broken_hyp = RuleHypothesis(id="hyp_broken", name="Broken Rule", code=broken_code)
    passed, reg_report, eval_report = harness.evaluate_candidate(
        candidate_hypothesis=broken_hyp,
        df_validation=mock_validation_dataset,
        baseline_report=None,
    )

    assert passed is False
    assert reg_report.status == "FAILED"
    assert "failed execution" in reg_report.reasons[0].lower()
