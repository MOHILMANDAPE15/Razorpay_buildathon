"""
Regenerates v1_frozen_rules_snapshot.json with a 100% autonomous
Generator -> Reflector -> Selector pipeline. No human-authored rules injected.
3 rounds x 3 candidates per round = ~18 LLM calls total.

Produces final train-vs-validation table at the end.
"""

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = THIS_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import numpy as np
from app.data.loader import load_train_data, load_validation_data
from app.data.schema import sanitize_features
from app.engine.frozen_rule_snapshot import (
    generate_frozen_rule_snapshot,
    FrozenRuleEnsemble,
    LIVE_SNAPSHOT_PATH,
)
from app.engine.evaluator import CostWeightedEvaluator
from app.core.sandbox import execute_rule_sandboxed

print("=" * 70)
print("Regenerating v1_frozen_rules_snapshot.json")
print("  . 3 rounds x 3 candidates per round")
print("  . Zero human-authored rules -- 100% LLM-generated")
print("  . Drift columns excluded")
print("=" * 70)

snapshot = generate_frozen_rule_snapshot(live=True, n_rounds=3, hypotheses_per_round=3)

selected = snapshot.get("selected_rules", [])
print(f"\n[Snapshot] {len(selected)} rules selected:")
for r in selected:
    print(f"  ID: {r['id']}")
    print(f"  Name: {r['name']}")
    print(f"  Code:\n{r['code']}\n")

df_train = load_train_data()
df_val = load_validation_data()

evaluator = CostWeightedEvaluator()
ensemble = FrozenRuleEnsemble(LIVE_SNAPSHOT_PATH).load()

sanitized_train = sanitize_features(df_train)
train_flags = __import__('numpy').zeros(len(df_train), dtype=bool)
for rule in ensemble.rules:
    flags = execute_rule_sandboxed(rule.code, sanitized_train)
    train_flags = train_flags | flags.astype(bool)
train_report = evaluator.evaluate_flags(train_flags, df_train, "frozen_train", "Frozen v1 (Train)")

sanitized_val = sanitize_features(df_val)
val_flags = __import__('numpy').zeros(len(df_val), dtype=bool)
for rule in ensemble.rules:
    flags = execute_rule_sandboxed(rule.code, sanitized_val)
    val_flags = val_flags | flags.astype(bool)
val_report = evaluator.evaluate_flags(val_flags, df_val, "frozen_val", "Frozen v1 (Validation/Drift)")

print("\n" + "=" * 70)
print("FINAL RESULTS -- Frozen v1 Rule Ensemble (100% Autonomously Generated)")
print(f"{'Split':<28} {'Precision':>10} {'Recall':>8} {'F1':>8} {'Net Savings (Rs.)':>18}")
print("-" * 70)

tr = train_report.standard_metrics
tc = train_report.cost_metrics
vr = val_report.standard_metrics
vc = val_report.cost_metrics

print(f"{'Train (Pre-Drift, Days 0-55)':<28} {tr.precision*100:>9.1f}% {tr.recall*100:>7.2f}% {tr.f1*100:>7.2f}% {tc.net_financial_savings_inr:>18,.2f}")
print(f"{'Validation (Drift, Days 56-75)':<28} {vr.precision*100:>9.1f}% {vr.recall*100:>7.2f}% {vr.f1*100:>7.2f}% {vc.net_financial_savings_inr:>18,.2f}")
print("=" * 70)
delta_prec = vr.precision - tr.precision
delta_rec  = vr.recall  - tr.recall
delta_f1   = vr.f1      - tr.f1
delta_net  = vc.net_financial_savings_inr - tc.net_financial_savings_inr
print(f"{'Delta (Val - Train)':<28} {delta_prec*100:>+9.1f}% {delta_rec*100:>+7.2f}% {delta_f1*100:>+7.2f}% {delta_net:>+18,.2f}")
print("=" * 70)
print("\nSnapshot:", LIVE_SNAPSHOT_PATH)
print("Rule IDs:", [r['id'] for r in selected])
print("\nAll rules autonomously generated. No hand-authored rules seeded.")
