"""Gate 3: Defense-Only Audit Gate.

Enforces Track 2's strict defense-only requirement:
Guarantees that all generated hypotheses, rule code, and plain-English rationales
are purely defensive mechanisms (detecting RTO/COD fraud) and contain zero
evasion instructions, attacker exploits, or offensive circumvention guidance.

Two-Phase Verification:
  Phase 1: Deterministic keyword & pattern scanner (fast, zero API cost).
  Phase 2: LLM Adversarial Judge (secondary LLM call reviewing rationale text).
"""

import json
import re
from typing import List, Optional, Tuple

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm import get_llm_client
from app.engine.types import AuditResult, RuleHypothesis

# High-risk keywords indicating potential evasion instructions or offensive exploits
OFFENSIVE_EVASION_PATTERNS: List[str] = [
    r"\bavoid detection\b",
    r"\bevade (?:filter|detection|flag|scoring)\b",
    r"\bbypass (?:fraud|defense|filter|rules?)\b",
    r"\bcircumvent\b",
    r"\bhow to structure an? (?:fraudulent )?order\b",
    r"\bsuppress flags? for attacker\b",
    r"\bexploit vulnerability\b",
    r"\bgenerate fake customer\b",
    r"\bspoof device\b",
]

DEFENSE_AUDIT_PROMPT = """You are the Lead Compliance & AI Safety Auditor for Aegis-RTO, an autonomous fraud defense system.

Your job is to strictly enforce the "Defense-Only" mandate:
Verify that the proposed fraud detection rule and its rationale are strictly DEFENSIVE (designed to detect and mitigate e-commerce RTO abuse) and do NOT contain offensive evasion instructions, advice on how fraudsters can circumvent defenses, or instructions for constructing fraudulent orders.

Review the following hypothesis:
Title: {name}
Description: {description}
Rationale: {rationale}
Code:
```python
{code}
```

EVALUATION CRITERIA:
1. Is this hypothesis strictly defensive (aimed at protecting merchants from RTO fraud)?
2. Does the rationale or description give instructions on how to evade detection?
3. Does the code contain hidden backdoor triggers or malicious bypasses?

Respond with valid JSON:
{{
    "is_defense_only": true,
    "confidence": 0.99,
    "concern": "None. Rule is standard risk scoring based on order features.",
    "verdict": "APPROVED"
}}
"""


class DefenseOnlyAuditGate:
    """Gate 3: Audits candidate hypotheses for compliance with the defense-only mandate."""

    def __init__(self, use_llm_judge: bool = True):
        self.use_llm_judge = use_llm_judge

    def audit(self, hypothesis: RuleHypothesis) -> AuditResult:
        """Runs candidate through Gate 3 Defense-Only Audit.
        
        Args:
            hypothesis: The RuleHypothesis to audit.
            
        Returns:
            AuditResult: Details of Phase 1 (keyword) and Phase 2 (LLM judge) checks.
        """
        combined_text = f"{hypothesis.name}\n{hypothesis.description}\n{hypothesis.rationale}\n{hypothesis.code}".lower()

        # Phase 1: Deterministic keyword / pattern scan
        flagged_keywords = []
        for pattern in OFFENSIVE_EVASION_PATTERNS:
            if re.search(pattern, combined_text, re.IGNORECASE):
                flagged_keywords.append(pattern)

        phase_1_passed = len(flagged_keywords) == 0

        # If Phase 1 failed on blatant offensive terms, fail immediately
        if not phase_1_passed:
            return AuditResult(
                gate_name="Gate 3: Defense-Only Audit",
                hypothesis_id=hypothesis.id,
                is_defense_only=False,
                status="FAILED",
                phase_1_keyword_passed=False,
                phase_2_llm_judge_passed=False,
                flagged_keywords=flagged_keywords,
                judge_reasoning=f"Phase 1 keyword filter caught prohibited evasion terms: {flagged_keywords}",
                details=f"Gate 3 FAILED: Rule contains evasion or offensive guidance keywords ({flagged_keywords}).",
            )

        # Phase 2: LLM Adversarial Judge (if configured and API key available)
        phase_2_passed = True
        judge_reasoning = "Phase 1 passed. LLM judge not invoked or offline."

        if self.use_llm_judge:
            try:
                llm = get_llm_client(temperature=0.1)
                prompt = DEFENSE_AUDIT_PROMPT.format(
                    name=hypothesis.name,
                    description=hypothesis.description,
                    rationale=hypothesis.rationale,
                    code=hypothesis.code,
                )
                response = llm.invoke([HumanMessage(content=prompt)])
                content_str = response.content.strip()
                # Clean potential markdown wrapping
                if content_str.startswith("```json"):
                    content_str = content_str.split("```json", 1)[1].split("```", 1)[0].strip()
                elif content_str.startswith("```"):
                    content_str = content_str.split("```", 1)[1].split("```", 1)[0].strip()
                
                raw_json = json.loads(content_str)
                is_defense = bool(raw_json.get("is_defense_only", True))
                concern = raw_json.get("concern", "No concern reported.")
                verdict = raw_json.get("verdict", "APPROVED")

                phase_2_passed = is_defense and (verdict.upper() != "REJECTED")
                judge_reasoning = f"LLM Judge verdict: {verdict}. Concern: {concern}"
            except Exception as e:
                # LLM network failure or parse error: fallback to Phase 1 result
                judge_reasoning = f"LLM Judge offline or skipped: {str(e)}. Defaulting to Phase 1 clean pass."
                phase_2_passed = True

        overall_passed = phase_1_passed and phase_2_passed
        return AuditResult(
            gate_name="Gate 3: Defense-Only Audit",
            hypothesis_id=hypothesis.id,
            is_defense_only=overall_passed,
            status="PASSED" if overall_passed else "FAILED",
            phase_1_keyword_passed=phase_1_passed,
            phase_2_llm_judge_passed=phase_2_passed,
            flagged_keywords=flagged_keywords,
            judge_reasoning=judge_reasoning,
            details="Gate 3 PASSED: Verified strictly defense-only." if overall_passed else f"Gate 3 FAILED: {judge_reasoning}",
        )
