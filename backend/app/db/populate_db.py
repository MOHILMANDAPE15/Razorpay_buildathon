"""Database Population & Sync Script for Aegis-RTO.

Populates PostgreSQL database (aegis_rto) with:
1. Evolution Runs (evolution_runs)
2. Generated Hypotheses (hypotheses)
3. Mutation Lineages (hypothesis_lineages)
4. Evaluator Reports (evaluation_reports)
5. Online Scoring Logs (scoring_logs)
"""

import json
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

from app.db.session import get_db
from app.db.models import (
    EvolutionRun,
    Hypothesis as HypothesisModel,
    HypothesisLineage as HypothesisLineageModel,
    EvaluationReportModel,
    ScoringLog,
)
from app.agents.runner import EvolutionRunner
from app.data.loader import load_train_data, load_validation_data
from app.core.sandbox import execute_rule_sandboxed
from app.engine.evaluator import CostWeightedEvaluator


def populate_database():
    """Populates PostgreSQL tables with evolution history, live runs, and scoring logs."""
    print("=" * 70)
    print("AEGIS-RTO: Populating PostgreSQL Database (aegis_rto)")
    print("=" * 70)

    db = next(get_db())
    evaluator = CostWeightedEvaluator()
    df_train = load_train_data()
    df_val = load_validation_data()

    # 1. Sync Frozen Snapshot Rule (Section 4.7)
    snapshot_path = Path(__file__).resolve().parent.parent / "engine" / "v1_frozen_rules_snapshot.json"
    if snapshot_path.exists():
        with open(snapshot_path, "r", encoding="utf-8") as f:
            snap_data = json.load(f)

        print("[DB Sync] Ingesting Section 4.7 Frozen Rule Ensemble...")
        run_id = "run_section_4_7_frozen_v1"
        existing_run = db.query(EvolutionRun).filter_by(run_id=run_id).first()
        if not existing_run:
            db_run = EvolutionRun(
                run_id=run_id,
                total_rounds=snap_data.get("n_rounds", 3),
                hypotheses_tested=snap_data.get("hypotheses_evaluated", 14),
                final_best_net_savings_inr=snap_data.get("performance_train_pre_drift", {}).get("net_financial_savings_inr", -76288.01),
                champion_hypothesis_id=snap_data.get("selected_rules", [{}])[0].get("id", "hyp_r2_mut_5966"),
                status="COMPLETED",
            )
            db.add(db_run)
            db.commit()

        for rule in snap_data.get("selected_rules", []):
            rule_id = rule["id"]
            existing = db.query(HypothesisModel).filter_by(hypothesis_id=rule_id).first()
            if not existing:
                db_hyp = HypothesisModel(
                    hypothesis_id=rule_id,
                    run_id=run_id,
                    generation_round=rule.get("generation_round", 2),
                    name=rule["name"],
                    target_signal=rule.get("target_signal", "night_rto_promo"),
                    description=rule.get("description", ""),
                    rationale=rule.get("rationale", ""),
                    rule_code=rule["code"],
                    status="champion",
                )
                db.add(db_hyp)
                db.flush()

                # Evaluate and add evaluation reports
                try:
                    flags_train = execute_rule_sandboxed(rule["code"], df_train)
                    rep_train = evaluator.evaluate_flags(flags_train, df_train, rule_id, rule["name"])
                    db_rep_train = EvaluationReportModel(
                        hypothesis_id=rule_id,
                        dataset_split="train",
                        precision=rep_train.standard_metrics.precision,
                        recall=rep_train.standard_metrics.recall,
                        f1_score=rep_train.standard_metrics.f1,
                        accuracy=rep_train.standard_metrics.accuracy,
                        flag_rate=rep_train.standard_metrics.flag_rate,
                        total_orders=rep_train.standard_metrics.total_orders,
                        true_positives=rep_train.standard_metrics.true_positives,
                        false_positives=rep_train.standard_metrics.false_positives,
                        true_negatives=rep_train.standard_metrics.true_negatives,
                        false_negatives=rep_train.standard_metrics.false_negatives,
                        avoided_rto_loss_inr=rep_train.cost_metrics.avoided_rto_loss_inr,
                        false_positive_insult_cost_inr=rep_train.cost_metrics.false_positive_insult_cost_inr,
                        net_financial_savings_inr=rep_train.cost_metrics.net_financial_savings_inr,
                        cost_efficiency_ratio=rep_train.cost_metrics.cost_efficiency_ratio,
                    )
                    db.add(db_rep_train)

                    flags_val = execute_rule_sandboxed(rule["code"], df_val)
                    rep_val = evaluator.evaluate_flags(flags_val, df_val, rule_id, rule["name"])
                    db_rep_val = EvaluationReportModel(
                        hypothesis_id=rule_id,
                        dataset_split="validation",
                        precision=rep_val.standard_metrics.precision,
                        recall=rep_val.standard_metrics.recall,
                        f1_score=rep_val.standard_metrics.f1,
                        accuracy=rep_val.standard_metrics.accuracy,
                        flag_rate=rep_val.standard_metrics.flag_rate,
                        total_orders=rep_val.standard_metrics.total_orders,
                        true_positives=rep_val.standard_metrics.true_positives,
                        false_positives=rep_val.standard_metrics.false_positives,
                        true_negatives=rep_val.standard_metrics.true_negatives,
                        false_negatives=rep_val.standard_metrics.false_negatives,
                        avoided_rto_loss_inr=rep_val.cost_metrics.avoided_rto_loss_inr,
                        false_positive_insult_cost_inr=rep_val.cost_metrics.false_positive_insult_cost_inr,
                        net_financial_savings_inr=rep_val.cost_metrics.net_financial_savings_inr,
                        cost_efficiency_ratio=rep_val.cost_metrics.cost_efficiency_ratio,
                    )
                    db.add(db_rep_val)
                except Exception as e:
                    print(f"  [DB Sync] Eval note: {e}")

        db.commit()

    # 2. Run Autonomous Evolution Loop (generates live run, hypotheses, lineages, and reports)
    print("\n[DB Sync] Running 2-round autonomous self-evolution loop to populate database...")
    runner = EvolutionRunner()
    summary = runner.run_evolution(rounds=2, hypotheses_per_round=2, df_validation=df_val)
    print(f"  -> Generated {summary.total_hypotheses_tested} hypotheses across {summary.total_rounds} rounds.")

    # 3. Populate Sample Scoring Logs
    print("\n[DB Sync] Generating sample scoring logs for online inference audit...")
    champion_hyp = db.query(HypothesisModel).filter_by(status="alive").first()
    if champion_hyp:
        sample_orders = df_val.head(20)
        try:
            flags = execute_rule_sandboxed(champion_hyp.rule_code, sample_orders)
            for idx, (_, row) in enumerate(sample_orders.iterrows()):
                is_flagged = bool(flags[idx]) if idx < len(flags) else False
                log = ScoringLog(
                    order_id=str(row["order_id"]),
                    active_hypothesis_id=champion_hyp.hypothesis_id,
                    risk_score=0.85 if is_flagged else 0.15,
                    decision="FLAG_FOR_REVIEW" if is_flagged else "APPROVE_COD",
                    decision_latency_ms=12.4,
                    is_flagged=is_flagged,
                    ground_truth_outcome="CONFIRMED_RTO" if row["is_rto"] == 1 else "DELIVERED",
                )
                db.add(log)
            db.commit()
        except Exception as e:
            print(f"  [DB Sync] Scoring log note: {e}")

    # 4. Print summary counts
    print("\n" + "=" * 70)
    print("FINAL DATABASE TABLE COUNTS:")
    print("=" * 70)
    tables = [
        "orders_train",
        "orders_validation",
        "orders_held_out_test",
        "evolution_runs",
        "hypotheses",
        "hypothesis_lineages",
        "evaluation_reports",
        "scoring_logs",
    ]
    from sqlalchemy import text
    for tbl in tables:
        count = db.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
        print(f"  -> {tbl:25s}: {count:6d} rows")

    db.close()


if __name__ == "__main__":
    populate_database()
