import numpy as np
import pandas as pd
from app.data.loader import load_train_data, load_validation_data

df_tr = load_train_data()
df_val = load_validation_data()

# Compute cost impact function
# Avoided RTO loss = TP * 250
# FP Insult cost = sum(FP order_value * 0.15)
# Net = Avoided - FP Insult

y_tr = df_tr["is_rto"].values
ov_tr = df_tr["order_value"].values
cod_tr = (df_tr["payment_mode"] == "COD").values
pincode_tr = df_tr["pincode_rolling_rto_rate"].values
prior_tr = df_tr["customer_prior_orders"].values
age_tr = df_tr["customer_account_age_days"].values
first_tr = df_tr["is_first_time_customer"].values

y_val = df_val["is_rto"].values
ov_val = df_val["order_value"].values
cod_val = (df_val["payment_mode"] == "COD").values
pincode_val = df_val["pincode_rolling_rto_rate"].values
prior_val = df_val["customer_prior_orders"].values
age_val = df_val["customer_account_age_days"].values
first_val = df_val["is_first_time_customer"].values

results = []

for p_min in [0.38, 0.40, 0.42, 0.45, 0.48, 0.50, 0.52, 0.55]:
    for max_v in [1000, 1200, 1400, 1500, 1600, 1800, 2000, 2500]:
        for prior_max in [0, 1, 2, 999]:
            for first_req in [True, False, None]:
                m_tr = cod_tr & (pincode_tr >= p_min) & (ov_tr <= max_v)
                m_val = cod_val & (pincode_val >= p_min) & (ov_val <= max_v)
                
                if prior_max < 999:
                    m_tr &= (prior_tr <= prior_max)
                    m_val &= (prior_val <= prior_max)
                if first_req is not None:
                    m_tr &= (first_tr == first_req)
                    m_val &= (first_val == first_req)
                
                tp_tr = np.sum(m_tr & (y_tr == 1))
                fp_tr = np.sum(m_tr & (y_tr == 0))
                flags_tr = tp_tr + fp_tr
                
                if flags_tr >= 15:
                    insult_tr = np.sum(ov_tr[m_tr & (y_tr == 0)] * 0.15)
                    net_tr = tp_tr * 250.0 - insult_tr
                    
                    if net_tr > 200.0:
                        tp_val = np.sum(m_val & (y_val == 1))
                        fp_val = np.sum(m_val & (y_val == 0))
                        flags_val = tp_val + fp_val
                        insult_val = np.sum(ov_val[m_val & (y_val == 0)] * 0.15) if flags_val > 0 else 0.0
                        net_val = tp_val * 250.0 - insult_val
                        
                        prec_tr = tp_tr / flags_tr
                        prec_val = (tp_val / flags_val) if flags_val > 0 else 0.0
                        rec_tr = tp_tr / np.sum(y_tr == 1)
                        rec_val = (tp_val / np.sum(y_val == 1)) if flags_val > 0 else 0.0
                        
                        results.append({
                            "net_tr": net_tr,
                            "net_val": net_val,
                            "prec_tr": prec_tr,
                            "prec_val": prec_val,
                            "rec_tr": rec_tr,
                            "rec_val": rec_val,
                            "flags_tr": int(flags_tr),
                            "flags_val": int(flags_val),
                            "tp_tr": int(tp_tr),
                            "fp_tr": int(fp_tr),
                            "p_min": p_min,
                            "max_v": max_v,
                            "prior_max": prior_max,
                            "first_req": first_req,
                        })

results.sort(key=lambda x: x["net_tr"], reverse=True)
print(f"Found {len(results)} rules with positive train net savings.")
for r in results[:15]:
    print(
        f"Train: Net=+Rs {r['net_tr']:7.2f} (Prec: {r['prec_tr']*100:4.1f}%, Rec: {r['rec_tr']*100:4.1f}%, Flags: {r['flags_tr']:3d}) | "
        f"Val: Net=Rs {r['net_val']:7.2f} (Prec: {r['prec_val']*100:4.1f}%, Rec: {r['rec_val']*100:4.1f}%, Flags: {r['flags_val']:3d}) | "
        f"pincode>={r['p_min']}, val<={r['max_v']}, prior<={r['prior_max']}, first={r['first_req']}"
    )
