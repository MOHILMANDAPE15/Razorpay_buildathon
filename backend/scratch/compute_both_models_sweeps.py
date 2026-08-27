"""Compute exact threshold sweeps for both Model A (v1) and Model B (Champion)."""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.data.loader import evaluate_on_held_out_test, reset_held_out_access_guard_for_testing
from app.engine.frozen_rule_snapshot import load_frozen_v1_rules
from app.engine.router import ThreeWayRouter
from app.engine.selector import EnsembleRule
from evaluate_final_held_out_test import get_adapted_champion_rules


def run_sweep(df_test):
    v1_rules = load_frozen_v1_rules()
    champ_rules = get_adapted_champion_rules()
    
    gt_map = dict(zip(df_test["order_id"].astype(str), df_test["is_rto"].astype(int)))
    
    for name, rules in [("Model A: Static Frozen v1 (2 Rules)", v1_rules), ("Model B: Drift-Adapted Champion (3 Rules)", champ_rules)]:
        print(f"\n{'='*80}\n{name.upper()}\n{'='*80}")
        print(f"{'Threshold':<10} | {'Auto-Block':<10} | {'Auto-Prec':<10} | {'Auto-TP':<8} | {'Auto-FP':<8} | {'Review Vol':<15} | {'Review RTO%':<12} | {'Auto Net INR':<12}")
        print("-" * 96)
        ensemble = EnsembleRule(rules)
        for th in [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]:
            router = ThreeWayRouter(low_risk_threshold=0.35, high_risk_threshold=th)
            decisions = router.route_batch(df_test, ensemble)
            bd = router.evaluate_section_6_2_split(df_test, decisions)
            ab = [d for d in decisions if d.decision == "AUTO_BLOCK"]
            tp = sum(1 for d in ab if gt_map.get(d.order_id, 0) == 1)
            fp = sum(1 for d in ab if gt_map.get(d.order_id, 0) == 0)
            print(
                f"{th:<10.2f} | "
                f"{bd.auto_blocked_count:<10} | "
                f"{bd.auto_decided_precision*100:<9.2f}% | "
                f"{tp:<8} | "
                f"{fp:<8} | "
                f"{bd.manual_review_count} ({bd.manual_review_pct:.2f}%) | "
                f"{bd.review_queue_rto_concentration*100:<11.2f}% | "
                f"Rs. {bd.auto_decided_net_savings_inr:<10,.2f}"
            )


if __name__ == "__main__":
    reset_held_out_access_guard_for_testing()
    evaluate_on_held_out_test(run_sweep)
