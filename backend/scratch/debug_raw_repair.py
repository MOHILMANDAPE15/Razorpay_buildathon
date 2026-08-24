from app.core.llm import get_llm_client
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.prompts import REPAIR_SYSTEM_PROMPT

llm = get_llm_client(temperature=0.1)

broken_code = """
def predict(df):
    # Syntax error: unclosed parenthesis
    return (df['payment_mode'] == 'COD' & (df['order_value'] > 1000)
"""
error_msg = "SyntaxError: '(' was never closed"

prompt = f"""The following fraud rule code produced an error during sandboxed validation:

BROKEN CODE:
```python
{broken_code}
```

ERROR ENCOUNTERED:
{error_msg}

Please repair the code. Fix any syntax errors, undefined variables, or invalid column names.
Ensure it defines `def predict(df: pd.DataFrame)` returning boolean / 0-1 array.
"""

res = llm.invoke([SystemMessage(content=REPAIR_SYSTEM_PROMPT), HumanMessage(content=prompt)])
print("RAW LLM OUTPUT:\n" + "="*50)
print(res.content.encode('ascii', errors='replace').decode('ascii'))
