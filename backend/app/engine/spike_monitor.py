"""Real-Time Spike Monitor & Drift Detection Engine.

Tracks incoming live scoring events, computes rolling window flag rates,
and triggers statistical alerts using Z-score and CUSUM anomaly detection algorithms.
"""

from collections import deque
from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional
import numpy as np
from pydantic import BaseModel, Field


class AlertPayload(BaseModel):
    """Structured drift/spike alert generated when anomaly thresholds are breached."""
    alert_id: str
    timestamp: str
    severity: str  # "INFO", "WARNING", "CRITICAL_SPIKE"
    metric: str
    current_value: float
    threshold_value: float
    baseline_value: float
    message: str
    recommended_action: str


class MonitorSnapshot(BaseModel):
    """Current statistical snapshot of real-time traffic monitoring."""
    status: str  # "HEALTHY", "WARNING", "CRITICAL"
    total_orders_processed: int
    window_size: int
    current_flag_rate: float
    baseline_expected_rate: float
    z_score: float
    cusum_positive: float
    cusum_threshold: float
    active_alerts: List[AlertPayload]
    timestamp: str


class SpikeMonitor:
    """Sliding-window drift and anomaly detection engine."""

    def __init__(
        self,
        window_size: int = 50,
        baseline_rate: float = 0.08,
        z_threshold: float = 2.5,
        cusum_k: float = 0.02,
        cusum_h: float = 0.15,
        warmup: bool = False,
    ):
        self.window_size = window_size
        self.baseline_rate = baseline_rate
        self.z_threshold = z_threshold
        self.cusum_k = cusum_k
        self.cusum_h = cusum_h

        self.order_history = deque(maxlen=window_size * 5)
        self.window_flags = deque(maxlen=window_size)
        self.cusum_pos: float = 0.0
        self.total_processed: int = 0
        self.alerts: List[AlertPayload] = []
        self.time_series_points: List[Dict[str, Any]] = []

        if warmup:
            self._warmup_baseline(count=60)

    def _warmup_baseline(self, count: int = 60) -> None:
        """Pre-populates baseline operational telemetry for immediate demo readiness."""
        np.random.seed(42)
        for i in range(count):
            is_flag = bool(np.random.rand() < self.baseline_rate)
            val = float(np.random.uniform(350.0, 2400.0))
            self.record_scoring_event(
                order_id=f"ORD_BASE_{1000 + i}",
                is_flagged=is_flag,
                order_value=val,
            )
        self.alerts = []
        self.cusum_pos = 0.0

    def record_scoring_event(
        self,
        order_id: str,
        is_flagged: bool,
        order_value: float,
        timestamp: Optional[str] = None,
    ) -> MonitorSnapshot:
        """Processes a single real-time order scoring event and updates sliding statistics."""
        self.total_processed += 1
        ts = timestamp or datetime.now(timezone.utc).isoformat()

        flag_val = 1 if is_flagged else 0
        self.window_flags.append(flag_val)
        self.order_history.append({
            "order_id": order_id,
            "is_flagged": is_flagged,
            "order_value": order_value,
            "timestamp": ts,
        })

        # Calculate sliding metrics
        current_n = len(self.window_flags)
        current_flag_rate = float(sum(self.window_flags) / current_n) if current_n > 0 else 0.0

        # Standard error under binomial baseline
        se = math.sqrt((self.baseline_rate * (1 - self.baseline_rate)) / max(current_n, 10))
        z_score = float((current_flag_rate - self.baseline_rate) / se) if se > 0 else 0.0

        # CUSUM update
        deviation = (flag_val - self.baseline_rate) - self.cusum_k
        self.cusum_pos = max(0.0, self.cusum_pos + deviation)

        # Check anomalies
        active_alerts: List[AlertPayload] = []
        status = "HEALTHY"

        if z_score >= self.z_threshold or self.cusum_pos >= self.cusum_h:
            status = "CRITICAL"
            alert = AlertPayload(
                alert_id=f"alert_spike_{self.total_processed}",
                timestamp=ts,
                severity="CRITICAL_SPIKE",
                metric="flag_rate_zscore",
                current_value=round(current_flag_rate, 4),
                threshold_value=round(self.baseline_rate + self.z_threshold * se, 4),
                baseline_value=self.baseline_rate,
                message=f"Severe fraud flag rate spike detected: {current_flag_rate*100:.1f}% (Z-Score: {z_score:.2f}, CUSUM: {self.cusum_pos:.2f})",
                recommended_action="Trigger autonomous background evolution to synthesize adapted defense rules.",
            )
            active_alerts.append(alert)
            self.alerts.append(alert)
        elif z_score >= (self.z_threshold * 0.7):
            status = "WARNING"
            alert = AlertPayload(
                alert_id=f"alert_warn_{self.total_processed}",
                timestamp=ts,
                severity="WARNING",
                metric="flag_rate_zscore",
                current_value=round(current_flag_rate, 4),
                threshold_value=round(self.baseline_rate + (self.z_threshold * 0.7) * se, 4),
                baseline_value=self.baseline_rate,
                message=f"Elevated fraud flag rate: {current_flag_rate*100:.1f}% (Z-Score: {z_score:.2f})",
                recommended_action="Monitor rolling distribution for systemic attack emergence.",
            )
            active_alerts.append(alert)

        snapshot = MonitorSnapshot(
            status=status,
            total_orders_processed=self.total_processed,
            window_size=current_n,
            current_flag_rate=round(current_flag_rate, 4),
            baseline_expected_rate=self.baseline_rate,
            z_score=round(z_score, 2),
            cusum_positive=round(self.cusum_pos, 4),
            cusum_threshold=self.cusum_h,
            active_alerts=active_alerts,
            timestamp=ts,
        )

        # Record time series point
        self.time_series_points.append({
            "step": self.total_processed,
            "timestamp": ts,
            "flag_rate": round(current_flag_rate, 4),
            "baseline": self.baseline_rate,
            "upper_bound": round(self.baseline_rate + self.z_threshold * se, 4),
            "z_score": round(z_score, 2),
            "status": status,
        })

        return snapshot

    def get_current_status(self) -> MonitorSnapshot:
        """Returns the latest monitoring snapshot."""
        current_n = len(self.window_flags)
        current_flag_rate = float(sum(self.window_flags) / current_n) if current_n > 0 else 0.0
        se = math.sqrt((self.baseline_rate * (1 - self.baseline_rate)) / max(current_n, 10))
        z_score = float((current_flag_rate - self.baseline_rate) / se) if se > 0 else 0.0

        status = "HEALTHY"
        if z_score >= self.z_threshold or self.cusum_pos >= self.cusum_h:
            status = "CRITICAL"
        elif z_score >= (self.z_threshold * 0.7):
            status = "WARNING"

        return MonitorSnapshot(
            status=status,
            total_orders_processed=self.total_processed,
            window_size=current_n,
            current_flag_rate=round(current_flag_rate, 4),
            baseline_expected_rate=self.baseline_rate,
            z_score=round(z_score, 2),
            cusum_positive=round(self.cusum_pos, 4),
            cusum_threshold=self.cusum_h,
            active_alerts=self.alerts[-5:],
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Returns recent time-series trajectory points for dashboard charting."""
        return self.time_series_points[-limit:]


# Global singleton instance for app runtime
global_spike_monitor = SpikeMonitor(warmup=True)
