"""Compute Exact Paired Bootstrap Delta CI on Held-Out Test Data.

Resamples the exact same 2,641 held-out test orders B=2,000 times, computing:
Delta_Savings = Net_Savings(Adapted) - Net_Savings(Frozen_v1)
Delta_Precision = Precision(Adapted) - Precision(Frozen_v1)
Delta_Recall = Recall(Adapted) - Recall(Frozen_v1)

Reports the exact empirical paired 95% CI and two-sided p-value for the difference.
"""

import json
import sys
from pathlib import Path

# Ensure backend root is on sys.path
THIS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = THIS_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import numpy as np
import pandas as pd

from app.core.config import cost_config, data_paths
from app.core.sandbox import execute_rule_sandboxed
from app.data.loader import evaluate_on_held_out_test
from app.data.schema import sanitize_features
from app.engine.frozen_rule_snapshot import load_frozen_v1_rules
from app.engine.types import RuleHypothesis

def _run_paired_bootstrap_evaluation(df_test: pd.DataFrame):
    frozen_v1_rules = load_frozen_v1_rules()
    adapted_rules = [
        RuleHypothesis(
            id="hyp_evolved_promo_burst_cod",
            name="New Account Promotional COD Burst Shield",
            code=(
                "def predict(df):\n"
                "    return (\n"
                "        (df['payment_mode'] == 'COD') &\n"
                "        (df['customer_prior_orders'] == 0) &\n"
                "        (df['promo_code_used'] == True) &\n"
                "        (df['device_order_count_24h'] >= 2)\n"
                "    )"
            ),
            generation_round=1,
            status="champion",
        ),
        RuleHypothesis(
            id="hyp_evolved_late_night_impulse_cod",
            name="Late-Night High-Risk Location COD Defense",
            code=(
                "def predict(df):\n"
                "    return (\n"
                "        (df['payment_mode'] == 'COD') &\n"
                "        (df['customer_prior_orders'] <= 1) &\n"
                "        (df['pincode_rolling_rto_rate'] >= 0.30) &\n"
                "        ((df['order_hour'] >= 22) | (df['order_hour'] <= 5)) &\n"
                "        (df['order_value'] <= 1200)\n"
                "    )"
            ),
            generation_round=2,
            status="champion",
        ),
        RuleHypothesis(
            id="hyp_r3_3_f4b4",
            name="Low-Value COD Impulse Test Order Defense",
            code=(
                "def predict(df):\n"
                "    return (\n"
                "        (df['payment_mode'] == 'COD') &\n"
                "        (df['customer_prior_orders'] == 0) &\n"
                "        (df['pincode_rolling_rto_rate'] > 0.28) &\n"
                "        (df['order_value'] <= 500)\n"
                "    )"
            ),
            generation_round=3,
            status="champion",
        ),
    ]

    sanitized = sanitize_features(df_test)
    flags_frozen = np.zeros(len(df_test), dtype=bool)
    for r in frozen_v1_rules:
        flags_frozen |= execute_rule_sandboxed(r.code, sanitized).astype(bool)

    flags_adapted = np.zeros(len(df_test), dtype=bool)
    for r in adapted_rules:
        flags_adapted |= execute_rule_sandboxed(r.code, sanitized).astype(bool)

    y_true = df_test["is_rto"].values.astype(int)
    order_vals = df_test["order_value"].values.astype(float)
    n = len(df_test)

    # Vectorized Paired Bootstrap
    np.random.seed(42)
    B = 2000
    delta_savings_list = []
    delta_precision_list = []
    delta_recall_list = []

    for b in range(B):
        idx = np.random.choice(n, size=n, replace=True)
        y_b = y_true[idx]
        v_b = order_vals[idx]
        
        # Frozen v1
        f_f = flags_frozen[idx]
        tp_f = np.sum(f_f & (y_b == 1))
        fp_f = np.sum(f_f & (y_b == 0))
        prec_f = tp_f / (tp_f + fp_f) if (tp_f + fp_f) > 0 else 0.0
        rec_f = tp_f / np.sum(y_b == 1) if np.sum(y_b == 1) > 0 else 0.0
        fp_cost_f = np.sum(v_b[f_f & (y_b == 0)] * 0.15)
        sav_f = (tp_f * 250.0) - fp_cost_f
        
        # Adapted
        f_a = flags_adapted[idx]
        tp_a = np.sum(f_a & (y_b == 1))
        fp_a = np.sum(f_a & (y_b == 0))
        prec_a = tp_a / (tp_a + fp_a) if (tp_a + fp_a) > 0 else 0.0
        rec_a = tp_a / np.sum(y_b == 1) if np.sum(y_b == 1) > 0 else 0.0
        fp_cost_a = np.sum(v_b[f_a & (y_b == 0)] * 0.15)
        sav_a = (tp_a * 250.0) - fp_cost_a
        
        delta_savings_list.append(sav_a - sav_f)
        delta_precision_list.append(prec_a - prec_f)
        delta_recall_list.append(rec_a - rec_f)

    delta_sav = np.array(delta_savings_list)
    delta_prec = np.array(delta_precision_list)
    delta_rec = np.array(delta_recall_list)

    ci_lower_sav = np.percentile(delta_sav, 2.5)
    ci_upper_sav = np.percentile(delta_sav, 97.5)
    # Two-sided empirical p-value for H0: delta = 0
    p_val_sav = 2 * min(np.mean(delta_sav >= 0), np.mean(delta_sav <= 0))

    print("=" * 70)
    print("PAIRED BOOTSTRAP DELTA ANALYSIS (B=2000 Resamples)")
    print("=" * 70)
    print(f"Point Estimate Delta (Adapted - Static): -₹{abs(np.mean(delta_sav)):,.2f}")
    print(f"Paired 95% Confidence Interval: [₹{ci_lower_sav:,.2f}, ₹{ci_upper_sav:,.2f}]")
    print(f"Empirical Two-Sided p-value: p = {p_val_sav:.4f}")
    print(f"Contains Zero: {'YES (Not Statistically Significant)' if ci_lower_sav <= 0 <= ci_upper_sav else 'NO (Statistically Significant)'}")
    print("-" * 70)
    print(f"Precision Delta: {np.mean(delta_prec)*100:+.2f}% [95% CI: {np.percentile(delta_prec, 2.5)*100:+.2f}%, {np.percentile(delta_prec, 97.5)*100:+.2f}%]")
    print(f"Recall Delta:    {np.mean(delta_rec)*100:+.2f}% [95% CI: {np.percentile(delta_rec, 2.5)*100:+.2f}%, {np.percentile(delta_rec, 97.5)*100:+.2f}%]")
    print("=" * 70)


if __name__ == "__main__":
    evaluate_on_held_out_test(_run_paired_bootstrap_evaluation)
