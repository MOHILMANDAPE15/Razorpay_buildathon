"""Hypothesis Generator Agent for synthesizing executable fraud detection rules."""

import json
import re
import uuid
from typing import List, Optional
import pandas as pd
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm import get_llm_client, extract_response_text
from app.core.sandbox import validate_rule_code, execute_rule_sandboxed
from app.agents.prompts import GENERATOR_SYSTEM_PROMPT
from app.agents.repair import repair_rule_code
from app.engine.types import RuleHypothesis


class HypothesisGenerator:
    """Generates candidate fraud detection rules informed by schema and notepad history."""

    def __init__(self, llm: Optional[BaseChatModel] = None):
        self.llm = llm or get_llm_client(temperature=0.7)

    def generate_hypotheses(
        self,
        n_hypotheses: int = 2,
        notepad_summary: str = "",
        generation_round: int = 1,
        df_sample: Optional[pd.DataFrame] = None,
        miss_agenda: Optional[str] = None,
    ) -> List[RuleHypothesis]:
        """Proposes N new executable fraud hypotheses.
        
        Args:
            n_hypotheses: Number of distinct candidate rules to generate.
            notepad_summary: Memory summary of past successes and failures.
            generation_round: Current round number.
            df_sample: Optional sample dataframe for validation & repair.
            miss_agenda: Optional targeted agenda from ResidualMiner.
            
        Returns:
            List[RuleHypothesis]: Validated candidate rule hypotheses.
        """
        targeted_section = ""
        if miss_agenda:
            targeted_section = f"\n\nRESIDUAL MINER TARGETED AGENDA:\n{miss_agenda}\nFocus your rules on capturing this specific missed abuse pattern without over-flagging genuine customers."

        user_prompt = f"""Generation Round: {generation_round}

{notepad_summary}{targeted_section}

TASK:
You are analyzing Indian e-commerce COD (Cash on Delivery) order data where some orders result in RTO — Return-To-Origin. RTO occurs when a package is shipped but never delivered: the customer refuses, is absent, or the order was fraudulent. Each undelivered COD order causes direct logistics and restocking loss.

Your objective is to propose {n_hypotheses} DIVERSE candidate fraud detection rules. Each rule must flag different order patterns — do not propose rules that look for the same signal. Reason from the available data columns to find patterns that distinguish genuine orders from high-risk ones.

You have access to these columns (described in your system prompt). Use any combination of them. Do not assume which columns are important — discover that from reasoning about e-commerce fraud dynamics and the column semantics.

Respond with a JSON array containing {n_hypotheses} rule objects.
"""

        messages = [
            SystemMessage(content=GENERATOR_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = self.llm.invoke(messages)
            raw_content = extract_response_text(response)
        except Exception as e:
            print(f"[Generator] LLM invocation failed: {e}")
            return []

        parsed_items = self._parse_json_response(raw_content)
        valid_hypotheses: List[RuleHypothesis] = []

        for idx, item in enumerate(parsed_items):
            hyp_id = f"hyp_r{generation_round}_{idx+1}_{uuid.uuid4().hex[:4]}"
            name = item.get("name", f"Rule {hyp_id}")
            code = item.get("code", "")
            desc = item.get("description", "")
            rationale = item.get("rationale", "")
            target_signal = item.get("target_signal", "general")

            if not code or "def predict(" not in code:
                continue

            # Validate & Repair if needed
            is_valid = True
            try:
                validate_rule_code(code)
                if df_sample is not None and not df_sample.empty:
                    execute_rule_sandboxed(code, df_sample, timeout_sec=2.0)
            except Exception as exc:
                if df_sample is not None and not df_sample.empty:
                    success, repaired_code, _ = repair_rule_code(
                        broken_code=code,
                        error_message=str(exc),
                        df_sample=df_sample,
                        llm=self.llm,
                    )
                    if success:
                        code = repaired_code
                    else:
                        is_valid = False
                else:
                    is_valid = False

            if is_valid:
                valid_hypotheses.append(
                    RuleHypothesis(
                        id=hyp_id,
                        name=name,
                        code=code,
                        description=desc,
                        rationale=rationale,
                        target_signal=target_signal,
                        generation_round=generation_round,
                        parent_ids=[],
                        status="candidate",
                    )
                )

        return valid_hypotheses

    def _parse_json_response(self, text: str) -> List[dict]:
        """Robust parser for LLM JSON arrays and single objects."""
        # Note: think-tag stripping and Gemini list-content normalization
        # is handled upstream in extract_response_text(). Input is plain text.

        # Sanitize unicode quotes
        text = (
            text.replace("\u2011", "-")
            .replace("\u2013", "-")
            .replace("\u2014", "-")
            .replace("\u2018", "'")
            .replace("\u2019", "'")
            .replace("\u201c", '"')
            .replace("\u201d", '"')
        )

        # 1. Direct parse
        try:
            data = json.loads(text.strip())
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return [data]
        except Exception:
            pass

        # 2. Extract markdown JSON block
        matches = re.findall(r"```(?:json)?\s*([\[\{][\s\S]*?[\]\}])\s*```", text)
        for m in matches:
            try:
                data = json.loads(m)
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    return [data]
            except Exception:
                continue

        # 3. Fallback: regex search for bracketed array
        array_match = re.search(r"\[\s*\{[\s\S]*?\}\s*\]", text)
        if array_match:
            try:
                data = json.loads(array_match.group(0))
                if isinstance(data, list):
                    return data
            except Exception:
                pass

        # 4. Fallback: extract individual JSON objects
        obj_matches = re.finditer(r"\{[\s\S]*?\}", text)
        results = []
        for om in obj_matches:
            try:
                obj = json.loads(om.group(0))
                if isinstance(obj, dict) and ("code" in obj or "name" in obj):
                    results.append(obj)
            except Exception:
                continue
        if results:
            return results

        # 5. Fallback: extract any python def predict(df) functions directly
        func_matches = re.findall(r"(def predict\s*\([^)]*\):[\s\S]*?)(?=(?:def predict|\Z))", text)
        if func_matches:
            for idx, func in enumerate(func_matches):
                cleaned = re.sub(r"```.*", "", func).strip()
                if cleaned:
                    results.append({
                        "name": f"Generated Rule {idx+1}",
                        "code": cleaned,
                        "description": "Extracted rule function",
                        "rationale": "Direct rule extraction",
                        "target_signal": "general_risk",
                    })
            return results

        return []
