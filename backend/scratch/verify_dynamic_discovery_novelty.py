"""Novelty Verification Script: Dynamic Residual Mining vs Static Fallback Baseline.

Runs the dynamic subgroup miner restricted to the post-drift validation window (Days 56–75)
with static_fallback_clusters() disabled (mode="dynamic"). Compares discovered cluster signatures
against the three original hand-coded static patterns to verify genuine automated pattern discovery.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.data.loader import load_validation_data
from app.engine.frozen_rule_snapshot import load_frozen_v1_rules
from app.engine.residual_miner import ResidualMiner
from app.engine.selector import EnsembleRule


def main():
    print("=" * 80)
    print("AEGIS-RTO: DYNAMIC DISCOVERY NOVELTY VERIFICATION")
    print("=" * 80)

    # 1. Define the 3 original static baseline signatures for comparison
    STATIC_BASELINE_PATTERNS = {
        "cluster_promo_cod_burst": {
            "name": "Promotional COD Velocity (Static)",
            "signature_keys": {"payment_mode", "promo_code_used"},
        },
        "cluster_late_night_impulse": {
            "name": "Late-Night Pincode COD (Static)",
            "signature_keys": {"payment_mode", "order_hours", "min_pincode_rto_rate"},
        },
        "cluster_low_value_impulse_cod": {
            "name": "Low-Value First-Time COD (Static)",
            "signature_keys": {"payment_mode", "max_order_value", "customer_prior_orders"},
        },
    }

    # 2. Load post-drift validation data (Days 56–75)
    df_val = load_validation_data()
    v1_rules = load_frozen_v1_rules()
    incumbent_ensemble = EnsembleRule(v1_rules)
    current_day = int(df_val["day_index"].max())

    print(f"\n[1] Evaluating Post-Drift Distribution ({len(df_val):,} orders, Days 56–75)...")
    print(f"    Mode: DYNAMIC SUBGROUP MINER (Static fallback disabled)")

    # 3. Run Residual Miner strictly in DYNAMIC mode
    miner = ResidualMiner(
        maturity_window_days=5,
        min_cluster_size=10,
        min_cohort_size=30,
        max_conjunction_depth=3,
        significance_alpha=0.05,
        mode="dynamic",
    )
    report = miner.run_residual_analysis(df_val, incumbent_ensemble, current_day_index=current_day)

    print(f"\n[2] Discovery Results:")
    print(f"    -> Realized False Negatives Mined: {report.total_false_negatives:,}")
    print(f"    -> Dynamically Discovered Clusters: {len(report.clusters_identified)}")
    print(f"    -> Insignificant Candidates Filtered: {len(report.rejected_insignificant_clusters)}")

    # 4. Compare each discovered cluster against the static baseline
    matched_clusters = []
    novel_clusters = []

    for cluster in report.clusters_identified:
        cluster_keys = set(cluster.signature_patterns.keys())
        matched_static_id = None

        for static_id, static_meta in STATIC_BASELINE_PATTERNS.items():
            if static_meta["signature_keys"] == cluster_keys or static_meta["signature_keys"].issubset(cluster_keys):
                matched_static_id = static_id
                break

        if matched_static_id:
            matched_clusters.append((cluster, STATIC_BASELINE_PATTERNS[matched_static_id]["name"]))
        else:
            novel_clusters.append(cluster)

    # 5. Print Comparison Summary
    print("\n" + "-" * 80)
    print("A. REPRODUCED / REFINED BASELINE PATTERNS (Statistical Verification):")
    if matched_clusters:
        for cl, static_name in matched_clusters:
            print(f"    * [{cl.cluster_id}] '{cl.cluster_name}'")
            print(f"      Matched Against: {static_name}")
            print(f"      Miss Volume:     {cl.miss_count} orders (Lift: {cl.statistical_lift}x, p-value: {cl.p_value})")
            print(f"      Signature:       {cl.signature_patterns}")
    else:
        print("    (None)")

    print("\n" + "-" * 80)
    print("B. NOVEL DISCOVERED ABUSE PATTERNS (Beyond Static Fallback):")
    if novel_clusters:
        for cl in novel_clusters:
            print(f"    * [NOVEL] [{cl.cluster_id}] '{cl.cluster_name}'")
            print(f"      Novelty Status:  DISCOVERED AUTONOMOUSLY (No hand-coded static equivalent)")
            print(f"      Miss Volume:     {cl.miss_count} orders (Lift: {cl.statistical_lift}x, p-value: {cl.p_value})")
            print(f"      Conjunctions:    Depth {cl.conjunction_depth} (<= 3 feature cap)")
            print(f"      Signature:       {cl.signature_patterns}")
            print(f"      Agenda String:   \"{cl.generator_agenda}\"")
    else:
        print("    (All discovered patterns refined existing dimensions)")


    print("\n" + "=" * 80)
    print(f"NOVELTY VERIFICATION SUMMARY:")
    print(f"Total Discovered: {len(report.clusters_identified)} | Matched/Refined: {len(matched_clusters)} | Novel: {len(novel_clusters)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
