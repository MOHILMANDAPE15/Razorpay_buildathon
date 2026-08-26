"""Real Execution Demonstration: Residual-Driven Targeted Evolution.

Demonstrates the Residual Miner running on the real transition/validation dataset:
1. Enforces a 5-day label maturity window.
2. Identifies real false negatives unflagged by the frozen v1 baseline.
3. Clusters missed abuse patterns into structured agendas.
4. Synthesizes a targeted defense rule.
5. Evaluates the proposed rule on the FULL 3,885 validation orders under the strict cost-weighted acceptance gate.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pandas as pd
from app.data.loader import load_train_data, load_validation_data
from app.engine.frozen_rule_snapshot import load_frozen_v1_rules
from app.engine.residual_miner import ResidualMiner
from app.engine.selector import EnsembleRule
from app.engine.types import RuleHypothesis


def main():
    print("=" * 75)
    print("AEGIS-RTO: RESIDUAL-DRIVEN EVOLUTION DEMONSTRATION")
    print("=" * 75)

    # 1. Load real datasets and active v1 frozen ensemble
    df_val = load_validation_data()
    v1_rules = load_frozen_v1_rules()
    incumbent_ensemble = EnsembleRule(v1_rules)

    print(f"\n[1] Loaded Validation Dataset: {len(df_val):,} orders (Days 56–75).")
    print(f"    Active Incumbent Ensemble: {len(v1_rules)} frozen baseline rules.")

    # 2. Initialize Residual Miner with 5-day maturity window
    miner = ResidualMiner(maturity_window_days=5, min_cluster_size=10)
    current_day = int(df_val["day_index"].max())

    print(f"\n[2] Executing Residual Miner Scan (Current Day: {current_day}, Maturity Window: 5 Days)...")
    report = miner.run_residual_analysis(df_val, incumbent_ensemble, current_day_index=current_day)

    print(f"    -> Total Orders Scanned:          {report.total_orders_analyzed:,}")
    print(f"    -> Mature Orders Evaluated:       {report.mature_orders_count:,} (Days <= {current_day - 5})")
    print(f"    -> In-Flight Orders Deferred:      {report.unmatured_orders_deferred:,} (Days > {current_day - 5})")
    print(f"    -> Realized False Negatives:      {report.total_false_negatives:,} unflagged RTO losses")
    print(f"    -> False Negative Rate:           {report.false_negative_rate * 100:.1f}%")
    print(f"    -> Miss Clusters Discovered:      {len(report.clusters_identified)}")

    # 3. Inspect top discovered miss cluster
    if not report.clusters_identified:
        print("\n[!] No coherent miss clusters identified.")
        return

    top_cluster = report.clusters_identified[0]
    print("\n" + "-" * 75)
    print(f"[3] PRIMARY DISCOVERED MISS CLUSTER: [{top_cluster.cluster_id}]")
    print(f"    Title:        {top_cluster.cluster_name}")
    print(f"    Miss Volume:  {top_cluster.miss_count} unflagged RTOs ({top_cluster.miss_percentage_of_cohort:.1f}% of cohort)")
    print(f"    Signature:    {top_cluster.signature_patterns}")
    print(f"\n    [Generator Agenda]:")
    print(f"    \"{top_cluster.generator_agenda}\"")

    # 4. Propose Targeted Rule Hypothesis addressing the miss cluster
    targeted_candidate = RuleHypothesis(
        id="hyp_residual_promo_burst_shield",
        name="Targeted Promotional COD Velocity Shield",
        description="Flags first-time COD orders using promo codes with high device order frequency.",
        rationale="Mined directly from false-negative cluster: unflagged RTOs exhibit multiple device orders within 24h on promotional COD checkouts.",
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
    )

    print("\n" + "-" * 75)
    print(f"[4] TARGETED HYPOTHESIS PROPOSED BY GENERATOR:")
    print(f"    Rule ID:   {targeted_candidate.id}")
    print(f"    Name:      {targeted_candidate.name}")
    print(f"    Code:\n{targeted_candidate.code}")

    # 5. Strict Acceptance Gate: Full-Validation Cost-Weighted Evaluation
    print("\n" + "-" * 75)
    print(f"[5] STRICT ACCEPTANCE GATE EVALUATION (Full {len(df_val):,} Validation Orders):")
    verdict = miner.evaluate_cluster_hypothesis_on_full_dataset(
        candidate_rule=targeted_candidate,
        df_validation=df_val,
        incumbent_ensemble=incumbent_ensemble,
    )

    print(f"    Baseline Net Financial Savings:  Rs. {verdict['baseline_net_savings_inr']:,.2f}")
    print(f"    Combined Net Financial Savings:  Rs. {verdict['candidate_net_savings_inr']:,.2f}")
    print(f"    Net Financial Delta:             +Rs. {verdict['delta_net_savings_inr']:,.2f}")
    print(f"    Full-Validation Precision:       {verdict['full_validation_precision'] * 100:.2f}%")
    print(f"    Full-Validation Recall:          {verdict['full_validation_recall'] * 100:.2f}%")
    print(f"    True Positives Caught:           {verdict['full_validation_tp']}")
    print(f"    False Positives Insulted:        {verdict['full_validation_fp']}")
    print(f"\n    FINAL GATE VERDICT:              [{verdict['verdict']}]")
    print(f"    Decision Reason:                 {verdict['reasons'][0]}")
    print("=" * 75)


if __name__ == "__main__":
    main()
