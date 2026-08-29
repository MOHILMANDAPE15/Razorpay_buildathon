"""FastAPI endpoints for Real-Time Spike Monitoring & Traffic Diagnostics."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.engine.spike_monitor import (
    AlertPayload,
    MonitorSnapshot,
    global_spike_monitor,
)

router = APIRouter(prefix="/monitor", tags=["Spike Monitor & Diagnostics"])


class ScoringEventRequest(BaseModel):
    """Payload for logging a live order scoring result."""
    order_id: str
    is_flagged: bool
    order_value: float
    timestamp: Optional[str] = None


class TrafficSimulationRequest(BaseModel):
    """Configuration for diagnostic traffic streaming replay."""
    total_events: int = Field(default=30, ge=1, le=200, description="Number of events to simulate")
    count: Optional[int] = Field(default=None, description="Alternative alias for total_events")
    spike_rate: float = Field(default=0.45, ge=0.0, le=1.0, description="Flag rate during the simulated burst")
    order_value_mean: float = Field(default=1250.0, description="Average order value")



@router.get("/status", response_model=MonitorSnapshot)
def get_monitor_status():
    """Returns real-time traffic health snapshot, rolling flag rate, Z-score, and active alerts."""
    return global_spike_monitor.get_current_status()


@router.get("/history", response_model=List[Dict[str, Any]])
def get_monitor_history(limit: int = Query(default=100, ge=10, le=500)):
    """Returns sliding window time series data points for real-time line charts."""
    return global_spike_monitor.get_history(limit=limit)


@router.post("/event", response_model=MonitorSnapshot)
def record_scoring_event(event: ScoringEventRequest):
    """Records an incoming live order scoring event and updates sliding statistical bounds."""
    snapshot = global_spike_monitor.record_scoring_event(
        order_id=event.order_id,
        is_flagged=event.is_flagged,
        order_value=event.order_value,
        timestamp=event.timestamp,
    )
    return snapshot


@router.post("/simulate-traffic")
def simulate_traffic(sim: TrafficSimulationRequest):
    """Diagnostic replay test harness for UI demos and drift response validation.

    Defense-only compliant: this simulates order streaming to test the spike detection engine
    without generating live fraudulent orders or mutating production policies.
    """
    import random
    snapshots = []
    events_to_run = sim.count if sim.count is not None else sim.total_events
    for i in range(events_to_run):
        is_flagged = random.random() < sim.spike_rate
        val = max(100.0, random.gauss(sim.order_value_mean, 300.0))
        snap = global_spike_monitor.record_scoring_event(
            order_id=f"sim_ord_{global_spike_monitor.total_processed + 1:04d}",
            is_flagged=is_flagged,
            order_value=round(val, 2),
        )
        snapshots.append(snap)


    return {
        "status": "COMPLETED",
        "events_simulated": events_to_run,
        "latest_snapshot": snapshots[-1],
        "active_alerts_count": len(global_spike_monitor.alerts),
    }
