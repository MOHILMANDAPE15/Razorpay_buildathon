"""Unit tests verifying all 5 fixes from concerns2.md:

1. Generator prompt neutrality (zero targeting hints in Round 1).
2. Decoy columns present and blinded column mapping functions correctly.
3. Bootstrap confidence interval evaluation returns valid uncertainty bounds.
4. Regression harness uses Rs. 500 noise buffer and respects bootstrap CI lower bounds.
5. Defense-Only Audit Gate (Gate 3) rejects evasion rationale and approves defense rationale.
"""

import numpy as np
import pandas as pd
import pytest

from app.agents.generator import HypothesisGenerator
from app.data.loader import load_validation_data
from app.data.schema import (
    BLINDED_COLUMN_MAP,
    PERMISSIBLE_FEATURE_COLUMNS,
    get_blinded_dataframe,
    get_real_dataframe,
)
from app.engine.defense_audit import DefenseOnlyAuditGate
from app.engine.evaluator import CostWeightedEvaluator
from app.engine.regression import RegressionHarness
from app.engine.types import (
    CostMetrics,
    EvaluationReport,
    RuleHypothesis,
    StandardMetrics,
)


def test_issue_1_generator_prompt_has_no_drift_hints():
    """Verifies that the Generator user prompt contains NO hard-coded targeting hints."""
    generator = HypothesisGenerator()
    # Mock generation call or check prompt formatting logic
    # Ensure forbidden leak keywords are absent from the prompt template
    import inspect
    source = inspect.getsource(HypothesisGenerator.generate_hypotheses)
    
    forbidden_leak_strings = [
        "COD high-value risk or pincode history combinations",
        "device reuse abuse (device_order_count_24h)",
        "promo code stacking abuse",
    ]
    for leak in forbidden_leak_strings:
        assert leak not in source, f"Found leaked drift signal hint in generator.py: '{leak}'"


def test_issue_2_decoy_columns_and_blinded_mapping():
    """Verifies that decoy columns exist in schema and blinded mapping translates back and forth."""
    assert "device_model_name" in PERMISSIBLE_FEATURE_COLUMNS
    assert "app_theme_color" in PERMISSIBLE_FEATURE_COLUMNS

    df_val = load_validation_data()
    assert "device_model_name" in df_val.columns
    assert "app_theme_color" in df_val.columns

    # Test blinded transformation at sandbox boundary
    df_blinded = get_blinded_dataframe(df_val)
    assert "col_01" in df_blinded.columns
    assert "col_18" in df_blinded.columns  # device_model_name
    assert "col_19" in df_blinded.columns  # app_theme_color

    df_restored = get_real_dataframe(df_blinded)
    assert "device_model_name" in df_restored.columns
    assert "pincode_rolling_rto_rate" in df_restored.columns


def test_issue_3_bootstrap_confidence_intervals():
    """Verifies that evaluate_hypothesis_bootstrap produces non-degenerate CI bounds."""
    df_val = load_validation_data()
    evaluator = CostWeightedEvaluator()

    rule = RuleHypothesis(
        id="hyp_test_ci",
        name="Test COD High Pincode Rule",
        code="def predict(df):\n    return (df['payment_mode'] == 'COD') & (df['pincode_rolling_rto_rate'] > 0.35)",
    )

    boot_metrics = evaluator.evaluate_hypothesis_bootstrap(
        hypothesis=rule,
        df=df_val,
        n_bootstrap=50,  # Fast test run
        ci_percentile=95.0,
    )

    assert boot_metrics.n_bootstrap == 50
    assert boot_metrics.ci_lower_precision <= boot_metrics.mean_precision <= boot_metrics.ci_upper_precision
    assert boot_metrics.ci_lower_recall <= boot_metrics.mean_recall <= boot_metrics.ci_upper_recall
    assert boot_metrics.ci_lower_net_savings_inr <= boot_metrics.mean_net_savings_inr <= boot_metrics.ci_upper_net_savings_inr
    assert boot_metrics.std_net_savings_inr >= 0.0


def test_issue_4_regression_tolerance_buffer():
    """Verifies that a candidate with slight degradation within the Rs. 500 noise buffer passes Gate 1."""
    evaluator = CostWeightedEvaluator()
    harness = RegressionHarness(evaluator=evaluator, max_cost_drop_tolerance_inr=500.0)

    # Candidate rule
    cand = RuleHypothesis(
        id="cand_1",
        name="Candidate Rule",
        code="def predict(df):\n    return (df['payment_mode'] == 'COD') & (df['order_value'] > 3000)",
    )

    df_val = load_validation_data()

    # First evaluate candidate to get its true score
    cand_eval = evaluator.evaluate_hypothesis(cand, df_val)
    cand_net = cand_eval.cost_metrics.net_financial_savings_inr
    cand_rec = cand_eval.standard_metrics.recall

    # Create synthetic baseline with Rs. 200 higher net savings (within the Rs. 500 buffer)
    baseline_report = EvaluationReport(
        hypothesis_id="base_1",
        hypothesis_name="Baseline Rule",
        is_valid=True,
        standard_metrics=StandardMetrics(
            precision=cand_eval.standard_metrics.precision,
            recall=cand_rec,
            f1=cand_eval.standard_metrics.f1,
            accuracy=cand_eval.standard_metrics.accuracy,
            total_orders=1000,
            flagged_orders=100,
            flag_rate=0.1,
            true_positives=50,
            false_positives=50,
            true_negatives=850,
            false_negatives=50,
        ),
        cost_metrics=CostMetrics(
            avoided_rto_loss_inr=cand_eval.cost_metrics.avoided_rto_loss_inr,
            false_positive_insult_cost_inr=cand_eval.cost_metrics.false_positive_insult_cost_inr,
            net_financial_savings_inr=cand_net + 200.0,  # 200 INR higher -> candidate is 200 INR below
            cost_efficiency_ratio=1.0,
            avg_fp_insult_cost_inr=100.0,
        ),
    )

    passed, report, _ = harness.evaluate_candidate(
        candidate_hypothesis=cand,
        df_validation=df_val,
        baseline_report=baseline_report,
    )
    assert passed, f"Candidate within Rs. 500 buffer should have passed Gate 1, but failed: {report.reasons}"


def test_issue_5_defense_only_audit_gate():
    """Verifies that Gate 3 Defense-Only Audit catches offensive evasion content and approves defense rules."""
    audit_gate = DefenseOnlyAuditGate(use_llm_judge=False)  # Fast deterministic Phase 1 test

    # 1. Offensive evasion rule -> must FAIL
    bad_rule = RuleHypothesis(
        id="bad_01",
        name="Attacker Evasion Rule",
        description="Explains how to structure an order to avoid detection and evade filter.",
        rationale="Fraudsters can avoid detection by keeping order value below threshold.",
        code="def predict(df):\n    return df['payment_mode'] == 'COD'",
    )
    res_bad = audit_gate.audit(bad_rule)
    assert not res_bad.is_defense_only
    assert res_bad.status == "FAILED"
    assert not res_bad.phase_1_keyword_passed
    assert len(res_bad.flagged_keywords) > 0

    # 2. Legitimate defense rule -> must PASS
    good_rule = RuleHypothesis(
        id="good_01",
        name="High COD RTO Risk Filter",
        description="Flags high-risk Cash-on-Delivery orders in pincodes with chronic delivery failures.",
        rationale="Merchants suffer logistics loss when unverified COD orders are sent to high-return pincodes.",
        code="def predict(df):\n    return (df['payment_mode'] == 'COD') & (df['pincode_rolling_rto_rate'] > 0.35)",
    )
    res_good = audit_gate.audit(good_rule)
    assert res_good.is_defense_only
    assert res_good.status == "PASSED"
    assert res_good.phase_1_keyword_passed
