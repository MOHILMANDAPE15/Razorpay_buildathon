"""Unit and integration tests for Real-Time Spike Monitor Engine and API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.api.main import app
from app.engine.spike_monitor import SpikeMonitor

client = TestClient(app)


def test_spike_monitor_baseline_healthy():
    """Verifies that normal traffic with low flag rate stays in HEALTHY status."""
    monitor = SpikeMonitor(window_size=20, baseline_rate=0.08, z_threshold=2.5)

    # Feed 20 genuine orders
    for i in range(20):
        snap = monitor.record_scoring_event(order_id=f"ord_{i}", is_flagged=False, order_value=1000.0)

    assert snap.status == "HEALTHY"
    assert snap.current_flag_rate == 0.0
    assert len(snap.active_alerts) == 0


def test_spike_monitor_detects_critical_spike():
    """Verifies that a sudden surge in flagged orders triggers CRITICAL_SPIKE alert."""
    monitor = SpikeMonitor(window_size=20, baseline_rate=0.08, z_threshold=2.0, cusum_h=0.10)

    # Feed burst of 15 flagged orders
    for i in range(15):
        snap = monitor.record_scoring_event(order_id=f"burst_{i}", is_flagged=True, order_value=1200.0)

    assert snap.status in ["WARNING", "CRITICAL"]
    assert snap.current_flag_rate == 1.0
    assert len(snap.active_alerts) >= 1
    assert "alert_spike" in snap.active_alerts[0].alert_id
    assert "Trigger autonomous" in snap.active_alerts[0].recommended_action


def test_spike_monitor_api_endpoints():
    """Tests /api/v1/monitor REST endpoints."""
    # 1. GET /api/v1/monitor/status
    res = client.get("/api/v1/monitor/status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "baseline_expected_rate" in data

    # 2. POST /api/v1/monitor/event
    event_res = client.post(
        "/api/v1/monitor/event",
        json={"order_id": "test_api_01", "is_flagged": True, "order_value": 850.0},
    )
    assert event_res.status_code == 200
    snap = event_res.json()
    assert snap["total_orders_processed"] >= 1

    # 3. GET /api/v1/monitor/history
    hist_res = client.get("/api/v1/monitor/history?limit=10")
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert isinstance(history, list)

    # 4. POST /api/v1/monitor/simulate-traffic (Diagnostic replay)
    sim_res = client.post(
        "/api/v1/monitor/simulate-traffic",
        json={"total_events": 10, "spike_rate": 0.40, "order_value_mean": 1100.0},
    )
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert sim_data["status"] == "COMPLETED"
    assert sim_data["events_simulated"] == 10
