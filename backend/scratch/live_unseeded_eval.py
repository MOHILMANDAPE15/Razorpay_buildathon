import numpy as np
import pandas as pd
from app.agents.generator import HypothesisGenerator
from app.agents.reflector import HypothesisReflector
from app.engine.evaluator import CostWeightedEvaluator
from app.engine.selector import CostWeightedSelector
from app.engine.notepad import Notepad
from app.data.loader import load_train_data, load_validation_data
from app.data.schema import sanitize_features

df_train = load_train_data()
df_val = load_validation_data()

gen = HypothesisGenerator()
ref = HypothesisReflector()
evaluator = CostWeightedEvaluator()
notepad = Notepad()
selector = CostWeightedSelector(evaluator=evaluator)

# Neutral Pre-Drift Context: No hardcoded thresholds or prescribed conditions
neutral_prompt_summary = (
    "Pre-Drift Fraud Baseline (Days 0-55):\n"
    "- Target fraud patterns in historical training data.\n"
    "- Available historical signals include payment mode, pincode RTO rate history, customer account age, prior order counts, order value, and category.\n"
    "- Remember the cost function: catching RTO fraud saves Rs. 250, but false alarms cost 15% of order value (lost merchant profit).\n"
    "- To maximize net savings (INR), combine discriminating risk signals and protect against false alarms on high-value orders."
)

print("Running 2-round autonomous evolution on orders_train without any seed rules...")
for r in range(1, 3):
    print(f"\n--- Round {r} ---")
    candidates = gen.generate_hypotheses(
        n_hypotheses=3,
        notepad_summary=neutral_prompt_summary if r == 1 else notepad.get_history_summary_for_generator(),
        generation_round=r,
        df_sample=sanitize_features(df_train.head(20)),
    )
    for c in candidates:
        if any(col in c.code for col in ["promo_code_used", "device_order_count_24h", "order_hour"]):
            print(f"Skipping candidate {c.name} (contains drift column)")
            continue
        notepad.add_hypothesis(c)
        report = evaluator.evaluate_hypothesis(c, df_train)
        notepad.record_evaluation(report)
        print(f"Rule: {c.name}")
        print(f"  Code: {c.code.strip()}")
        print(f"  Train: Prec {report.standard_metrics.precision*100:.1f}%, Rec {report.standard_metrics.recall*100:.2f}%, Net Rs. {report.cost_metrics.net_financial_savings_inr:,.2f}")

        # Live Reflector Mutation
        mutated = ref.reflect_and_mutate(c, report, generation_round=r, df_sample=sanitize_features(df_train.head(20)))
        if mutated and not any(col in mutated.code for col in ["promo_code_used", "device_order_count_24h", "order_hour"]):
            notepad.add_hypothesis(mutated)
            mut_report = evaluator.evaluate_hypothesis(mutated, df_train)
            notepad.record_evaluation(mut_report)
            print(f"  -> Mutated Child: {mutated.name}")
            print(f"     Code: {mutated.code.strip()}")
            print(f"     Train: Prec {mut_report.standard_metrics.precision*100:.1f}%, Rec {mut_report.standard_metrics.recall*100:.2f}%, Net Rs. {mut_report.cost_metrics.net_financial_savings_inr:,.2f}")

all_cands = notepad.get_all_hypotheses()
print(f"\nSelecting ensemble from {len(all_cands)} live-generated candidates...")
ens = selector.select_ensemble(all_cands, df_train, min_marginal_gain_inr=50.0)

print(f"\nSelected Ensemble: {len(ens.selected_rules)} rules")
for rule in ens.selected_rules:
    print(f"  - {rule.name}: {rule.code.strip()}")

# Evaluate on Train
from app.core.sandbox import execute_rule_sandboxed
sanitized_train = sanitize_features(df_train)
train_flags = np.zeros(len(df_train), dtype=bool)
for rule in ens.selected_rules:
    train_flags = train_flags | execute_rule_sandboxed(rule.code, sanitized_train).astype(bool)
rep_train = evaluator.evaluate_flags(train_flags, df_train, "ens_train", "Ensemble Train")

# Evaluate on Validation (Drift)
sanitized_val = sanitize_features(df_val)
val_flags = np.zeros(len(df_val), dtype=bool)
for rule in ens.selected_rules:
    val_flags = val_flags | execute_rule_sandboxed(rule.code, sanitized_val).astype(bool)
rep_val = evaluator.evaluate_flags(val_flags, df_val, "ens_val", "Ensemble Val")

print("\n" + "="*70)
print("LIVE EVOLVED ENSEMBLE RESULTS (100% UNSEEDED / ZERO HARDCODED RULES):")
print(f"  Train (Pre-drift):      Net Rs. {rep_train.cost_metrics.net_financial_savings_inr:,.2f} | Prec: {rep_train.standard_metrics.precision*100:.1f}% | Rec: {rep_train.standard_metrics.recall*100:.2f}%")
print(f"  Validation (Post-drift): Net Rs. {rep_val.cost_metrics.net_financial_savings_inr:,.2f} | Prec: {rep_val.standard_metrics.precision*100:.1f}% | Rec: {rep_val.standard_metrics.recall*100:.2f}%")
print("="*70)
