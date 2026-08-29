"""Playground Test Case Generator & Explanation API.

Provides:
1. GET /api/v1/playground/generate: Samples an order from the pre-computed difficulty tier pools
   (Easy, Medium, Hard) strictly from the validation split (Days 56-75), runs it through the
   production frozen ensemble, and returns routing decisions, matched rules, and ground truth.
2. POST /api/v1/playground/explain: Generates grounded natural-language explanations of the
   decision logic using an LLM call, with deterministic fallback templates and timeout guards.
"""

import json
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.llm import extract_response_text, get_llm_client
from app.data.loader import load_validation_data
from app.engine.frozen_rule_snapshot import load_frozen_v1_rules
from app.engine.router import ThreeWayRouter
from app.engine.selector import EnsembleRule
from app.engine.types import RuleHypothesis

router = APIRouter(prefix="/playground", tags=["Playground"])

_POOLS_PATH = Path(__file__).resolve().parent.parent / "data" / "playground_pools.json"

# Cached resources in memory for instant responses
_POOLS_CACHE: Optional[Dict[str, List[str]]] = None
_VAL_DF_CACHE: Optional[pd.DataFrame] = None
_VAL_DICT_CACHE: Optional[Dict[str, Dict[str, Any]]] = None
_ENSEMBLE_CACHE: Optional[EnsembleRule] = None
_ROUTER_CACHE: Optional[ThreeWayRouter] = None


def _get_resources():
    """Initializes and caches validation data, rules, and pools."""
    global _POOLS_CACHE, _VAL_DF_CACHE, _VAL_DICT_CACHE, _ENSEMBLE_CACHE, _ROUTER_CACHE

    if _POOLS_CACHE is None:
        if _POOLS_PATH.exists():
            with open(_POOLS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                _POOLS_CACHE = data.get("pools", {})
        else:
            _POOLS_CACHE = {"easy": [], "medium": [], "hard": []}

    if _VAL_DF_CACHE is None:
        _VAL_DF_CACHE = load_validation_data()
        _VAL_DICT_CACHE = {
            str(row["order_id"]): row.to_dict()
            for _, row in _VAL_DF_CACHE.iterrows()
        }

    if _ENSEMBLE_CACHE is None:
        rules = load_frozen_v1_rules()
        _ENSEMBLE_CACHE = EnsembleRule(rules)
        _ROUTER_CACHE = ThreeWayRouter()

    return _POOLS_CACHE, _VAL_DF_CACHE, _VAL_DICT_CACHE, _ENSEMBLE_CACHE, _ROUTER_CACHE


class MatchedRuleDetail(BaseModel):
    rule_id: str
    rule_name: str
    rule_code: str


class RuleEvaluationDetail(BaseModel):
    rule_id: str
    rule_name: str
    rule_code: str
    is_matched: bool


class OrderTestCaseResponse(BaseModel):
    order_id: str
    tier: str
    tier_label: str
    tier_description: str
    order_features: Dict[str, Any]
    routing_decision: str
    risk_score: float
    is_flagged: bool
    matched_rules: List[MatchedRuleDetail]
    evaluated_rules: List[RuleEvaluationDetail] = Field(default_factory=list)
    ground_truth: Dict[str, Any]
    outcome_classification: str
    is_correct: Optional[bool]
    verdict_badge: str
    explanation: Optional[str] = None



class ExplainRequest(BaseModel):
    order_id: str
    tier: str
    order_features: Dict[str, Any]
    routing_decision: str
    risk_score: float
    matched_rules: List[Dict[str, Any]] = Field(default_factory=list)
    ground_truth: Dict[str, Any]
    outcome_classification: str


class ExplainResponse(BaseModel):
    order_id: str
    explanation: str
    model_used: str
    source: str  # "llm" or "fallback_template"


def _build_fallback_explanation(
    tier: str,
    outcome: str,
    decision: str,
    risk: float,
    rules: List[Dict[str, Any]],
    features: Dict[str, Any],
    is_rto: int,
) -> str:
    """Generates a deterministic grounded fallback explanation if LLM is offline or times out."""
    pay_mode = features.get("payment_mode", "UNKNOWN")
    order_val = features.get("order_value", 0.0)
    pincode_rate = features.get("pincode_rolling_rto_rate", 0.20)
    acc_age = features.get("customer_account_age_days", 30)

    if outcome == "CORRECT_BLOCK":
        rule_str = f"triggered rule '{rules[0].get('rule_name', rules[0].get('rule_id', 'Risk Rule'))}'" if rules else "exceeded the high-risk threshold (T=0.70)"
        return (
            f"This order (Value: ₹{order_val:,.2f}, Payment: {pay_mode}, Account Age: {acc_age}d) {rule_str} "
            f"with a composite risk score of {risk:.2f}. The system correctly AUTO_BLOCKED this order, preventing a verified RTO loss and saving ₹250 in logistics costs."
        )
    elif outcome == "CORRECT_APPROVE":
        return (
            f"This order (Value: ₹{order_val:,.2f}, Payment: {pay_mode}) exhibited clean behavioral characteristics with an ambient risk score of {risk:.2f} (< 0.35 threshold) "
            f"and matched no fraud heuristics. The system correctly AUTO_APPROVED the order for frictionless checkout, and it was successfully delivered without RTO."
        )
    elif outcome == "BORDERLINE_REVIEW":
        return (
            f"This order fell into the intermediate risk band ({risk:.2f} in [0.35, 0.70]) driven by moderate pincode RTO rate ({pincode_rate*100:.1f}%) "
            f"or single-rule matching. It was routed to the HUMAN MANUAL REVIEW queue to verify delivery address and customer intent without inflicting an automated false positive insult."
        )
    elif outcome == "FALSE_NEGATIVE_MISS":
        return (
            f"This order is an intentionally hard case representing the adaptation gap this system is designed to close over time. "
            f"While ground-truth was RTO, the order scored low risk ({risk:.2f}) under the frozen baseline rules (Payment: {pay_mode}, Account Age: {acc_age}d). "
            f"The Residual Miner isolates these unflagged misses to synthesize next-generation defense agendas."
        )
    elif outcome == "FALSE_POSITIVE_INSULT":
        return (
            f"This order (Value: ₹{order_val:,.2f}) matched risk patterns with score {risk:.2f} and was AUTO_BLOCKED, but the buyer was legitimate (delivered/non-RTO). "
            f"This incurs a merchant margin loss of ₹{order_val * 0.15:,.2f} (15% insult cost), illustrating why high precision (T=0.70) is economically vital."
        )
    else:
        return f"Order evaluated under {decision} with risk score {risk:.2f} against ground truth {'RTO' if is_rto == 1 else 'DELIVERED'}."


@router.get("/generate", response_model=OrderTestCaseResponse)
def generate_playground_test_case(
    tier: str = Query("easy", pattern="^(easy|medium|hard)$", description="Difficulty tier: easy, medium, or hard"),
):
    """Samples a real order from the specified tier's precomputed pool and runs it through the production ensemble."""
    pools, df_val, val_dict, ensemble, router_inst = _get_resources()

    tier_pool = pools.get(tier.lower(), [])
    if not tier_pool:
        # Fallback to random order from validation if pool empty
        tier_pool = list(val_dict.keys())

    order_id = random.choice(tier_pool)
    order_row = val_dict.get(order_id)
    if not order_row:
        order_row = df_val.sample(n=1).iloc[0].to_dict()
        order_id = str(order_row["order_id"])

    # Run through router
    single_df = pd.DataFrame([order_row])
    decision = router_inst.route_batch(single_df, ensemble)[0]

    # Inspect matched rules with code
    from app.core.sandbox import execute_rule_sandboxed
    from app.data.schema import sanitize_features

    sanitized = sanitize_features(single_df)
    matched_rule_details: List[MatchedRuleDetail] = []
    evaluated_rule_details: List[RuleEvaluationDetail] = []
    for r in ensemble.rules:
        flags = execute_rule_sandboxed(r.code, sanitized)
        matched = bool(flags[0])
        if matched:
            matched_rule_details.append(
                MatchedRuleDetail(
                    rule_id=r.id,
                    rule_name=r.name or r.id,
                    rule_code=r.code,
                )
            )
        evaluated_rule_details.append(
            RuleEvaluationDetail(
                rule_id=r.id,
                rule_name=r.name or r.id,
                rule_code=r.code,
                is_matched=matched,
            )
        )

    is_rto = int(order_row.get("is_rto", 0))

    # Classify outcome
    if decision.decision == "AUTO_BLOCK" and is_rto == 1:
        outcome = "CORRECT_BLOCK"
        is_correct = True
        badge = "PASS (True Positive Avoided RTO)"
    elif decision.decision == "AUTO_APPROVE" and is_rto == 0:
        outcome = "CORRECT_APPROVE"
        is_correct = True
        badge = "PASS (True Negative Frictionless)"
    elif decision.decision == "AUTO_APPROVE" and is_rto == 1:
        outcome = "FALSE_NEGATIVE_MISS"
        is_correct = False
        badge = "GAP (False Negative Miss)"
    elif decision.decision == "AUTO_BLOCK" and is_rto == 0:
        outcome = "FALSE_POSITIVE_INSULT"
        is_correct = False
        badge = "INSULT (False Positive Margin Loss)"
    else:
        outcome = "BORDERLINE_REVIEW"
        is_correct = None
        badge = "REVIEW (Routed to Human Investigation)"

    tier_descriptions = {
        "easy": "Simulates standard transactions: unambiguous high-confidence fraud attempts or clean verified buyers.",
        "medium": "Simulates borderline transactions: intermediate signals scoring near threshold boundaries (0.35–0.70).",
        "hard": "Simulates deceptive fraud scenarios: unflagged edge cases, newly emerging vectors, and false-positive margin risk scenarios.",
    }

    tier_labels = {
        "easy": "Easy (Clear Pattern)",
        "medium": "Medium (Borderline / Boundary)",
        "hard": "Hard (Deceptive / Adaptation Gap)",
    }

    # Clean feature dict for response
    feature_cols = [
        "order_id", "order_value", "payment_mode", "item_category",
        "customer_account_age_days", "customer_prior_orders", "pincode_rolling_rto_rate",
        "promo_code_used", "device_order_count_24h", "order_hour", "day_index",
    ]
    clean_features = {
        k: (float(order_row[k]) if isinstance(order_row[k], (float, int)) and not isinstance(order_row[k], bool) and k != "customer_prior_orders" and k != "customer_account_age_days" and k != "day_index" and k != "order_hour" else order_row[k])
        for k in feature_cols if k in order_row
    }

    # Generate quick default explanation
    default_expl = _build_fallback_explanation(
        tier=tier,
        outcome=outcome,
        decision=decision.decision,
        risk=decision.risk_score,
        rules=[r.model_dump() for r in matched_rule_details],
        features=clean_features,
        is_rto=is_rto,
    )

    return OrderTestCaseResponse(
        order_id=order_id,
        tier=tier,
        tier_label=tier_labels.get(tier, tier.capitalize()),
        tier_description=tier_descriptions.get(tier, ""),
        order_features=clean_features,
        routing_decision=decision.decision,
        risk_score=decision.risk_score,
        is_flagged=decision.is_flagged,
        matched_rules=matched_rule_details,
        evaluated_rules=evaluated_rule_details,
        ground_truth={
            "is_rto": is_rto,
            "actual_outcome": "RTO Refused / Returned" if is_rto == 1 else "Successfully Delivered",
        },
        outcome_classification=outcome,
        is_correct=is_correct,
        verdict_badge=badge,
        explanation=default_expl,
    )



@router.post("/explain", response_model=ExplainResponse)
def explain_order_decision(payload: ExplainRequest):
    """Generates a natural-language explanation via LLM call strictly grounded in order features, matched rules, and ground truth."""
    rules_text = "\n".join([f"- {r.get('rule_name', r.get('rule_id'))}: {r.get('rule_code', '')}" for r in payload.matched_rules]) if payload.matched_rules else "No active rules matched (ambient baseline risk only)."
    
    is_rto = int(payload.ground_truth.get("is_rto", 0))
    gt_label = "RTO (Buyer refused/returned order)" if is_rto == 1 else "DELIVERED (Successful delivery)"

    prompt = (
        f"You are the Aegis-RTO Explanation Agent. Provide a concise (2-3 sentences), highly factual explanation for how and why Aegis routed this order.\n\n"
        f"STRICT GROUNDING RULES:\n"
        f"1. Reason ONLY using the provided order features, matched rule(s), routing decision, and ground truth below. Do not invent details.\n"
        f"2. Reference key numeric values (e.g. order value, payment mode, account age, risk score) that justified the outcome.\n"
        f"{'3. CRITICAL: For this HARD-tier miss, explicitly frame the explanation as: \"this is an intentionally hard case representing the adaptation gap this system is designed to close over time\" rather than a bare system failure.' if payload.outcome_classification == 'FALSE_NEGATIVE_MISS' else ''}\n"
        f"{'3. CRITICAL: For this FALSE POSITIVE case, explicitly frame the explanation around the honest cost-tradeoff: the order triggered risk heuristics resulting in an auto-block, incurring a 15% merchant gross margin loss insult cost, illustrating why high precision (T=0.70) is economically vital.' if payload.outcome_classification == 'FALSE_POSITIVE_INSULT' else ''}\n\n"
        f"ORDER CONTEXT:\n"
        f"- Order ID: {payload.order_id}\n"
        f"- Difficulty Tier: {payload.tier.upper()}\n"
        f"- Features: {json.dumps(payload.order_features)}\n"
        f"- Risk Score: {payload.risk_score:.4f}\n"
        f"- Routing Decision: {payload.routing_decision}\n"
        f"- Matched Rules:\n{rules_text}\n"
        f"- Ground Truth: {gt_label}\n"
        f"- Outcome Classification: {payload.outcome_classification}\n\n"
        f"Explanation:"
    )

    try:
        from langchain_core.messages import HumanMessage
        llm = get_llm_client(max_tokens=2048, temperature=0.3)
        response = llm.invoke([HumanMessage(content=prompt)])
        raw_text = extract_response_text(response)
        if raw_text and len(raw_text.strip()) > 15:
            return ExplainResponse(
                order_id=payload.order_id,
                explanation=raw_text.strip(),
                model_used=os.getenv("DEFAULT_LLM_MODEL", "gemini-3.6-flash"),
                source="llm",
            )
    except Exception as e:
        print(f"[Playground Explain] LLM generation failed or timed out: {e}")

    # Deterministic fallback
    fallback = _build_fallback_explanation(
        tier=payload.tier,
        outcome=payload.outcome_classification,
        decision=payload.routing_decision,
        risk=payload.risk_score,
        rules=payload.matched_rules,
        features=payload.order_features,
        is_rto=is_rto,
    )
    return ExplainResponse(
        order_id=payload.order_id,
        explanation=fallback,
        model_used="deterministic_fallback_engine",
        source="fallback_template",
    )
