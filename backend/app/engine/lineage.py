"""Knowledge Graph Lineage Engine for Aegis-RTO.

Queries PostgreSQL for evolution runs, hypotheses, mutation edges, and evaluation reports.
Builds run-scoped Directed Acyclic Graph (DAG) structures for visualization and analysis.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models import EvolutionRun, Hypothesis, HypothesisLineage, EvaluationReportModel


def get_evolution_runs(db: Session) -> List[Dict[str, Any]]:
    """Retrieves all registered evolution runs sorted by started_at descending."""
    runs = db.query(EvolutionRun).order_by(desc(EvolutionRun.started_at)).all()
    results = []
    for r in runs:
        hyps_count = db.query(Hypothesis).filter_by(run_id=r.run_id).count()
        results.append({
            "run_id": r.run_id,
            "status": r.status,
            "total_rounds": r.total_rounds,
            "hypotheses_tested": r.hypotheses_tested or hyps_count,
            "initial_best_net_savings_inr": float(r.initial_best_net_savings_inr or 0.0),
            "final_best_net_savings_inr": float(r.final_best_net_savings_inr or 0.0),
            "net_savings_delta_inr": float(r.net_savings_delta_inr or 0.0),
            "champion_hypothesis_id": r.champion_hypothesis_id,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        })
    return results


def get_run_lineage_graph(db: Session, run_id: Optional[str] = None) -> Dict[str, Any]:
    """Builds a run-scoped DAG containing hypothesis nodes and mutation edges.
    
    If run_id is not provided, defaults to the latest completed evolution run with hypotheses,
    or the latest overall run.
    
    Args:
        db: Active SQLAlchemy Session.
        run_id: Optional evolution run ID to scope the graph.
        
    Returns:
        Dict with 'run_id', 'run_summary', 'nodes', 'edges', and 'rounds'.
    """
    # 1. Resolve run_id
    if not run_id:
        latest_run = (
            db.query(EvolutionRun)
            .filter(EvolutionRun.status == "COMPLETED")
            .order_by(desc(EvolutionRun.started_at))
            .first()
        )
        if not latest_run:
            latest_run = db.query(EvolutionRun).order_by(desc(EvolutionRun.started_at)).first()
        
        if latest_run:
            run_id = latest_run.run_id
        else:
            sample_hyp = db.query(Hypothesis).first()
            if sample_hyp and sample_hyp.run_id:
                run_id = sample_hyp.run_id

    # 2. Query run metadata
    run_obj = db.query(EvolutionRun).filter_by(run_id=run_id).first() if run_id else None
    
    # 3. Query hypotheses for this run
    if run_id:
        hyps = db.query(Hypothesis).filter_by(run_id=run_id).order_by(Hypothesis.generation_round).all()
    else:
        hyps = db.query(Hypothesis).order_by(Hypothesis.generation_round).all()

    if not hyps and run_id:
        fallback_hyp = db.query(Hypothesis).filter(Hypothesis.run_id.isnot(None)).first()
        if fallback_hyp:
            run_id = fallback_hyp.run_id
            run_obj = db.query(EvolutionRun).filter_by(run_id=run_id).first()
            hyps = db.query(Hypothesis).filter_by(run_id=run_id).order_by(Hypothesis.generation_round).all()

    hyp_ids = {h.hypothesis_id for h in hyps}

    # 4. Query mutation lineages scoped to these hypotheses
    lineages = []
    if hyp_ids:
        lineages = (
            db.query(HypothesisLineage)
            .filter(
                HypothesisLineage.parent_hypothesis_id.in_(hyp_ids) |
                HypothesisLineage.child_hypothesis_id.in_(hyp_ids)
            )
            .all()
        )

    # 5. Build nodes dictionary with latest evaluation report
    nodes = []
    rounds_set = set()
    parent_map: Dict[str, List[str]] = {h_id: [] for h_id in hyp_ids}
    child_map: Dict[str, List[str]] = {h_id: [] for h_id in hyp_ids}

    for l in lineages:
        if l.child_hypothesis_id in parent_map and l.parent_hypothesis_id not in parent_map[l.child_hypothesis_id]:
            parent_map[l.child_hypothesis_id].append(l.parent_hypothesis_id)
        if l.parent_hypothesis_id in child_map and l.child_hypothesis_id not in child_map[l.parent_hypothesis_id]:
            child_map[l.parent_hypothesis_id].append(l.child_hypothesis_id)

    for h in hyps:
        rounds_set.add(h.generation_round)
        eval_rep = (
            db.query(EvaluationReportModel)
            .filter_by(hypothesis_id=h.hypothesis_id)
            .order_by(desc(EvaluationReportModel.report_id))
            .first()
        )

        is_champ = (h.status == "champion") or (run_obj and run_obj.champion_hypothesis_id == h.hypothesis_id)

        # Discovery Type Tagging: hand_coded, mutated, autonomous_discovery
        h_id_lower = h.hypothesis_id.lower()
        h_desc_lower = (h.description or "").lower()
        h_target_lower = (h.target_signal or "").lower()
        if (
            "dyn" in h_id_lower
            or "autonomous" in h_desc_lower
            or "cluster_dyn" in h_id_lower
            or "dynamic" in h_target_lower
            or h.hypothesis_id == "cluster_dyn_new_account_high_val_cod"
        ):
            disc_type = "autonomous_discovery"
        elif len(parent_map.get(h.hypothesis_id, [])) > 0 or (h.generation_round and h.generation_round > 1):
            disc_type = "mutated"
        else:
            disc_type = "hand_coded"

        node = {
            "id": h.hypothesis_id,
            "name": h.name,
            "generation_round": h.generation_round,
            "status": "champion" if is_champ else h.status,
            "discovery_type": disc_type,
            "target_signal": h.target_signal or "general",
            "description": h.description or "",
            "rationale": h.rationale or "",
            "rule_code": h.rule_code,
            "is_champion": is_champ,
            "parent_ids": parent_map.get(h.hypothesis_id, []),
            "child_ids": child_map.get(h.hypothesis_id, []),
            "created_at": h.created_at.isoformat() if h.created_at else None,
            "metrics": {
                "precision": float(eval_rep.precision) if eval_rep else 0.0,
                "recall": float(eval_rep.recall) if eval_rep else 0.0,
                "f1_score": float(eval_rep.f1_score) if eval_rep else 0.0,
                "flag_rate": float(eval_rep.flag_rate) if eval_rep else 0.0,
                "net_financial_savings_inr": float(eval_rep.net_financial_savings_inr) if eval_rep else 0.0,
                "dataset_split": eval_rep.dataset_split if eval_rep else "unknown",
            } if eval_rep else None,
        }
        nodes.append(node)

    # 6. Build edges list
    edges = []
    for l in lineages:
        if l.parent_hypothesis_id in hyp_ids and l.child_hypothesis_id in hyp_ids:
            edges.append({
                "id": f"edge_{l.id}",
                "source": l.parent_hypothesis_id,
                "target": l.child_hypothesis_id,
                "relationship_type": l.relationship_type,
                "mutation_strategy": l.mutation_strategy or "",
                "created_at": l.created_at.isoformat() if l.created_at else None,
            })

    best_net = max([n["metrics"]["net_financial_savings_inr"] for n in nodes if n["metrics"]], default=0.0)
    champions_count = sum(1 for n in nodes if n["is_champion"])

    return {
        "run_id": run_id,
        "run_summary": {
            "run_id": run_id,
            "status": run_obj.status if run_obj else "COMPLETED",
            "champion_hypothesis_id": run_obj.champion_hypothesis_id if run_obj else (
                [n["id"] for n in nodes if n["is_champion"]][0] if champions_count > 0 else None
            ),
            "final_best_net_savings_inr": float(run_obj.final_best_net_savings_inr) if run_obj and run_obj.final_best_net_savings_inr else best_net,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "total_rounds": len(rounds_set),
            "total_champions": champions_count,
        },
        "rounds": sorted(list(rounds_set)),
        "nodes": nodes,
        "edges": edges,
    }


def get_hypothesis_details(db: Session, hypothesis_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves exhaustive detail for a single hypothesis including code, lineages, and all split evals."""
    hyp = db.query(Hypothesis).filter_by(hypothesis_id=hypothesis_id).first()
    if not hyp:
        return None

    parent_edges = (
        db.query(HypothesisLineage)
        .filter_by(child_hypothesis_id=hypothesis_id)
        .all()
    )
    child_edges = (
        db.query(HypothesisLineage)
        .filter_by(parent_hypothesis_id=hypothesis_id)
        .all()
    )

    parent_nodes = [
        {
            "hypothesis_id": p.parent_hypothesis_id,
            "name": p.parent_hypothesis.name if p.parent_hypothesis else p.parent_hypothesis_id,
            "relationship_type": p.relationship_type,
            "mutation_strategy": p.mutation_strategy,
        }
        for p in parent_edges
    ]

    child_nodes = [
        {
            "hypothesis_id": c.child_hypothesis_id,
            "name": c.child_hypothesis.name if c.child_hypothesis else c.child_hypothesis_id,
            "relationship_type": c.relationship_type,
            "mutation_strategy": c.mutation_strategy,
        }
        for c in child_edges
    ]

    eval_reps = (
        db.query(EvaluationReportModel)
        .filter_by(hypothesis_id=hypothesis_id)
        .order_by(EvaluationReportModel.report_id)
        .all()
    )

    split_reports = [
        {
            "report_id": r.report_id,
            "dataset_split": r.dataset_split,
            "precision": float(r.precision),
            "recall": float(r.recall),
            "f1_score": float(r.f1_score),
            "flag_rate": float(r.flag_rate),
            "total_orders": r.total_orders,
            "true_positives": r.true_positives,
            "false_positives": r.false_positives,
            "avoided_rto_loss_inr": float(r.avoided_rto_loss_inr),
            "false_positive_insult_cost_inr": float(r.false_positive_insult_cost_inr),
            "net_financial_savings_inr": float(r.net_financial_savings_inr),
            "gate_1_status": r.gate_1_status,
        }
        for r in eval_reps
    ]

    return {
        "hypothesis_id": hyp.hypothesis_id,
        "run_id": hyp.run_id,
        "name": hyp.name,
        "generation_round": hyp.generation_round,
        "status": hyp.status,
        "target_signal": hyp.target_signal,
        "description": hyp.description,
        "rationale": hyp.rationale,
        "rule_code": hyp.rule_code,
        "created_at": hyp.created_at.isoformat() if hyp.created_at else None,
        "parents": parent_nodes,
        "children": child_nodes,
        "evaluation_reports": split_reports,
    }
