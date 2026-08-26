"""Hypothesis Reflector Agent for diagnosing rule failures and synthesizing mutated rules."""

import json
import re
import uuid
from typing import Optional
import pandas as pd
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm import get_llm_client, extract_response_text
from app.core.sandbox import validate_rule_code, execute_rule_sandboxed
from app.agents.prompts import REFLECTOR_SYSTEM_PROMPT
from app.agents.repair import repair_rule_code
from app.engine.types import EvaluationReport, RuleHypothesis


class HypothesisReflector:
    """Diagnoses misclassified orders from Evaluator reports and formulates targeted mutations."""

    def __init__(self, llm: Optional[BaseChatModel] = None):
        self.llm = llm or get_llm_client(temperature=0.6)

    def reflect_and_mutate(
        self,
        parent_hypothesis: RuleHypothesis,
        eval_report: EvaluationReport,
        generation_round: int = 2,
        df_sample: Optional[pd.DataFrame] = None,
    ) -> Optional[RuleHypothesis]:
        """Diagnoses why parent_hypothesis failed and produces an evolved, mutated child hypothesis.
        
        Args:
            parent_hypothesis: The parent RuleHypothesis that was evaluated.
            eval_report: EvaluationReport containing precision, recall, net savings, and top failure cases.
            generation_round: Current round number.
            df_sample: Optional sample dataframe for validation & repair.
            
        Returns:
            Optional[RuleHypothesis]: The mutated child hypothesis, or None if mutation failed.
        """
        if not eval_report.is_valid or eval_report.standard_metrics is None or eval_report.cost_metrics is None:
            return None

        sm = eval_report.standard_metrics
        cm = eval_report.cost_metrics

        # Format concrete failure cases
        fps_formatted = [
            {
                "order_id": fp.order_id,
                "order_value": fp.order_value,
                "merchant_profit_lost": fp.cost_impact_inr,
                "key_features": {
                    k: v for k, v in fp.features.items()
                    if k in ["payment_mode", "customer_prior_orders", "order_value", "pincode_rolling_rto_rate", "promo_code_used", "device_order_count_24h", "order_hour"]
                }
            }
            for fp in eval_report.top_false_positives[:4]
        ]

        fns_formatted = [
            {
                "order_id": fn.order_id,
                "order_value": fn.order_value,
                "missed_rto_loss": fn.cost_impact_inr,
                "key_features": {
                    k: v for k, v in fn.features.items()
                    if k in ["payment_mode", "customer_prior_orders", "order_value", "pincode_rolling_rto_rate", "promo_code_used", "device_order_count_24h", "order_hour"]
                }
            }
            for fn in eval_report.top_false_negatives[:4]
        ]

        user_prompt = f"""EVALUATION AUDIT FOR PARENT RULE [{parent_hypothesis.id}]: '{parent_hypothesis.name}'

CURRENT RULE CODE:
```python
{parent_hypothesis.code}
```

METRICS SUMMARY:
- Precision: {sm.precision*100:.1f}% | Recall: {sm.recall*100:.1f}% | F1: {sm.f1:.3f}
- True Positives (Caught): {sm.true_positives}
- False Alarms (Wrongly Blocked): {sm.false_positives} (Total Profit Burned: ₹{cm.false_positive_insult_cost_inr:,.2f})
- Missed Frauds: {sm.false_negatives}
- Net Financial Impact: ₹{cm.net_financial_savings_inr:,.2f}

TOP FALSE ALARMS (Genuine customers wrongly blocked):
{json.dumps(fps_formatted, indent=2)}

TOP MISSED FRAUDS (Uncaught fraud loss events):
{json.dumps(fns_formatted, indent=2)}

DIAGNOSIS & MUTATION TASK:
1. Identify the specific structural flaw in the parent rule that caused these false alarms or missed frauds.
2. Formulate a mutated Python rule `predict(df)` that fixes the flaw (e.g., adding multi-factor checks, combining promo + device signals, or exempting safe loyal buyers).
3. Return valid JSON adhering to the required schema.
"""

        messages = [
            SystemMessage(content=REFLECTOR_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = self.llm.invoke(messages)
            raw_content = extract_response_text(response)
        except Exception as e:
            print(f"[Reflector] LLM invocation failed: {e}")
            return None

        parsed_data = self._parse_json_response(raw_content)
        if not parsed_data:
            # Fallback: extract code directly from raw text
            code_match = re.search(r"```(?:python)?\s*(def predict[\s\S]*?)(?:```|\Z)", raw_content)
            if code_match:
                parsed_data = {
                    "mutated_rule_name": f"Mutated {parent_hypothesis.name}",
                    "mutated_code": code_match.group(1).strip(),
                    "diagnosis": "Direct code extraction",
                    "mutation_strategy": "Direct code mutation",
                }
            elif "def predict(" in raw_content:
                start_idx = raw_content.find("def predict(")
                code_text = raw_content[start_idx:].strip()
                if "```" in code_text:
                    code_text = code_text[:code_text.find("```")].strip()
                parsed_data = {
                    "mutated_rule_name": f"Mutated {parent_hypothesis.name}",
                    "mutated_code": code_text,
                    "diagnosis": "Direct code extraction",
                    "mutation_strategy": "Direct code mutation",
                }
            else:
                return None

        mutated_name = (
            parsed_data.get("mutated_rule_name")
            or parsed_data.get("name")
            or parsed_data.get("rule_name")
            or parsed_data.get("title")
            or f"Mutated {parent_hypothesis.name}"
        )
        mutated_code = (
            parsed_data.get("mutated_code")
            or parsed_data.get("code")
            or parsed_data.get("mutated_rule_code")
            or parsed_data.get("rule_code")
            or parsed_data.get("rule")
            or ""
        )
        diagnosis = parsed_data.get("diagnosis", "")
        strategy = parsed_data.get("mutation_strategy", "")

        # Clean markdown fences from inside string if present
        if "```" in mutated_code:
            code_clean = re.search(r"(?:```(?:python)?\s*)?(def predict\(.*?)(?:```|$)", mutated_code, re.DOTALL)
            if code_clean:
                mutated_code = code_clean.group(1).strip()

        if not mutated_code or "def predict(" not in mutated_code:
            return None

        # Validate & Repair if needed
        is_valid = True
        try:
            validate_rule_code(mutated_code)
            if df_sample is not None and not df_sample.empty:
                execute_rule_sandboxed(mutated_code, df_sample, timeout_sec=2.0)
        except Exception as exc:
            if df_sample is not None and not df_sample.empty:
                success, repaired_code, _ = repair_rule_code(
                    broken_code=mutated_code,
                    error_message=str(exc),
                    df_sample=df_sample,
                    llm=self.llm,
                )
                if success:
                    mutated_code = repaired_code
                else:
                    is_valid = False
            else:
                is_valid = False

        if not is_valid:
            return None

        child_id = f"hyp_r{generation_round}_mut_{uuid.uuid4().hex[:4]}"
        return RuleHypothesis(
            id=child_id,
            name=mutated_name,
            code=mutated_code,
            description=f"Mutated from {parent_hypothesis.id}. Strategy: {strategy[:120]}",
            rationale=f"Diagnosis: {diagnosis[:200]} | Strategy: {strategy[:200]}",
            target_signal=parent_hypothesis.target_signal or "mutated_composite",
            generation_round=generation_round,
            parent_ids=[parent_hypothesis.id],
            status="candidate",
        )

    def _parse_json_response(self, text: str) -> Optional[dict]:
        """Parses reflection JSON output.
        Note: think-tag stripping handled upstream by extract_response_text().
        """
        try:
            data = json.loads(text.strip())
            if isinstance(data, dict):
                return data
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                return data[0]
        except Exception:
            pass

        # Extract markdown JSON block
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except Exception:
                pass

        # Fallback: search for first { and matching }
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except Exception:
                pass

        return None
