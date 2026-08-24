import pandas as pd
from app.agents.generator import HypothesisGenerator

df = pd.DataFrame({
    "order_id": ["ORD01", "ORD02", "ORD03", "ORD04"],
    "customer_id": ["CUST01", "CUST02", "CUST03", "CUST04"],
    "order_value": [1000.0, 4500.0, 2000.0, 12000.0],
    "payment_mode": ["COD", "COD", "Prepaid", "COD"],
    "is_first_time_customer": [True, True, False, True],
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

import pandas as pd
gen = HypothesisGenerator()
candidates = gen.generate_hypotheses(
    n_hypotheses=2,
    notepad_summary="Cold start round",
    generation_round=1,
    df_sample=df,
)
print("Returned candidates:", len(candidates))
for c in candidates:
    print(c.name, ":", c.code)
