"""Compute exact held-out test metrics across thresholds and exact FP AOV."""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pandas as pd
import numpy as np
from app.data.loader import evaluate_on_held_out_test, load_validation_data
from app.engine.frozen_rule_snapshot import load_frozen_v1_rules
from app.engine.router import ThreeWayRouter
from app.engine.selector import EnsembleRule


def run_analysis(df_test):
    v1_rules = load_frozen_v1_rules()
    ensemble = EnsembleRule(v1_rules)
    
    print("=" * 80)
    print(f"HELD-OUT TEST SET ANALYSIS (2,641 Orders, Days 76–89)")
    print("=" * 80)

    # 1. Headline Baseline (0.70 threshold)
    router_base = ThreeWayRouter(low_risk_threshold=0.35, high_risk_threshold=0.70)
    decisions_base = router_base.route_batch(df_test, ensemble)
    breakdown_base = router_base.evaluate_section_6_2_split(df_test, decisions_base)

    gt_map = dict(zip(df_test["order_id"].astype(str), df_test["is_rto"].astype(int)))
    val_map = dict(zip(df_test["order_id"].astype(str), df_test["order_value"].astype(float)))

    auto_blocked = [d for d in decisions_base if d.decision == "AUTO_BLOCK"]
    auto_fp = [d for d in auto_blocked if gt_map.get(d.order_id, 0) == 0]
    auto_tp = [d for d in auto_blocked if gt_map.get(d.order_id, 0) == 1]

    fp_vals = [val_map.get(d.order_id, 0.0) for d in auto_fp]
    tp_vals = [val_map.get(d.order_id, 0.0) for d in auto_tp]

    print(f"\n[1] EXACT AUDIT OF AUTO-BLOCKED FALSE POSITIVES (Baseline Threshold >= 0.70):")
    print(f"    Total Auto-Blocked:        {len(auto_blocked)}")
    print(f"    True Positives (TP):       {len(auto_tp)} orders")
    print(f"    False Positives (FP):      {len(auto_fp)} orders")
    print(f"    Sum of FP Order Values:    Rs. {sum(fp_vals):,.2f}")
    print(f"    Actual Mean FP Order Val:  Rs. {np.mean(fp_vals):,.2f}")
    print(f"    Median FP Order Value:     Rs. {np.median(fp_vals):,.2f}")
    print(f"    Min / Max FP Order Value:  Rs. {min(fp_vals):,.2f} / Rs. {max(fp_vals):,.2f}")
    print(f"    Avoided RTO Savings (TP):  {len(auto_tp)} * Rs. 250 = Rs. {len(auto_tp)*250:,.2f}")
    print(f"    Actual FP Margin Loss:     Rs. {sum(fp_vals)*0.15:,.2f} (15% of Rs. {sum(fp_vals):,.2f})")
    print(f"    Net Financial Savings:     Rs. {len(auto_tp)*250 - sum(fp_vals)*0.15:,.2f}")
    
    # Exact Break-Even Precision Calculation
    mean_fp_val = np.mean(fp_vals)
    mean_fp_cost = mean_fp_val * 0.15
    be_precision = mean_fp_cost / (250.0 + mean_fp_cost)
    print(f"    Exact Break-Even Precision: {be_precision*100:.2f}% (based on actual mean FP value of Rs. {mean_fp_val:.2f})")

    # 2. Threshold Sweep on Held-Out Test Set
    print(f"\n[2] HELD-OUT TEST SPLIT THRESHOLD SWEEP (2,641 Orders):")
    print(f"{'Threshold':<12} | {'Auto-Block':<10} | {'Auto-Prec':<10} | {'Auto-TP':<8} | {'Auto-FP':<8} | {'Review Vol':<12} | {'Review RTO%':<12} | {'Auto Net INR':<12}")
    print("-" * 96)

    for th in [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]:
        router = ThreeWayRouter(low_risk_threshold=0.35, high_risk_threshold=th)
        decisions = router.route_batch(df_test, ensemble)
        bd = router.evaluate_section_6_2_split(df_test, decisions)
        
        ab = [d for d in decisions if d.decision == "AUTO_BLOCK"]
        tp_cnt = sum(1 for d in ab if gt_map.get(d.order_id, 0) == 1)
        fp_cnt = sum(1 for d in ab if gt_map.get(d.order_id, 0) == 0)

        print(
            f"{th:<12.2f} | "
            f"{bd.auto_blocked_count:<10} | "
            f"{bd.auto_decided_precision*100:<9.2f}% | "
            f"{tp_cnt:<8} | "
            f"{fp_cnt:<8} | "
            f"{bd.manual_review_count} ({bd.manual_review_pct:.2f}%) | "
            f"{bd.review_queue_rto_concentration*100:<11.2f}% | "
            f"Rs. {bd.auto_decided_net_savings_inr:<10,.2f}"
        )


if __name__ == "__main__":
    evaluate_on_held_out_test(run_analysis)
