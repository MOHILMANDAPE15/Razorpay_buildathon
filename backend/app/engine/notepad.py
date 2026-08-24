"""Notepad persistent memory for hypothesis history, lineage tracking, and fitness trajectories."""

import json
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.engine.types import EvaluationReport, RuleHypothesis


class HypothesisRecord(BaseModel):
    """Internal memory record for a registered hypothesis."""
    hypothesis: RuleHypothesis
    latest_report: Optional[EvaluationReport] = None
    all_reports: List[EvaluationReport] = Field(default_factory=list)


class Notepad:
    """Persistent memory store tracking the full evolution trajectory, rule lineages,
    and performance history across generations."""

    def __init__(self):
        self.registry: Dict[str, HypothesisRecord] = {}
        self.lineage_graph: Dict[str, List[str]] = {}  # parent_id -> list of child_ids

    def add_hypothesis(self, hypothesis: RuleHypothesis) -> None:
        """Registers a new hypothesis in memory."""
        if hypothesis.id not in self.registry:
            self.registry[hypothesis.id] = HypothesisRecord(hypothesis=hypothesis)
            
        # Update lineage
        for pid in hypothesis.parent_ids:
            if pid not in self.lineage_graph:
                self.lineage_graph[pid] = []
            if hypothesis.id not in self.lineage_graph[pid]:
                self.lineage_graph[pid].append(hypothesis.id)

    def record_evaluation(self, report: EvaluationReport) -> None:
        """Records an evaluation report against an existing hypothesis."""
        if report.hypothesis_id in self.registry:
            record = self.registry[report.hypothesis_id]
            record.latest_report = report
            record.all_reports.append(report)

    def get_hypothesis(self, hyp_id: str) -> Optional[RuleHypothesis]:
        """Retrieves a hypothesis by ID."""
        record = self.registry.get(hyp_id)
        return record.hypothesis if record else None

    def get_latest_report(self, hyp_id: str) -> Optional[EvaluationReport]:
        """Retrieves the latest evaluation report for a hypothesis."""
        record = self.registry.get(hyp_id)
        return record.latest_report if record else None

    def get_all_hypotheses(self) -> List[RuleHypothesis]:
        """Returns all hypotheses in the registry."""
        return [record.hypothesis for record in self.registry.values()]

    def get_top_hypotheses(self, top_k: int = 5) -> List[Tuple[RuleHypothesis, EvaluationReport]]:
        """Returns the top-K hypotheses ranked by net financial savings (INR)."""
        evaluated_records = [
            (rec.hypothesis, rec.latest_report)
            for rec in self.registry.values()
            if rec.latest_report and rec.latest_report.is_valid and rec.latest_report.cost_metrics
        ]
        
        # Sort descending by net financial savings
        sorted_records = sorted(
            evaluated_records,
            key=lambda item: item[1].cost_metrics.net_financial_savings_inr,
            reverse=True,
        )
        return sorted_records[:top_k]

    def get_history_summary_for_generator(self, max_entries: int = 5) -> str:
        """Constructs a concise summary of past successes and failures to inform the Generator."""
        if not self.registry:
            return "No previous hypotheses tested yet (Cold Start Round)."

        top_items = self.get_top_hypotheses(top_k=max_entries)
        
        summary_lines = ["### Past Evolution History (What Worked vs What Failed):"]
        
        if top_items:
            summary_lines.append("\n**Top Performing Rules (Highest Net ₹ Savings):**")
            for hyp, rep in top_items:
                cm = rep.cost_metrics
                sm = rep.standard_metrics
                summary_lines.append(
                    f"- Rule [{hyp.id}] '{hyp.name}': Net Impact ₹{cm.net_financial_savings_inr:,.0f} | "
                    f"Precision {sm.precision*100:.1f}% | Recall {sm.recall*100:.1f}% | Signal: {hyp.target_signal or 'custom'}"
                )

        # Include recent failures/pruned
        failures = [
            (rec.hypothesis, rec.latest_report)
            for rec in self.registry.values()
            if rec.latest_report and (
                not rec.latest_report.is_valid
                or (rec.latest_report.cost_metrics and rec.latest_report.cost_metrics.net_financial_savings_inr < 0)
            )
        ]
        if failures:
            summary_lines.append("\n**Underperforming / Negative Value Rules to Avoid Repeating:**")
            for hyp, rep in failures[-3:]:
                if not rep.is_valid:
                    summary_lines.append(f"- Rule [{hyp.id}] '{hyp.name}': Execution Failed ({rep.error_message})")
                else:
                    cm = rep.cost_metrics
                    summary_lines.append(
                        f"- Rule [{hyp.id}] '{hyp.name}': Net Loss ₹{cm.net_financial_savings_inr:,.0f} "
                        f"(Excessive False Alarms burned profit)"
                    )

        return "\n".join(summary_lines)

    def prune_unselected(self, active_ids: List[str]) -> None:
        """Marks hypotheses not in active_ids as 'pruned' (archived, not deleted)."""
        for hyp_id, record in self.registry.items():
            if hyp_id not in active_ids and record.hypothesis.status == "alive":
                record.hypothesis.status = "pruned"

    def sync_to_db(self, db_session=None, run_id: Optional[str] = None) -> None:
        """Persists all hypotheses, lineages, and evaluation reports in memory into PostgreSQL."""
        from app.db.session import get_db
        from app.db.models import (
            Hypothesis as HypothesisModel,
            HypothesisLineage as HypothesisLineageModel,
            EvaluationReportModel,
        )

        should_close = False
        if db_session is None:
            try:
                db_session = next(get_db())
                should_close = True
            except Exception as e:
                # If database is offline/unreachable in testing, fail gracefully
                return

        try:
            for hyp_id, rec in self.registry.items():
                hyp = rec.hypothesis
                existing = db_session.query(HypothesisModel).filter_by(hypothesis_id=hyp.id).first()
                if existing:
                    existing.status = hyp.status
                    existing.generation_round = hyp.generation_round
                    existing.name = hyp.name
                    existing.rule_code = hyp.code
                    existing.description = hyp.description
                    existing.rationale = hyp.rationale
                    existing.target_signal = hyp.target_signal
                    if run_id and not existing.run_id:
                        existing.run_id = run_id
                else:
                    db_hyp = HypothesisModel(
                        hypothesis_id=hyp.id,
                        run_id=run_id,
                        generation_round=hyp.generation_round,
                        name=hyp.name,
                        target_signal=hyp.target_signal,
                        description=hyp.description,
                        rationale=hyp.rationale,
                        rule_code=hyp.code,
                        status=hyp.status,
                    )
                    db_session.add(db_hyp)
                db_session.flush()

                # Persist lineages
                for pid in hyp.parent_ids:
                    existing_lin = db_session.query(HypothesisLineageModel).filter_by(
                        parent_hypothesis_id=pid,
                        child_hypothesis_id=hyp.id,
                    ).first()
                    if not existing_lin:
                        # Ensure parent exists in DB before creating lineage foreign key
                        parent_in_db = db_session.query(HypothesisModel).filter_by(hypothesis_id=pid).first()
                        if parent_in_db:
                            lin = HypothesisLineageModel(
                                parent_hypothesis_id=pid,
                                child_hypothesis_id=hyp.id,
                                relationship_type="mutated_from",
                                mutation_strategy=hyp.description or "Evolved mutation",
                            )
                            db_session.add(lin)

                # Persist evaluation reports
                for rep in rec.all_reports:
                    if rep.is_valid and rep.standard_metrics and rep.cost_metrics:
                        sm = rep.standard_metrics
                        cm = rep.cost_metrics
                        split_name = getattr(rep, "dataset_split", None) or "validation"
                        existing_rep = db_session.query(EvaluationReportModel).filter_by(
                            hypothesis_id=hyp.id,
                            dataset_split=split_name,
                        ).first()
                        if not existing_rep:
                            db_rep = EvaluationReportModel(
                                hypothesis_id=hyp.id,
                                dataset_split=split_name,
                                precision=sm.precision,
                                recall=sm.recall,
                                f1_score=sm.f1,
                                accuracy=sm.accuracy,
                                flag_rate=sm.flag_rate,
                                total_orders=sm.total_orders,
                                true_positives=sm.true_positives,
                                false_positives=sm.false_positives,
                                true_negatives=sm.true_negatives,
                                false_negatives=sm.false_negatives,
                                avoided_rto_loss_inr=cm.avoided_rto_loss_inr,
                                false_positive_insult_cost_inr=cm.false_positive_insult_cost_inr,
                                net_financial_savings_inr=cm.net_financial_savings_inr,
                                cost_efficiency_ratio=cm.cost_efficiency_ratio,
                                gate_1_status=getattr(rep, "gate_status", "PASSED") or "PASSED",
                                gate_1_reasons=getattr(rep, "gate_reasons", []) or [],
                            )
                            db_session.add(db_rep)

            db_session.commit()
        except Exception as e:
            db_session.rollback()
            print(f"[Notepad] Error syncing to DB: {e}")
        finally:
            if should_close:
                db_session.close()
