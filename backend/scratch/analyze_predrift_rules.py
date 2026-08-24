"""Analyze authentic pre-drift rules that have positive train net savings and degrade on validation drift."""

import pandas as pd
import numpy as np
from app.data.loader import load_train_data, load_validation_data
from app.engine.evaluator import CostWeightedEvaluator

df_tr = load_train_data()
df_val = load_validation_data()
ev = CostWeightedEvaluator()

print("Train shape:", df_tr.shape, "Train RTOs:", df_tr["is_rto"].sum())
print("Validation shape:", df_val.shape, "Val RTOs:", df_val["is_rto"].sum())

# Explore clean pre-drift features:
# payment_mode == 'COD', pincode_rolling_rto_rate, customer_account_age_days, customer_prior_orders, is_first_time_customer, order_value, item_category

candidates = []

# Candidate 1: High pincode risk COD with first-time/new customers
c1 = (df_tr["payment_mode"] == "COD") & (df_tr["pincode_rolling_rto_rate"] > 0.45) & (df_tr["is_first_time_customer"] == True)
candidates.append(("Pincode Risk COD First-Time", c1, lambda df: (df["payment_mode"] == "COD") & (df["pincode_rolling_rto_rate"] > 0.45) & (df["is_first_time_customer"] == True)))

# Candidate 2: High pincode risk COD with low account age
c2 = (df_tr["payment_mode"] == "COD") & (df_tr["pincode_rolling_rto_rate"] > 0.40) & (df_tr["customer_account_age_days"] < 30) & (df_tr["order_value"] < 3000)
candidates.append(("Pincode Risk COD New Account Capped Value", c2, lambda df: (df["payment_mode"] == "COD") & (df["pincode_rolling_rto_rate"] > 0.40) & (df["customer_account_age_days"] < 30) & (df["order_value"] < 3000)))

# Candidate 3: High pincode risk with zero prior orders
c3 = (df_tr["payment_mode"] == "COD") & (df_tr["pincode_rolling_rto_rate"] > 0.42) & (df_tr["customer_prior_orders"] == 0) & (df_tr["order_value"] < 3500)
candidates.append(("Pincode Risk COD Zero Prior Orders", c3, lambda df: (df["payment_mode"] == "COD") & (df["pincode_rolling_rto_rate"] > 0.42) & (df["customer_prior_orders"] == 0) & (df["order_value"] < 3500)))

# Candidate 4: Moderate-High pincode risk in high RTO categories
c4 = (df_tr["payment_mode"] == "COD") & (df_tr["pincode_rolling_rto_rate"] > 0.38) & (df_tr["item_category"].isin(["Footwear", "Apparel", "Electronics"])) & (df_tr["order_value"] < 2500)
candidates.append(("Pincode Risk COD High Risk Categories", c4, lambda df: (df["payment_mode"] == "COD") & (df["pincode_rolling_rto_rate"] > 0.38) & (df["item_category"].isin(["Footwear", "Apparel", "Electronics"])) & (df["order_value"] < 2500)))

for name, mask, fn in candidates:
    r_tr = ev.evaluate_flags(mask.values, df_tr, name, name)
    r_val = ev.evaluate_flags(fn(df_val).values, df_val, name, name)
    print(f"\n--- {name} ---")
    print(f"  Train: Flagged={r_tr.standard_metrics.flagged_orders:3d} (TP={r_tr.standard_metrics.true_positives:2d}, FP={r_tr.standard_metrics.false_positives:2d}) | Prec={r_tr.standard_metrics.precision*100:5.1f}% | Rec={r_tr.standard_metrics.recall*100:4.1f}% | Net=Rs. {r_tr.cost_metrics.net_financial_savings_inr:,.2f}")
    print(f"  Val:   Flagged={r_val.standard_metrics.flagged_orders:3d} (TP={r_val.standard_metrics.true_positives:2d}, FP={r_val.standard_metrics.false_positives:2d}) | Prec={r_val.standard_metrics.precision*100:5.1f}% | Rec={r_val.standard_metrics.recall*100:4.1f}% | Net=Rs. {r_val.cost_metrics.net_financial_savings_inr:,.2f}")
