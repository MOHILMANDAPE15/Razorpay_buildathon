import sys, os
sys.path.insert(0, os.path.abspath('.'))
import pandas as pd
import numpy as np
from app.core.config import data_paths, cost_config
from app.data.loader import load_train_data, load_validation_data
from app.engine.frozen_rule_snapshot import load_frozen_v1_rules
from app.engine.selector import EnsembleRule
from app.engine.router import ThreeWayRouter

df_train = load_train_data()
df_val = load_validation_data()
df_test = pd.read_csv(data_paths.held_out_test_path)
df_all = pd.concat([df_train, df_val, df_test], ignore_index=True)

champion_rules = load_frozen_v1_rules()
ensemble = EnsembleRule(champion_rules) if champion_rules else None
router = ThreeWayRouter()


print("=== WHOLE DATASET OVERVIEW (17,333 Orders, Days 0-89) ===")
total_orders = len(df_all)
total_rtos = int(df_all["is_rto"].sum())
total_rto_gmv = float(df_all.loc[df_all["is_rto"] == 1, "order_value"].sum())
total_preventable_logistics = float(total_rtos * 250.0)

print(f"Total Dataset Orders: {total_orders:,}")
print(f"Total Genuine RTO Orders: {total_rtos:,} ({total_rtos/total_orders*100:.2f}% RTO rate)")
print(f"Total Potential RTO Logistics Loss (Max Theoretical Ceiling): Rs. {total_preventable_logistics:,.2f}")
print("=== WHOLE DATASET OVERVIEW (17,333 Orders, Days 0-89) ===")
total_orders = len(df_all)
total_rtos = int(df_all["is_rto"].sum())
total_rto_gmv = float(df_all.loc[df_all["is_rto"] == 1, "order_value"].sum())
total_preventable_logistics = float(total_rtos * 250.0)

print(f"Total Dataset Orders: {total_orders:,}")
print(f"Total Genuine RTO Orders: {total_rtos:,} ({total_rtos/total_orders*100:.2f}% RTO rate)")
print(f"Total Potential RTO Logistics Loss (Max Theoretical Ceiling): Rs. {total_preventable_logistics:,.2f}")
print(f"Total Potential RTO Order GMV: Rs. {total_rto_gmv:,.2f}")

print("\n=== SAVINGS BREAKDOWN BY SPLIT ===")

for name, df in [
    ("1. Held-Out Test Set (Days 76-89)", df_test),
    ("2. Validation Post-Drift (Days 56-75)", df_val),
    ("3. Training Pre-Drift (Days 0-55)", df_train),
    ("4. Full Combined Dataset (Days 0-89)", df_all),
]:
    n_orders = len(df)
    n_rtos = int(df["is_rto"].sum())
    max_logistics_pool = n_rtos * 250.0
    rto_gmv_pool = float(df.loc[df["is_rto"] == 1, "order_value"].sum())

    # Score through 3-way router
    decisions = router.route_batch(df, ensemble)
    eval_res = router.evaluate_section_6_2_split(df, decisions)

    # Review queue assisted metrics:
    # Review queue contains actual RTO orders. If human agents review them with 85% capture efficiency:
    review_decisions = [d for d in decisions if d.decision == "MANUAL_REVIEW"]
    gt_map = dict(zip(df["order_id"].astype(str), df["is_rto"].astype(int)))
    tp_review = sum(1 for d in review_decisions if gt_map.get(d.order_id, 0) == 1)
    fp_review = sum(1 for d in review_decisions if gt_map.get(d.order_id, 0) == 0)
    review_gross_potential = tp_review * 250.0
    review_85pct_saved = int(tp_review * 0.85) * 250.0
    
    total_system_combined = eval_res.auto_decided_net_savings_inr + review_85pct_saved

    print(f"\n=======================================================")
    print(f"{name}")
    print(f"=======================================================")
    print(f"• Total Order Volume: {n_orders:,}")
    print(f"• Total Genuine RTOs in split: {n_rtos:,} ({n_rtos/n_orders*100:.2f}%)")
    print(f"• Total Preventable RTO Logistics Loss Pool (Max Ceiling at Rs. 250/RTO): Rs. {max_logistics_pool:,.2f}")
    print(f"• Total RTO Merchandise Gross Value (GMV): Rs. {rto_gmv_pool:,.2f}")
    print(f"\n[A] AUTOMATED 3-WAY DECISIONS (Instant Machine Execution):")
    print(f"  - Auto-Blocked: {eval_res.auto_blocked_count:,} orders (TP: {int(eval_res.auto_blocked_count * eval_res.auto_decided_precision)}, FP: {eval_res.auto_blocked_count - int(eval_res.auto_blocked_count * eval_res.auto_decided_precision)})")
    print(f"  - Auto Precision: {eval_res.auto_decided_precision*100:.2f}% (Break-even threshold: 22.26%)")
    print(f"  - Auto Net Financial Savings: Rs. {eval_res.auto_decided_net_savings_inr:,.2f}")
    print(f"  - Auto-Decision Scalability: {eval_res.auto_decided_pct:.2f}% of all traffic resolved instantly")
    print(f"  - Realized Share of Total Loss Pool: {eval_res.auto_decided_net_savings_inr / max_logistics_pool * 100:.2f}% net profit captured")
    print(f"\n[B] MANUAL REVIEW QUEUE (Human Risk Triage):")
    print(f"  - Routed to Human Review: {eval_res.manual_review_count:,} orders ({eval_res.manual_review_pct:.2f}% of traffic)")
    print(f"  - Genuine RTOs in Review Queue: {tp_review:,} out of {eval_res.manual_review_count:,} ({eval_res.review_queue_rto_concentration*100:.2f}% concentration vs 31% random)")
    print(f"  - Potential RTO Savings in Review Queue (100% / 85% capture): Rs. {review_gross_potential:,.2f} / Rs. {review_85pct_saved:,.2f}")
    print(f"\n[C] COMBINED FULL-SYSTEM FINANCIAL IMPACT:")
    print(f"  - Total Machine + Human Saved: Rs. {total_system_combined:,.2f}")
    print(f"  - Total Share of Preventable Pool Saved: {total_system_combined / max_logistics_pool * 100:.2f}%")

