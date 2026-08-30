"""Playground Test Case Generator & Explanation API.

Provides:
1. GET /api/v1/playground/generate: Samples uniformly at random from the full
   validation split pool (Days 56-75, non-held-out), executes the production
   frozen ensemble under 3-way routing, and computes post-hoc classification
   ('Clear pattern', 'Borderline', 'Adaptation gap') with plain-language reasoning.
2. POST /api/v1/playground/explain: Generates grounded natural-language explanations
   incorporating the post-hoc classification and arithmetic via Gemini LLM with
   deterministic fallback engine.
"""

import json
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.llm import extract_response_text, get_llm_client
from app.data.loader import load_validation_data
from app.engine.frozen_rule_snapshot import load_frozen_v1_rules
from app.engine.router import ThreeWayRouter
from app.engine.selector import EnsembleRule

router = APIRouter(prefix="/playground", tags=["Playground"])

# Cached resources in memory for instant responses
_VAL_DF_CACHE: Optional[pd.DataFrame] = None
_VAL_DICT_CACHE: Optional[Dict[str, Dict[str, Any]]] = None
_ENSEMBLE_CACHE: Optional[EnsembleRule] = None
_ROUTER_CACHE: Optional[ThreeWayRouter] = None


def _get_resources():
    """Initializes and caches validation data and rules ensemble."""
    global _VAL_DF_CACHE, _VAL_DICT_CACHE, _ENSEMBLE_CACHE, _ROUTER_CACHE

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

    return _VAL_DF_CACHE, _VAL_DICT_CACHE, _ENSEMBLE_CACHE, _ROUTER_CACHE


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
    classification: str
    classification_reason: str
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
    dataset_split: str = "validation"
    split_description: str = "Validation Split (Days 56–75, strictly non-held-out)"
    explanation: Optional[str] = None
    tier: Optional[str] = None
    tier_label: Optional[str] = None


class ExplainRequest(BaseModel):
    order_id: str
    classification: Optional[str] = None
    classification_reason: Optional[str] = None
    order_features: Dict[str, Any]
    routing_decision: str
    risk_score: float
    matched_rules: List[Dict[str, Any]] = Field(default_factory=list)
    ground_truth: Dict[str, Any]
    outcome_classification: str
    tier: Optional[str] = None


class ExplainResponse(BaseModel):
    order_id: str
    explanation: str
    model_used: str
    source: str  # "llm" or "fallback_template"


def _classify_post_hoc(
    decision: str,
    risk_score: float,
    is_rto: int,
    outcome: str,
) -> tuple[str, str]:
    """Classifies the test case post-hoc based on actual scores, decision, and ground truth."""
    # 1. Adaptation gap: genuine miss (FN) or false positive insult (FP)
    if outcome == "FALSE_NEGATIVE_MISS" or (decision == "AUTO_APPROVE" and is_rto == 1):
        return (
            "Adaptation gap",
            f"Scored {risk_score:.2f}, below the 0.35 review cutoff and auto-approved, but actual ground truth was RTO -- represents an unflagged adaptation gap for residual mining.",
        )
    if outcome == "FALSE_POSITIVE_INSULT" or (decision == "AUTO_BLOCK" and is_rto == 0):
        return (
            "Adaptation gap",
            f"Scored {risk_score:.2f}, exceeding the 0.70 auto-block threshold, but actual buyer was legitimate (delivered) -- represents a false-positive insult risk.",
        )

    # 2. Borderline: routed to manual review or hovering within boundary threshold bands
    if decision == "MANUAL_REVIEW":
        if 0.65 <= risk_score <= 0.70:
            return (
                "Borderline",
                f"Scored {risk_score:.2f}, just under the 0.70 auto-block threshold -- a genuine boundary case routed to manual review.",
            )
        elif 0.35 <= risk_score <= 0.40:
            return (
                "Borderline",
                f"Scored {risk_score:.2f}, just crossing the 0.35 review cutoff -- an early boundary case routed to manual review.",
            )
        else:
            return (
                "Borderline",
                f"Scored {risk_score:.2f}, within the [0.35, 0.70] intermediate risk band -- routed to manual review queue for human investigation.",
            )

    if 0.30 <= risk_score < 0.35 and decision == "AUTO_APPROVE":
        return (
            "Borderline",
            f"Scored {risk_score:.2f}, near the 0.35 review threshold -- a borderline clean auto-approval.",
        )
    if 0.70 <= risk_score <= 0.75 and decision == "AUTO_BLOCK":
        return (
            "Borderline",
            f"Scored {risk_score:.2f}, just above the 0.70 auto-block threshold -- a borderline fraud auto-block.",
        )

    # 3. Clear pattern: high-confidence correct auto-decision far from threshold boundaries
    if decision == "AUTO_APPROVE" and is_rto == 0:
        return (
            "Clear pattern",
            f"Scored {risk_score:.2f}, far below any threshold (T=0.35) -- an unambiguous clean order correctly auto-approved.",
        )
    if decision == "AUTO_BLOCK" and is_rto == 1:
        return (
            "Clear pattern",
            f"Scored {risk_score:.2f}, comfortably above the 0.70 auto-block threshold -- an unambiguous high-confidence fraud case correctly blocked.",
        )

    return (
        "Clear pattern",
        f"Scored {risk_score:.2f} -- auto-decision ({decision}) aligned with ground truth.",
    )


def _build_fallback_explanation(
    classification: str,
    classification_reason: str,
    outcome: str,
    decision: str,
    risk: float,
    rules: List[Dict[str, Any]],
    features: Dict[str, Any],
    is_rto: int,
) -> str:
    """Generates a deterministic grounded fallback explanation incorporating post-hoc classification."""
    pay_mode = features.get("payment_mode", "UNKNOWN")
    order_val = features.get("order_value", 0.0)
    pincode_rate = features.get("pincode_rolling_rto_rate", 0.20)
    acc_age = features.get("customer_account_age_days", 30)

    if classification == "Adaptation gap":
        if outcome == "FALSE_NEGATIVE_MISS":
            return (
                f"This order represents an unflagged adaptation gap ({classification_reason}). "
                f"While ground-truth was RTO, the order scored low ambient risk ({risk:.2f}) under baseline heuristics (Payment: {pay_mode}, Account Age: {acc_age}d). "
                f"The Residual Miner isolates these unflagged misses to synthesize next-generation candidate defense agendas."
            )
        else:
            return (
                f"This order represents a false-positive margin risk ({classification_reason}). "
                f"The order (Value: ₹{order_val:,.2f}) matched risk heuristics with score {risk:.2f} and was AUTO_BLOCKED, but the customer was legitimate. "
                f"This incurs a 15% merchant margin insult loss (₹{order_val * 0.15:,.2f}), illustrating why high precision (T=0.70) is economically vital."
            )

    elif classification == "Borderline":
        return (
            f"This order is a borderline boundary case ({classification_reason}). "
            f"With a composite risk score of {risk:.2f} (Payment: {pay_mode}, Pincode RTO: {pincode_rate*100:.1f}%), "
            f"it was routed to the HUMAN MANUAL REVIEW queue to verify delivery address and customer intent without inflicting an automated false-positive insult."
        )

    else:  # Clear pattern
        if outcome == "CORRECT_BLOCK":
            rule_str = (
                f"triggered rule '{rules[0].get('rule_name', rules[0].get('rule_id', 'Risk Rule'))}'"
                if rules
                else "exceeded the high-risk threshold (T=0.70)"
            )
            return (
                f"This order exhibits a clear fraud pattern ({classification_reason}). "
                f"The transaction (Value: ₹{order_val:,.2f}, Payment: {pay_mode}, Account Age: {acc_age}d) {rule_str} "
                f"with a composite risk score of {risk:.2f}. The system correctly AUTO_BLOCKED this order, preventing verified RTO logistics loss (+₹250.00 saved)."
            )
        else:
            return (
                f"This order exhibits a clear legitimate buyer pattern ({classification_reason}). "
                f"With ambient risk score {risk:.2f} (< 0.35 threshold) and clean behavioral history (Payment: {pay_mode}, Account Age: {acc_age}d), "
                f"the system correctly AUTO_APPROVED the order for frictionless checkout with zero delivery loss."
            )


@router.get("/generate", response_model=OrderTestCaseResponse)
def generate_playground_test_case():
    """Samples uniformly at random from the full validation split pool (Days 56-75) and evaluates live ensemble routing."""
    df_val, val_dict, ensemble, router_inst = _get_resources()

    # Draw uniformly at random from the full validation dataset pool
    order_id = random.choice(list(val_dict.keys()))
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

    # Determine outcome
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

    # Compute post-hoc classification and dynamic reason
    classification, classification_reason = _classify_post_hoc(
        decision=decision.decision,
        risk_score=decision.risk_score,
        is_rto=is_rto,
        outcome=outcome,
    )

    # Clean feature dict for response
    feature_cols = [
        "order_id", "order_value", "payment_mode", "item_category",
        "customer_account_age_days", "customer_prior_orders", "pincode_rolling_rto_rate",
        "promo_code_used", "device_order_count_24h", "order_hour", "day_index",
    ]
    clean_features = {
        k: (float(order_row[k]) if isinstance(order_row[k], (float, int)) and not isinstance(order_row[k], bool) and k not in ("customer_prior_orders", "customer_account_age_days", "day_index", "order_hour") else order_row[k])
        for k in feature_cols if k in order_row
    }

    # Generate quick default explanation
    default_expl = _build_fallback_explanation(
        classification=classification,
        classification_reason=classification_reason,
        outcome=outcome,
        decision=decision.decision,
        risk=decision.risk_score,
        rules=[r.model_dump() for r in matched_rule_details],
        features=clean_features,
        is_rto=is_rto,
    )

    tier_key = classification.lower().replace(" ", "_")

    return OrderTestCaseResponse(
        order_id=order_id,
        classification=classification,
        classification_reason=classification_reason,
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
        dataset_split="validation",
        split_description="Validation Split (Days 56–75, strictly non-held-out)",
        explanation=default_expl,
        tier=tier_key,
        tier_label=classification,
    )


@router.post("/explain", response_model=ExplainResponse)
def explain_order_decision(payload: ExplainRequest):
    """Generates a natural-language explanation via LLM strictly grounded in order features, rules, post-hoc classification, and ground truth."""
    rules_text = "\n".join([f"- {r.get('rule_name', r.get('rule_id'))}: {r.get('rule_code', '')}" for r in payload.matched_rules]) if payload.matched_rules else "No active rules matched (ambient baseline risk only)."
    
    is_rto = int(payload.ground_truth.get("is_rto", 0))
    gt_label = "RTO (Buyer refused/returned order)" if is_rto == 1 else "DELIVERED (Successful delivery)"
    classification = payload.classification or "Analyzed Case"
    classification_reason = payload.classification_reason or ""

    miss_rule = (
        '3. CRITICAL: For this unflagged miss (Adaptation Gap), explicitly frame the explanation around the adaptation gap: '
        '"this is a deceptive order representing the adaptation gap this system is designed to close over time via Residual Mining" '
        'rather than a bare system failure.\n'
        if payload.outcome_classification == 'FALSE_NEGATIVE_MISS'
        else ''
    )
    fp_rule = (
        '3. CRITICAL: For this FALSE POSITIVE case, explicitly frame the explanation around the honest cost-tradeoff: '
        'the order triggered risk heuristics resulting in an auto-block, incurring a 15% merchant gross margin loss insult cost, '
        'illustrating why high precision (T=0.70) is economically vital.\n'
        if payload.outcome_classification == 'FALSE_POSITIVE_INSULT'
        else ''
    )

    prompt = (
        f"You are the Aegis-RTO Explanation Agent. Provide a concise (2-3 sentences), highly factual explanation for how and why Aegis routed this transaction.\n\n"
        f"STRICT GROUNDING RULES:\n"
        f"1. Reason ONLY using the provided order features, matched rule(s), routing decision, post-hoc classification, and ground truth below. Do not invent details.\n"
        f"2. Reference key numeric values (e.g. order value, payment mode, account age, risk score) that justified the outcome.\n"
        f"3. Incorporate the post-hoc classification ({classification}: {classification_reason}).\n"
        f"{miss_rule}"
        f"{fp_rule}\n"
        f"ORDER CONTEXT:\n"
        f"- Order ID: {payload.order_id}\n"
        f"- Post-Hoc Classification: {classification}\n"
        f"- Classification Reason: {classification_reason}\n"
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
        classification=classification,
        classification_reason=classification_reason,
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
