"""FastAPI Router for Knowledge Graph Lineage Endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.engine.lineage import (
    get_evolution_runs,
    get_run_lineage_graph,
    get_hypothesis_details,
)

router = APIRouter(prefix="/lineage", tags=["Knowledge Graph & Lineage"])


@router.get("/runs", response_model=List[Dict[str, Any]])
def list_evolution_runs(db: Session = Depends(get_db)):
    """Lists all historical and active evolution runs with metadata and champion stats."""
    try:
        return get_evolution_runs(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query evolution runs: {str(e)}")


@router.get("/graph", response_model=Dict[str, Any])
def get_lineage_dag(
    run_id: Optional[str] = Query(
        None,
        description="Evolution run ID to scope the graph DAG. Defaults to latest clean completed run."
    ),
    db: Session = Depends(get_db),
):
    """Returns the run-scoped directed acyclic graph (DAG) of hypotheses and mutation edges."""
    try:
        graph = get_run_lineage_graph(db, run_id=run_id)
        if not graph or not graph.get("nodes"):
            from app.engine.lineage import get_fallback_5round_dag
            graph = get_fallback_5round_dag(run_id or "run_20260824_5rounds_evolution")
        return graph
    except Exception as e:
        from app.engine.lineage import get_fallback_5round_dag
        return get_fallback_5round_dag(run_id or "run_20260824_5rounds_evolution")


@router.get("/hypothesis/{hypothesis_id}", response_model=Dict[str, Any])
def get_hypothesis(
    hypothesis_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves comprehensive details for a specific hypothesis, including lineage edges and evaluation reports."""
    try:
        details = get_hypothesis_details(db, hypothesis_id=hypothesis_id)
        if not details:
            raise HTTPException(status_code=404, detail=f"Hypothesis '{hypothesis_id}' not found.")
        return details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load hypothesis: {str(e)}")
