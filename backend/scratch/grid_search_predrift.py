import pandas as pd
from app.data.loader import load_train_data, load_validation_data
from app.engine.evaluator import CostWeightedEvaluator

df_tr = load_train_data()
df_val = load_validation_data()
ev = CostWeightedEvaluator()

results = []

for p_rate in [0.28, 0.30, 0.32, 0.35, 0.38, 0.40, 0.45]:
    for max_v in [1000, 1200, 1500, 1800, 2000, 2500, 3000]:
        for min_v in [0, 200, 400, 600, 800]:
            for age in [15, 30, 45, 60, 90, 999]:
                for prior in [0, 1, 2, 999]:
                    for first_time in [True, False, None]:
                        for cat in [None, ['Footwear', 'Apparel'], ['Electronics', 'Footwear'], ['Apparel']]:
                            cond_tr = (df_tr['payment_mode'] == 'COD') & (df_tr['pincode_rolling_rto_rate'] >= p_rate) & (df_tr['order_value'] <= max_v) & (df_tr['order_value'] >= min_v)
                            cond_val = (df_val['payment_mode'] == 'COD') & (df_val['pincode_rolling_rto_rate'] >= p_rate) & (df_val['order_value'] <= max_v) & (df_val['order_value'] >= min_v)
                            
                            if age < 999:
                                cond_tr &= (df_tr['customer_account_age_days'] <= age)
                                cond_val &= (df_val['customer_account_age_days'] <= age)
                            if prior < 999:
                                cond_tr &= (df_tr['customer_prior_orders'] <= prior)
                                cond_val &= (df_val['customer_prior_orders'] <= prior)
                            if first_time is not None:
                                cond_tr &= (df_tr['is_first_time_customer'] == first_time)
                                cond_val &= (df_val['is_first_time_customer'] == first_time)
                            if cat is not None:
                                cond_tr &= (df_tr['item_category'].isin(cat))
                                cond_val &= (df_val['item_category'].isin(cat))
                            
                            if cond_tr.sum() >= 20:
                                r_tr = ev.evaluate_flags(cond_tr.values, df_tr, 'h', 'h')
                                if r_tr.cost_metrics.net_financial_savings_inr >= 500.0:
                                    r_val = ev.evaluate_flags(cond_val.values, df_val, 'h', 'h')
                                    delta_net = r_val.cost_metrics.net_financial_savings_inr - r_tr.cost_metrics.net_financial_savings_inr
                                    if delta_net < 0:
                                        results.append({
                                            'tr_net': r_tr.cost_metrics.net_financial_savings_inr,
                                            'val_net': r_val.cost_metrics.net_financial_savings_inr,
                                            'tr_prec': r_tr.standard_metrics.precision,
                                            'val_prec': r_val.standard_metrics.precision,
                                            'tr_rec': r_tr.standard_metrics.recall,
                                            'val_rec': r_val.standard_metrics.recall,
                                            'tr_flags': r_tr.standard_metrics.flagged_orders,
                                            'val_flags': r_val.standard_metrics.flagged_orders,
                                            'p_rate': p_rate, 'min_v': min_v, 'max_v': max_v, 'age': age, 'prior': prior, 'first_time': first_time, 'cat': cat
                                        })

results.sort(key=lambda x: (x['tr_net'], -x['val_net']), reverse=True)
print(f"Total viable degrading rules found: {len(results)}")
for r in results[:15]:
    print(
        f"Train: Net=+Rs {r['tr_net']:,.2f}, Prec={r['tr_prec']*100:.1f}%, Rec={r['tr_rec']*100:.1f}% ({r['tr_flags']} flags) | "
        f"Val: Net=Rs {r['val_net']:,.2f}, Prec={r['val_prec']*100:.1f}%, Rec={r['val_rec']*100:.1f}% ({r['val_flags']} flags) | "
        f"params: pincode>={r['p_rate']}, val=[{r['min_v']}-{r['max_v']}], age<={r['age']}, prior<={r['prior']}, first={r['first_time']}"
    )
