from app.agents.repair import repair_rule_code
from app.data.loader import load_train_data

df = load_train_data().head(10)
code = """
def predict(df):
    return (df['payment_mode'] == 'COD' & (df['order_value'] > 1000)
"""

success, rep_code, exp = repair_rule_code(code, "SyntaxError: '(' was never closed", df)
print("Success:", success)
print("Repaired Code:\n", rep_code)
print("Explanation:", exp)
