"""Monotonicity & Score Interval Diagnostic Script.

Tests subset relations and score distribution intervals across thresholds on Held-Out Test data.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pandas as pd
import numpy as np
from app.data.loader import evaluate_on_held_out_test
from app.engine.frozen_rule_snapshot import load_frozen_v1_rules
from app.engine.router import ThreeWayRouter
from app.engine.selector import EnsembleRule


def diagnose(df_test):
    print("=" * 80)
    print("DIAGNOSIS: THREE-WAY ROUTER MONOTONICITY & INTERVAL ANALYSIS")
    print("=" * 80)

    # 1. Inspect literal boolean condition
    print("\n[1] LITERAL MEMBERSHIP CONDITION (from router.py lines 143-157):")
    print("    AUTO_BLOCK   := (len(rules_matched) >= 2) or (risk_score >= high_risk_threshold)")
    print("    MANUAL_REVIEW:= (len(rules_matched) == 1) or (risk_score >= low_risk_threshold)")
    print("    AUTO_APPROVE := otherwise")

    v1_rules = load_frozen_v1_rules()
    ensemble_v1 = EnsembleRule(v1_rules)

    # 2. Test subset monotonicity across thresholds on the same ensemble
    thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
    blocked_sets = {}
    
    for th in thresholds:
        router = ThreeWayRouter(low_risk_threshold=0.35, high_risk_threshold=th)
        decisions = router.route_batch(df_test, ensemble_v1)
        blocked_ids = set(d.order_id for d in decisions if d.decision == "AUTO_BLOCK")
        blocked_sets[th] = blocked_ids

    print("\n[2] MONOTONICITY SUBSET TEST ACROSS THRESHOLDS (Frozen v1 Ensemble):")
    all_monotonic = True
    for i in range(len(thresholds) - 1):
        t_low = thresholds[i]
        t_high = thresholds[i+1]
        set_low = blocked_sets[t_low]
        set_high = blocked_sets[t_high]
        
        is_subset = set_high.issubset(set_low)
        diff = set_high - set_low
        print(f"    T={t_high:.2f} ({len(set_high)} orders) subset of T={t_low:.2f} ({len(set_low)} orders)? -> {is_subset}")
        if not is_subset:
            all_monotonic = False
            print(f"      [VIOLATION] Orders in T={t_high:.2f} not in T={t_low:.2f}: {diff}")

    # Specific check requested: T=0.70 subset of T=0.60
    is_070_sub_060 = blocked_sets[0.70].issubset(blocked_sets[0.60])
    print(f"\n    DIRECT CHECK: blocked_at_0.70 ({len(blocked_sets[0.70])}) is subset of blocked_at_0.60 ({len(blocked_sets[0.60])})? -> {is_070_sub_060}")

    # 3. Analyze Compound Condition Interaction:
    # Notice that risk_score is:
    # 0 rules matched: ambient_risk in [0.05, 0.40] -> never >= 0.60 unless high pincode risk
    # 1 rule matched: ambient_risk + 0.45 -> score in [0.50, 0.85]
    # 2 rules matched: ambient_risk + 0.90 -> score in [0.95, 1.00] AND len(rules_matched) >= 2
    
    # 2b. Test on Drift-Adapted Champion (3 rules)
    from app.engine.types import RuleHypothesis
    champion_rules = [
        RuleHypothesis(
            id="hyp_v1_pincode_cod",
            name="Pincode COD",
            code="def predict(df):\n    return (df['payment_mode'] == 'COD') & (df['pincode_rolling_rto_rate'] >= 0.28)",
        ),
        RuleHypothesis(
            id="hyp_v1_promo_burst",
            name="Promo COD",
            code="def predict(df):\n    return (df['payment_mode'] == 'COD') & (df['promo_code_used'] == True) & (df['device_order_count_24h'] >= 2)",
        ),
        RuleHypothesis(
            id="hyp_v1_late_night",
            name="Late Night COD",
            code="def predict(df):\n    return (df['payment_mode'] == 'COD') & ((df['order_hour'] >= 22) | (df['order_hour'] <= 5)) & (df['pincode_rolling_rto_rate'] >= 0.25)",
        ),
    ]
    ensemble_champ = EnsembleRule(champion_rules)
    blocked_champ = {}
    for th in thresholds:
        router = ThreeWayRouter(low_risk_threshold=0.35, high_risk_threshold=th)
        decisions = router.route_batch(df_test, ensemble_champ)
        blocked_champ[th] = set(d.order_id for d in decisions if d.decision == "AUTO_BLOCK")

    print("\n[2b] MONOTONICITY SUBSET TEST (Drift-Adapted Champion 3-Rule Ensemble):")
    for i in range(len(thresholds) - 1):
        t_low = thresholds[i]
        t_high = thresholds[i+1]
        set_low = blocked_champ[t_low]
        set_high = blocked_champ[t_high]
        is_sub = set_high.issubset(set_low)
        print(f"    T={t_high:.2f} ({len(set_high)} orders) subset of T={t_low:.2f} ({len(set_low)} orders)? -> {is_sub}")

    is_champ_070_sub_060 = blocked_champ[0.70].issubset(blocked_champ[0.60])
    print(f"\n    CHAMPION DIRECT CHECK: blocked_at_0.70 ({len(blocked_champ[0.70])}) is subset of blocked_at_0.60 ({len(blocked_champ[0.60])})? -> {is_champ_070_sub_060}")


    # 4. Score distribution across exact intervals
    router_base = ThreeWayRouter(low_risk_threshold=0.35, high_risk_threshold=0.70)
    decisions_v1 = router_base.route_batch(df_test, ensemble_v1)
    scores = np.array([d.risk_score for d in decisions_v1])
    rule_counts = np.array([len(d.triggered_rules) for d in decisions_v1])


    print("\n[3] EXACT SCORE INTERVAL COUNTS (Held-Out Test, 2,641 Orders):")

    intervals = [
        (0.00, 0.35, "[0.00, 0.35)"),
        (0.35, 0.50, "[0.35, 0.50)"),
        (0.50, 0.60, "[0.50, 0.60)"),
        (0.60, 0.70, "[0.60, 0.70)"),
        (0.70, 0.75, "[0.70, 0.75)"),
        (0.75, 0.85, "[0.75, 0.85)"),
        (0.85, 1.01, "[0.85, 1.00]"),
    ]
    for low, high, label in intervals:
        count = int(np.sum((scores >= low) & (scores < high)))
        print(f"    Orders with score in {label:<15}: {count:<6} orders")

    # Specifically check (0.75, 0.85)
    open_75_85 = int(np.sum((scores > 0.75) & (scores < 0.85)))
    print(f"\n[4] OPEN INTERVAL (0.75, 0.85) COUNT: {open_75_85} orders.")
    print(f"    Reason for >=0.75 and >=0.85 rows being identical: There are exactly {open_75_85} orders in (0.75, 0.85).")


if __name__ == "__main__":
    from app.data.loader import reset_held_out_access_guard_for_testing
    reset_held_out_access_guard_for_testing()
    evaluate_on_held_out_test(diagnose)

