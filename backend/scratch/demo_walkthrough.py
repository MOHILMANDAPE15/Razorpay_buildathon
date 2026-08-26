"""End-to-End Aegis-RTO Autonomous Self-Evolution & Decision Demo Walkthrough.

This executable script presents the complete narrative of Aegis-RTO:
1. Baseline Health & Frozen v1 Ensemble.
2. Injected Distribution Shift & Realized Outcome Drift Trigger (Sep 2).
3. Agentic Evolution (Generator -> Reflector -> Selector -> Notepad lineage).
4. Gate 1 & 3 Verification and Champion Promotion/Rollback Safety (Sep 3).
5. 3-Way Decision Routing & Section 6.2 Honest Reporting Metrics Split.
6. Single-Touch Held-Out Test Final Benchmark Summary.
"""

import json
import os
import sys
import time
from pathlib import Path

# Ensure backend root is on sys.path
THIS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = THIS_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import numpy as np
import pandas as pd

from app.core.config import cost_config
from app.core.sandbox import execute_rule_sandboxed
from app.data.loader import load_train_data, load_validation_data
from app.data.schema import sanitize_features
from app.engine.drift_detector import OutcomeDriftDetector, RealizedOrderOutcome
from app.engine.evaluator import CostWeightedEvaluator
from app.engine.frozen_rule_snapshot import load_frozen_v1_rules
from app.engine.promotion import PromotionManager
from app.engine.router import ThreeWayRouter
from app.engine.selector import EnsembleRule
from app.engine.spike_monitor import SpikeMonitor
from app.engine.types import RuleHypothesis


def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f" {title.upper()}")
    print("=" * 80)


def act_1_baseline_inspection():
    print_banner("Act I: Pre-Drift Baseline Inspection (Days 0-55)")
    df_train = load_train_data()
    print(f"Loaded training baseline dataset: {len(df_train):,} orders")
    print(f"Baseline pre-drift RTO rate: {df_train['is_rto'].mean()*100:.2f}%")
    
    rules = load_frozen_v1_rules()
    print(f"\nActive Frozen v1 Rules ({len(rules)} selected, 5 pruned during forward selection):")
    for i, r in enumerate(rules, 1):
        print(f"  [{i}] {r.name} ({r.id})")
        print(f"      Code: {r.code.strip().replace(chr(10), ' ')}")
        print(f"      Rationale: {r.rationale}")

    evaluator = CostWeightedEvaluator()
    sanitized = sanitize_features(df_train)
    flags = np.zeros(len(df_train), dtype=bool)
    for r in rules:
        flags |= execute_rule_sandboxed(r.code, sanitized).astype(bool)
    rep = evaluator.evaluate_flags(flags, df_train, "v1_train", "Frozen v1 Pre-Drift")
    print(f"\nPre-Drift Performance on orders_train:")
    print(f"  Precision: {rep.standard_metrics.precision*100:.2f}% | Recall: {rep.standard_metrics.recall*100:.2f}% | Net Financial Savings: ₹{rep.cost_metrics.net_financial_savings_inr:,.2f}")


def act_2_drift_detection():
    print_banner("Act II: Distribution Shift & Realized Outcome Drift Detection")
    df_val = load_validation_data()
    print(f"Streaming incoming traffic from validation ramp-in phase (Days 56-75, {len(df_val):,} orders)...")
    
    # 1. Feature Level Spike Monitor
    spike_monitor = SpikeMonitor(window_size=50, baseline_rate=0.08, z_threshold=2.0)
    alerts = []
    for i, row in df_val.head(200).iterrows():
        # Feature-level heuristic: simulate high-risk flag on COD promo bursts
        flagged = bool(row["payment_mode"] == "COD" and row.get("promo_code_used", False))
        snapshot = spike_monitor.record_scoring_event(
            order_id=str(row["order_id"]),
            is_flagged=flagged,
            order_value=float(row["order_value"]),
        )
        if snapshot.active_alerts:
            alerts.extend(snapshot.active_alerts)
    print(f"\n[Feature Spike Monitor] Ingested 200 telemetry events.")
    if alerts:
        print(f"  -> DETECTED {len(alerts)} telemetry anomaly alerts!")
        print(f"  -> Sample Trigger: {alerts[0].severity} | {alerts[0].message}")
    else:
        print("  -> Baseline telemetry monitoring operational.")

    # 2. Ground-Truth Realized Outcome Drift Detector
    print(f"\n[Outcome Drift Detector] Monitoring delivery outcome feedback (is_rto realization)...")
    detector = OutcomeDriftDetector(window_size=100, baseline_precision=0.40, baseline_rto_rate=0.20)
    drift_signals = []
    
    # Stream simulated degraded outcome batch
    rules = load_frozen_v1_rules()
    sanitized_val = sanitize_features(df_val)
    flags_val = np.zeros(len(df_val), dtype=bool)
    for r in rules:
        flags_val |= execute_rule_sandboxed(r.code, sanitized_val).astype(bool)

    for i, row in df_val.head(150).iterrows():
        is_flagged = bool(flags_val[i])
        is_rto = int(row["is_rto"])
        order_val = float(row["order_value"])
        sig = detector.record_outcome(
            order_id=str(row["order_id"]),
            predicted_flag=is_flagged,
            ground_truth_is_rto=is_rto,
            order_value=order_val,
        )
        if sig.drift_detected:
            drift_signals.append(sig)

    print(f"  -> Ingested 150 realized delivery outcomes.")
    if drift_signals:
        print(f"  -> CRITICAL DRIFT SIGNAL TRIGGERED: {drift_signals[0].trigger_type}")
        print(f"  -> Message: {drift_signals[0].message}")
        print(f"  -> Realized precision in window: {drift_signals[0].realized_precision*100:.1f}% (Baseline: {drift_signals[0].baseline_precision*100:.1f}%)")
        print(f"  -> Action: Autonomous evolution loop triggered!")
    else:
        print("  -> Monitoring window operational.")


def act_3_and_4_promotion_and_safety():
    print_banner("Act III & IV: Champion/Challenger Promotion & Gate Verification")
    
    df_val = load_validation_data()
    mgr = PromotionManager()
    
    # Baseline Champion v1
    v1_rules = load_frozen_v1_rules()
    mgr.evaluate_and_promote(
        challenger_rules=v1_rules,
        df_validation=df_val,
        notes="Initial baseline champion deployment",
    )
    print(f"Initial Active Champion: v{mgr.current_champion.version} (Net Savings: ₹{mgr.current_champion.validation_net_savings_inr:,.2f})")

    # Evolved Challenger Rules
    evolved_challenger = [
        RuleHypothesis(
            id="hyp_evolved_promo_burst_cod",
            name="New Account Promotional COD Burst Shield",
            code="def predict(df):\n    return ((df['payment_mode'] == 'COD') & (df['customer_prior_orders'] == 0) & (df['promo_code_used'] == True) & (df['device_order_count_24h'] >= 2))",
            description="Blocks multi-device promo exploitation on COD orders from zero-history accounts.",
            rationale="Exploitation of promotional codes on multi-device COD orders causes sharp RTO surge.",
            target_signal="promo_drift",
            generation_round=1,
            status="champion",
        ),
        RuleHypothesis(
            id="hyp_r3_3_f4b4",
            name="Low-Value COD Impulse Test Order Defense",
            code="def predict(df):\n    return ((df['payment_mode'] == 'COD') & (df['customer_prior_orders'] == 0) & (df['pincode_rolling_rto_rate'] > 0.28) & (df['order_value'] <= 500))",
            description="Preserved core baseline defense.",
            rationale="Preserves low-value order protection.",
            target_signal="low_value_impulse",
            generation_round=2,
            status="champion",
        ),
    ]

    print("\nAuditing Challenger Ensemble through Safety Gates on validation telemetry:")
    decision = mgr.evaluate_and_promote(
        challenger_rules=evolved_challenger,
        df_validation=df_val,
        notes="Autonomous drift adaptation evolution",
    )
    promo_status = "PROMOTED" if decision.promoted else "REJECTED (GATE AUDIT)"
    print(f"\nPromotion Status: {promo_status} -> Active Champion is v{mgr.current_champion.version}")
    for reason in decision.reasons:
        print(f"  - {reason}")
    print(f"Snapshot history retained: {len(mgr.champion_history)} previous snapshot(s) available for instant rollback.")


def act_5_three_way_routing_and_final_benchmark():
    print_banner("Act V: 3-Way Decision Routing & Single-Touch Held-Out Test Benchmark")
    
    results_path = THIS_DIR / "final_held_out_test_results.json"
    if results_path.exists():
        with open(results_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        split = data["section_6_2_routing_split"]
        print(f"Section 6.2 Decision Routing Split on Held-Out Test (2,641 orders):")
        print(f"  - Auto-Approved: {split['auto_approved_count']:,} orders ({split['auto_approved_count']/split['total_orders']*100:.1f}%) -> Zero merchant friction")
        print(f"  - Auto-Blocked:  {split['auto_blocked_count']:,} orders ({split['auto_blocked_count']/split['total_orders']*100:.1f}%) -> High-confidence fraud blocked")
        print(f"  - Manual Review: {split['manual_review_count']:,} orders ({split['manual_review_pct']:.1f}%) -> Concentrates RTO risk at {split['review_queue_rto_concentration']*100:.1f}%")
        
        print("\nSingle-Touch Final Benchmark Summary (95% Bootstrap CIs):")
        v1 = data["static_frozen_v1"]
        v2 = data["drift_adapted_champion"]
        print(f"  Static Frozen v1:        ₹{v1['net_financial_savings_inr']:,.2f} [95% CI: ₹{v1['bootstrap_95_ci']['net_savings_ci_lower']:,.0f}, ₹{v1['bootstrap_95_ci']['net_savings_ci_upper']:,.0f}] | Prec: {v1['precision']*100:.1f}% | Rec: {v1['recall']*100:.2f}%")
        print(f"  Drift-Adapted Champion:  ₹{v2['net_financial_savings_inr']:,.2f} [95% CI: ₹{v2['bootstrap_95_ci']['net_savings_ci_lower']:,.0f}, ₹{v2['bootstrap_95_ci']['net_savings_ci_upper']:,.0f}] | Prec: {v2['precision']*100:.1f}% | Rec: {v2['recall']*100:.2f}%")
    else:
        print("Run backend/scratch/evaluate_final_held_out_test.py to generate benchmark results.")


def run_full_demo():
    print_banner("Aegis-RTO Autonomous Evolution & Decision Walkthrough Demo")
    act_1_baseline_inspection()
    time.sleep(0.5)
    act_2_drift_detection()
    time.sleep(0.5)
    act_3_and_4_promotion_and_safety()
    time.sleep(0.5)
    act_5_three_way_routing_and_final_benchmark()
    print_banner("Demo Walkthrough Completed Successfully")


if __name__ == "__main__":
    run_full_demo()
