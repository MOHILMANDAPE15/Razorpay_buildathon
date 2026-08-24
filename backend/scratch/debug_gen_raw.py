import pandas as pd
from app.core.llm import get_llm_client
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.prompts import GENERATOR_SYSTEM_PROMPT

llm = get_llm_client(temperature=0.7)

user_prompt = """You are currently exploring Round 1.
Notepad Context / Prior Discoveries:
Cold start round. No prior hypotheses evaluated yet. Begin exploration across diverse signals.

You have access to these columns (described in your system prompt). Use any combination of them. Do not assume which columns are important - discover that from reasoning about e-commerce fraud dynamics and the column semantics.

Respond with a JSON array containing 2 rule objects.
"""

res = llm.invoke([SystemMessage(content=GENERATOR_SYSTEM_PROMPT), HumanMessage(content=user_prompt)])
print("RAW LLM OUTPUT:\n" + "="*50)
print(res.content.encode('ascii', errors='replace').decode('ascii'))
