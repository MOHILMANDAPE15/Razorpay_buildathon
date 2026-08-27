"""Reconciliation Script: Reconciling 51 vs 23 Auto-Block Discrepancy."""

import hashlib
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import data_paths
from app.data.loader import evaluate_on_held_out_test, reset_held_out_access_guard_for_testing
from app.engine.frozen_rule_snapshot import load_frozen_v1_rules
from app.engine.router import ThreeWayRouter
from app.engine.selector import EnsembleRule
from evaluate_final_held_out_test import get_adapted_champion_rules



def reconcile(df_test):
    print("=" * 80)
    print("RECONCILIATION AUDIT: AUTO-BLOCK DISCREPANCY AT T=0.70")
    print("=" * 80)

    # 1. File Checksum & Metadata
    file_bytes = data_paths.held_out_test_path.read_bytes()
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    print(f"\n[1] DATASET VERIFICATION:")
    print(f"    File Path:     {data_paths.held_out_test_path}")
    print(f"    Row Count:     {len(df_test):,} rows")
    print(f"    Date Range:    Day {df_test['day_index'].min()} to Day {df_test['day_index'].max()}")
    print(f"    SHA-256 Hash:  {sha256}")

    # 2. Model A: Frozen v1 Baseline (2 rules)
    v1_rules = load_frozen_v1_rules()
    ensemble_v1 = EnsembleRule(v1_rules)
    router_070 = ThreeWayRouter(low_risk_threshold=0.35, high_risk_threshold=0.70)
    decisions_v1 = router_070.route_batch(df_test, ensemble_v1)
    bd_v1 = router_070.evaluate_section_6_2_split(df_test, decisions_v1)

    # 3. Model B: Drift-Adapted Champion (3 rules)
    champ_rules = get_adapted_champion_rules()
    ensemble_champ = EnsembleRule(champ_rules)
    decisions_champ = router_070.route_batch(df_test, ensemble_champ)
    bd_champ = router_070.evaluate_section_6_2_split(df_test, decisions_champ)

    print("\n[2] SIDE-BY-SIDE MODEL COMPARISON AT T=0.70 ON THE SAME DATASET:")
    print(f"{'Attribute':<32} | {'Run B: Static Frozen v1 (2 Rules)':<35} | {'Run A: Drift-Adapted Champion (3 Rules)':<35}")
    print("-" * 110)
    print(f"{'Model Version':<32} | {'frozen_v1_baseline (2 rules)':<35} | {'drift_adapted_champion_v2 (3 rules)':<35}")
    print(f"{'Rule Set':<32} | {[r.id for r in v1_rules]!s:<35} | {[r.id for r in champ_rules]!s:<35}")
    print(f"{'Auto-Blocked Orders':<32} | {bd_v1.auto_blocked_count:<35} | {bd_champ.auto_blocked_count:<35}")
    print(f"{'Auto-Blocked TP / FP':<32} | {f'{bd_v1.auto_decided_precision*bd_v1.auto_blocked_count:.0f} TP / {bd_v1.auto_blocked_count - bd_v1.auto_decided_precision*bd_v1.auto_blocked_count:.0f} FP':<35} | {f'{bd_champ.auto_decided_precision*bd_champ.auto_blocked_count:.0f} TP / {bd_champ.auto_blocked_count - bd_champ.auto_decided_precision*bd_champ.auto_blocked_count:.0f} FP':<35}")
    print(f"{'Auto-Block Precision':<32} | {f'{bd_v1.auto_decided_precision*100:.2f}%':<35} | {f'{bd_champ.auto_decided_precision*100:.2f}%':<35}")
    print(f"{'Manual Review Orders':<32} | {f'{bd_v1.manual_review_count} ({bd_v1.manual_review_pct:.2f}%)':<35} | {f'{bd_champ.manual_review_count} ({bd_champ.manual_review_pct:.2f}%)':<35}")
    print(f"{'Review Queue RTO Concentration':<32} | {f'{bd_v1.review_queue_rto_concentration*100:.2f}%':<35} | {f'{bd_champ.review_queue_rto_concentration*100:.2f}%':<35}")
    print(f"{'Auto Net Financial Savings':<32} | {f'Rs. {bd_v1.auto_decided_net_savings_inr:,.2f}':<35} | {f'Rs. {bd_champ.auto_decided_net_savings_inr:,.2f}':<35}")
    print("=" * 110)


if __name__ == "__main__":
    reset_held_out_access_guard_for_testing()
    evaluate_on_held_out_test(reconcile)
