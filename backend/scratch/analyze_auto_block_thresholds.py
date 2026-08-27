"""Empirical Threshold Analysis: Auto-Block vs Manual Review Distribution.

Analyzes the score distribution, precision, recall, review queue volume, and net financial savings
across different high-risk auto-block thresholds and routing criteria on both Validation (3,885 orders)
and Held-Out Test (2,641 orders).
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import numpy as np
import pandas as pd
from app.data.loader import load_validation_data, evaluate_on_held_out_test
from app.engine.frozen_rule_snapshot import load_frozen_v1_rules
from app.engine.router import ThreeWayRouter
from app.engine.selector import EnsembleRule


def evaluate_threshold_sweep(df, split_name="Validation"):
    v1_rules = load_frozen_v1_rules()
    ensemble = EnsembleRule(v1_rules)
    
    print(f"\n================================================================================")
    print(f"THRESHOLD SWEEP ANALYSIS ON {split_name.upper()} DATASET ({len(df):,} Orders)")
    print(f"Base RTO Rate: {df['is_rto'].mean()*100:.2f}%")
    print(f"================================================================================")
    print(f"{'High Thresh':<12} | {'Auto-Block':<10} | {'Auto-Prec':<10} | {'Auto-TP':<8} | {'Auto-FP':<8} | {'Review Vol':<10} | {'Review RTO%':<12} | {'Auto Net INR':<12}")
    print("-" * 92)

    thresholds = [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]

    for th in thresholds:
        router = ThreeWayRouter(low_risk_threshold=0.35, high_risk_threshold=th)
        decisions = router.route_batch(df, ensemble)
        breakdown = router.evaluate_section_6_2_split(df, decisions)
        
        gt_map = dict(zip(df["order_id"].astype(str), df["is_rto"].astype(int)))
        auto_blocked = [d for d in decisions if d.decision == "AUTO_BLOCK"]
        tp = sum(1 for d in auto_blocked if gt_map.get(d.order_id, 0) == 1)
        fp = sum(1 for d in auto_blocked if gt_map.get(d.order_id, 0) == 0)

        print(
            f"{th:<12.2f} | "
            f"{breakdown.auto_blocked_count:<10} | "
            f"{breakdown.auto_decided_precision*100:<9.2f}% | "
            f"{tp:<8} | "
            f"{fp:<8} | "
            f"{breakdown.manual_review_pct:<9.2f}% | "
            f"{breakdown.review_queue_rto_concentration*100:<11.2f}% | "
            f"Rs. {breakdown.auto_decided_net_savings_inr:<10,.2f}"
        )


def analyze_score_distribution(df, split_name="Validation"):
    v1_rules = load_frozen_v1_rules()
    ensemble = EnsembleRule(v1_rules)
    router = ThreeWayRouter(low_risk_threshold=0.35, high_risk_threshold=0.70)
    decisions = router.route_batch(df, ensemble)
    
    gt_map = dict(zip(df["order_id"].astype(str), df["is_rto"].astype(int)))
    val_map = dict(zip(df["order_id"].astype(str), df["order_value"].astype(float)))
    
    # Detailed bucket breakdown
    print(f"\nSCORE & RULE-MATCH DISTRIBUTION ON {split_name.upper()}:")
    print(f"{'Band / Criteria':<35} | {'Count':<8} | {'RTOs':<8} | {'Precision':<10} | {'Avg Order Val':<15}")
    print("-" * 85)
    
    # Rule match counts
    for match_count in [0, 1, 2]:
        subset = [d for d in decisions if len(d.triggered_rules) == match_count]
        if subset:
            rtos = sum(1 for d in subset if gt_map.get(d.order_id, 0) == 1)
            prec = (rtos / len(subset)) * 100
            avg_val = np.mean([val_map.get(d.order_id, 0.0) for d in subset])
            print(f"Rules Matched == {match_count:<17} | {len(subset):<8} | {rtos:<8} | {prec:<9.2f}% | Rs. {avg_val:<13.2f}")

    # Risk score buckets
    score_bins = [(0.0, 0.35), (0.35, 0.50), (0.50, 0.70), (0.70, 0.85), (0.85, 1.01)]
    for low, high in score_bins:
        subset = [d for d in decisions if low <= d.risk_score < high]
        if subset:
            rtos = sum(1 for d in subset if gt_map.get(d.order_id, 0) == 1)
            prec = (rtos / len(subset)) * 100
            avg_val = np.mean([val_map.get(d.order_id, 0.0) for d in subset])
            print(f"Risk Score in [{low:.2f}, {high:.2f}){'':<11} | {len(subset):<8} | {rtos:<8} | {prec:<9.2f}% | Rs. {avg_val:<13.2f}")


if __name__ == "__main__":
    df_val = load_validation_data()
    analyze_score_distribution(df_val, "Validation Split (3,885 orders)")
    evaluate_threshold_sweep(df_val, "Validation Split (3,885 orders)")

