"""Unit and integration tests for Generator, Reflector, Repair, and Evolution Runner."""

import json
import pandas as pd
import pytest

from app.agents.generator import HypothesisGenerator
from app.agents.prompts import GENERATOR_SYSTEM_PROMPT, REFLECTOR_SYSTEM_PROMPT, REPAIR_SYSTEM_PROMPT
from app.agents.reflector import HypothesisReflector
from app.agents.repair import repair_rule_code
from app.agents.runner import EvolutionRunner
from app.engine.evaluator import CostWeightedEvaluator
from app.engine.notepad import Notepad
from app.engine.types import CostMetrics, DiagnosticOrder, EvaluationReport, RuleHypothesis, StandardMetrics


@pytest.fixture
def sample_orders_df():
    """Provides a sample DataFrame containing all valid schema features."""
    return pd.DataFrame({
        "order_id": ["ORD01", "ORD02", "ORD03", "ORD04"],
        "order_value": [1000.0, 4500.0, 2000.0, 12000.0],
        "payment_mode": ["COD", "COD", "Prepaid", "COD"],
        "is_first_time_customer": [1, 1, 0, 1],
        "customer_account_age_days": [5, 12, 180, 4],
        "customer_prior_orders": [0, 0, 8, 1],
        "pincode_rolling_rto_rate": [0.45, 0.35, 0.05, 0.40],
        "promo_code_used": [True, True, False, False],
        "device_order_count_24h": [4, 3, 0, 1],
        "order_hour": [23, 2, 14, 11],
        "day_index": [10, 25, 40, 50],
        "item_category": ["Electronics", "Fashion", "Grocery", "Beauty"],
        "pincode": ["110001", "400001", "560001", "700001"],
        "device_id": ["DEV01", "DEV02", "DEV03", "DEV04"],
        "device_model_name": ["Samsung Galaxy M34", "Redmi Note 12", "iPhone 13", "OnePlus Nord"],
        "app_theme_color": ["dark", "light", "system", "dark"],
        "is_rto": [1, 1, 0, 0],
    })


def test_notepad_lineage_and_ranking():
    """Verifies that Notepad properly tracks hypotheses, mutation lineage, and ranks by net savings."""
    notepad = Notepad()

    hyp_1 = RuleHypothesis(id="hyp_01", name="Rule A", code="def predict(df): return [0]*len(df)")
    hyp_2 = RuleHypothesis(id="hyp_02", name="Rule B (Child of A)", code="def predict(df): return [1]*len(df)", parent_ids=["hyp_01"])

    notepad.add_hypothesis(hyp_1)
    notepad.add_hypothesis(hyp_2)

    # Verify lineage
    assert "hyp_01" in notepad.lineage_graph
    assert "hyp_02" in notepad.lineage_graph["hyp_01"]

    # Record evaluations
    rep_1 = EvaluationReport(
        hypothesis_id="hyp_01",
        hypothesis_name="Rule A",
        is_valid=True,
        standard_metrics=StandardMetrics(precision=0.5, recall=0.4, f1=0.44, accuracy=0.7, total_orders=10, flagged_orders=4, flag_rate=0.4, true_positives=2, false_positives=2, true_negatives=5, false_negatives=1),
        cost_metrics=CostMetrics(avoided_rto_loss_inr=500.0, false_positive_insult_cost_inr=200.0, net_financial_savings_inr=300.0, cost_efficiency_ratio=2.5, avg_fp_insult_cost_inr=100.0),
    )
    rep_2 = EvaluationReport(
        hypothesis_id="hyp_02",
        hypothesis_name="Rule B",
        is_valid=True,
        standard_metrics=StandardMetrics(precision=0.8, recall=0.9, f1=0.85, accuracy=0.9, total_orders=10, flagged_orders=5, flag_rate=0.5, true_positives=4, false_positives=1, true_negatives=5, false_negatives=0),
        cost_metrics=CostMetrics(avoided_rto_loss_inr=1000.0, false_positive_insult_cost_inr=100.0, net_financial_savings_inr=900.0, cost_efficiency_ratio=10.0, avg_fp_insult_cost_inr=100.0),
    )

    notepad.record_evaluation(rep_1)
    notepad.record_evaluation(rep_2)

    top = notepad.get_top_hypotheses(top_k=2)
    assert len(top) == 2
    # Rule B (₹900 net savings) must be ranked #1
    assert top[0][0].id == "hyp_02"
    assert top[0][1].cost_metrics.net_financial_savings_inr == 900.0

    summary = notepad.get_history_summary_for_generator()
    assert "Rule B" in summary
    assert "₹900" in summary


def test_repair_handler_fixes_syntax_error(sample_orders_df):
    """Verifies that the repair handler successfully repairs code with a syntax error."""
    broken_code = """
def predict(df):
    # Syntax error: unclosed parenthesis
    return (df['payment_mode'] == 'COD' & (df['order_value'] > 1000)
"""
    error_msg = "SyntaxError: '(' was never closed"

    success, repaired_code, _ = repair_rule_code(
        broken_code=broken_code,
        error_message=error_msg,
        df_sample=sample_orders_df,
    )

    # Groq should fix the parenthesis
    assert success is True
    assert "def predict(" in repaired_code


def test_live_generator_proposes_valid_rules(sample_orders_df):
    """Verifies that the Generator generates valid, executable rule hypotheses using Groq."""
    generator = HypothesisGenerator()
    candidates = generator.generate_hypotheses(
        n_hypotheses=2,
        notepad_summary="Cold start round",
        generation_round=1,
        df_sample=sample_orders_df,
    )

    assert len(candidates) >= 1
    for cand in candidates:
        assert cand.name
        assert "def predict(" in cand.code
        assert cand.status == "candidate"


def test_live_reflector_mutates_rule(sample_orders_df):
    """Verifies that the Reflector agent diagnoses failures and produces a mutated child rule."""
    parent_rule = RuleHypothesis(
        id="hyp_parent_01",
        name="Naive COD High Pincode Rule",
        code="def predict(df):\n    return (df['payment_mode'] == 'COD') & (df['pincode_rolling_rto_rate'] > 0.3)",
        description="Flags high pincode COD orders.",
    )

    eval_report = EvaluationReport(
        hypothesis_id="hyp_parent_01",
        hypothesis_name=parent_rule.name,
        is_valid=True,
        standard_metrics=StandardMetrics(
            precision=0.45, recall=0.30, f1=0.36, accuracy=0.65,
            total_orders=100, flagged_orders=20, flag_rate=0.20,
            true_positives=9, false_positives=11, true_negatives=70, false_negatives=10
        ),
        cost_metrics=CostMetrics(
            avoided_rto_loss_inr=2250.0,
            false_positive_insult_cost_inr=5400.0,
            net_financial_savings_inr=-3150.0,
            cost_efficiency_ratio=0.42,
            avg_fp_insult_cost_inr=490.9,
        ),
        top_false_positives=[
            DiagnosticOrder(
                order_id="ORD_FP_1",
                order_value=12000.0,
                true_label=0,
                predicted_label=1,
                cost_impact_inr=1800.0,
                error_type="FALSE_POSITIVE",
                features={"payment_mode": "COD", "pincode_rolling_rto_rate": 0.35, "customer_prior_orders": 3, "promo_code_used": False, "device_order_count_24h": 0},
                diagnostic_reason="High value genuine customer falsely blocked.",
            )
        ],
        top_false_negatives=[
            DiagnosticOrder(
                order_id="ORD_FN_1",
                order_value=2500.0,
                true_label=1,
                predicted_label=0,
                cost_impact_inr=250.0,
                error_type="FALSE_NEGATIVE",
                features={"payment_mode": "COD", "pincode_rolling_rto_rate": 0.15, "customer_prior_orders": 0, "promo_code_used": True, "device_order_count_24h": 4},
                diagnostic_reason="Missed device-reuse and promo stacking fraud.",
            )
        ],
    )

    reflector = HypothesisReflector()
    mutated = reflector.reflect_and_mutate(
        parent_hypothesis=parent_rule,
        eval_report=eval_report,
        generation_round=2,
        df_sample=sample_orders_df,
    )

    assert mutated is not None
    assert mutated.parent_ids == ["hyp_parent_01"]
    assert "def predict(" in mutated.code
