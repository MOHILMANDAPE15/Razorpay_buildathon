"""Code repair handler for fixing syntax errors and sandbox violations in generated rules."""

import json
import re
from typing import Optional, Tuple
import pandas as pd
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm import get_llm_client
from app.core.sandbox import execute_rule_sandboxed, validate_rule_code
from app.agents.prompts import REPAIR_SYSTEM_PROMPT


def _extract_code_from_response(text: str) -> Tuple[str, str]:
    """Extracts python code and explanation from JSON or markdown code blocks."""
    # Attempt 1: Parse direct JSON
    try:
        data = json.loads(text.strip())
        if isinstance(data, dict) and "repaired_code" in data:
            return data["repaired_code"], data.get("explanation", "Repaired via JSON response")
    except Exception:
        pass

    # Attempt 2: Extract JSON from markdown fences ```json ... ```
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            if isinstance(data, dict) and "repaired_code" in data:
                return data["repaired_code"], data.get("explanation", "Repaired via JSON block")
        except Exception:
            pass

    # Attempt 3: Extract python code from ```python ... ``` fences
    code_match = re.search(r"```(?:python)?\s*(def predict[\s\S]*?)(?:```|\Z)", text)
    if code_match:
        return code_match.group(1).strip(), "Extracted from Python code block"

    # Attempt 4: Search for def predict
    if "def predict(" in text:
        start_idx = text.find("def predict(")
        code_text = text[start_idx:].strip()
        if "```" in code_text:
            code_text = code_text[:code_text.find("```")].strip()
        return code_text, "Extracted from raw text"

    return text.strip(), "Raw response"


def repair_rule_code(
    broken_code: str,
    error_message: str,
    df_sample: pd.DataFrame,
    llm: Optional[BaseChatModel] = None,
) -> Tuple[bool, str, str]:
    """Attempts to automatically repair broken rule code using the LLM with error feedback.
    
    Args:
        broken_code: The Python code that failed.
        error_message: The exception traceback or error reason.
        df_sample: A small sample DataFrame to test the repaired code on.
        llm: Optional LangChain chat model.
        
    Returns:
        Tuple[bool, str, str]:
            - success (bool): True if repaired code runs cleanly.
            - code (str): Repaired code or original if repair failed.
            - explanation (str): Explanation of repair or failure reason.
    """
    model = llm or get_llm_client(temperature=0.2)

    prompt_content = f"""The following fraud rule code produced an error during sandboxed validation:

BROKEN CODE:
```python
{broken_code}
```

ERROR ENCOUNTERED:
{error_message}

Please repair the code. Fix any syntax errors, undefined variables, or invalid column names.
Ensure it defines `def predict(df: pd.DataFrame)` returning boolean / 0-1 array.
"""

    messages = [
        SystemMessage(content=REPAIR_SYSTEM_PROMPT),
        HumanMessage(content=prompt_content),
    ]

    try:
        response = model.invoke(messages)
        repaired_code, explanation = _extract_code_from_response(response.content)

        # Validate repaired code
        validate_rule_code(repaired_code)
        
        # Test execution on sample dataframe
        execute_rule_sandboxed(repaired_code, df_sample, timeout_sec=2.0)
        
        return True, repaired_code, explanation

    except Exception as e:
        return False, broken_code, f"Repair attempt failed: {str(e)}"
