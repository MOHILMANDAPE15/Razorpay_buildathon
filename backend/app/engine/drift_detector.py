"""Realized Outcome Drift Detector (Sep 2 Milestone).

Tracks rolling windows of ACTUAL delivery outcomes (realized ground truth) to detect
true performance decay (precision collapse, ground-truth RTO surges, financial degradation)
and emit the official DRIFT_TRIGGER signal to launch re-evolution.

METHODOLOGICAL GUARANTEE:
Operates strictly on incoming streaming realized outcomes (orders_validation or live delivery logs).
NEVER accesses or touches held_out_test.csv.
"""

from collections import deque
from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional
import numpy as np
from pydantic import BaseModel, Field

from app.core.config import cost_config


class RealizedOrderOutcome(BaseModel):
    """An individual order with its model prediction and verified ground-truth outcome."""
    order_id: str
    predicted_flag: bool
    ground_truth_is_rto: int  # 1 = returned/fraud, 0 = genuine delivered
    order_value: float
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DriftSignal(BaseModel):
    """Structured drift alert payload emitted when true realized performance decays."""
    drift_detected: bool
    trigger_type: Optional[str] = None  # "PRECISION_COLLAPSE", "RTO_RATE_SURGE", "FINANCIAL_DEGRADATION"
    severity: str = "NORMAL"            # "NORMAL", "WARNING", "CRITICAL"
    window_size: int
    realized_precision: float
    baseline_precision: float
    realized_rto_rate: float
    baseline_rto_rate: float
    realized_net_savings_inr: float
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class OutcomeDriftDetector:
    """Sliding-window detector evaluating realized ground truth performance metrics."""

    def __init__(
        self,
        window_size: int = 100,
        baseline_precision: float = 0.30,
        baseline_rto_rate: float = 0.20,
        min_precision_ratio: float = 0.60,   # Trigger drift if precision drops < 60% of baseline
        max_rto_surge_sigma: float = 2.0,     # Trigger drift if ground-truth RTO rate surges > 2.0 sigma
    ):
        self.window_size = window_size
        self.baseline_precision = baseline_precision
        self.baseline_rto_rate = baseline_rto_rate
        self.min_precision_ratio = min_precision_ratio
        self.max_rto_surge_sigma = max_rto_surge_sigma

        self.outcome_history = deque(maxlen=window_size * 5)
        self.sliding_window = deque(maxlen=window_size)
        self.total_outcomes_processed: int = 0
        self.drift_signals: List[DriftSignal] = []

    def record_outcome(
        self,
        order_id: str,
        predicted_flag: bool,
        ground_truth_is_rto: int,
        order_value: float,
        timestamp: Optional[str] = None,
    ) -> DriftSignal:
        """Records an actual delivery outcome and evaluates the rolling window for distribution drift."""
        self.total_outcomes_processed += 1
        ts = timestamp or datetime.now(timezone.utc).isoformat()

        outcome = RealizedOrderOutcome(
            order_id=order_id,
            predicted_flag=predicted_flag,
            ground_truth_is_rto=int(ground_truth_is_rto),
            order_value=float(order_value),
            timestamp=ts,
        )

        self.sliding_window.append(outcome)
        self.outcome_history.append(outcome)

        return self.check_drift_status()

    def check_drift_status(self) -> DriftSignal:
        """Computes statistical metrics over the current sliding window of realized outcomes."""
        n = len(self.sliding_window)
        if n < min(20, self.window_size):
            # Not enough sample size to reliably detect statistical drift
            return DriftSignal(
                drift_detected=False,
                severity="NORMAL",
                window_size=n,
                realized_precision=self.baseline_precision,
                baseline_precision=self.baseline_precision,
                realized_rto_rate=self.baseline_rto_rate,
                baseline_rto_rate=self.baseline_rto_rate,
                realized_net_savings_inr=0.0,
                message="Warming up sliding window.",
            )

        # Compute realized confusion matrix & financial impact
        tp = sum(1 for o in self.sliding_window if o.predicted_flag and o.ground_truth_is_rto == 1)
        fp = sum(1 for o in self.sliding_window if o.predicted_flag and o.ground_truth_is_rto == 0)
        flagged = tp + fp
        actual_rtos = sum(1 for o in self.sliding_window if o.ground_truth_is_rto == 1)

        realized_precision = float(tp / flagged) if flagged > 0 else self.baseline_precision
        realized_rto_rate = float(actual_rtos / n)

        # Financial formula on realized window
        avoided_rto_inr = float(tp * cost_config.avoided_rto_cost_inr)
        fp_insult_cost_inr = float(
            sum(o.order_value * cost_config.fp_margin_loss_rate for o in self.sliding_window if o.predicted_flag and o.ground_truth_is_rto == 0)
        )
        realized_net_savings_inr = avoided_rto_inr - fp_insult_cost_inr

        # Statistical thresholds
        precision_threshold = self.baseline_precision * self.min_precision_ratio
        se_rto = math.sqrt((self.baseline_rto_rate * (1 - self.baseline_rto_rate)) / n)
        rto_surge_threshold = self.baseline_rto_rate + (self.max_rto_surge_sigma * se_rto)

        drift_detected = False
        trigger_type = None
        severity = "NORMAL"
        message = "Realized metrics within expected distribution bounds."

        # Condition 1: Severe Precision Collapse
        if flagged >= 5 and realized_precision < precision_threshold:
            drift_detected = True
            trigger_type = "PRECISION_COLLAPSE"
            severity = "CRITICAL"
            message = (
                f"Realized precision collapsed to {realized_precision*100:.1f}% "
                f"(baseline: {self.baseline_precision*100:.1f}%, threshold: {precision_threshold*100:.1f}%). "
                f"Rules are misclassifying shifted traffic."
            )

        # Condition 2: Ground-Truth RTO Surge
        elif realized_rto_rate > rto_surge_threshold:
            drift_detected = True
            trigger_type = "RTO_RATE_SURGE"
            severity = "CRITICAL"
            message = (
                f"Realized RTO rate surged to {realized_rto_rate*100:.1f}% "
                f"(baseline: {self.baseline_rto_rate*100:.1f}%, upper threshold: {rto_surge_threshold*100:.1f}%). "
                f"New fraud pattern evading existing rules."
            )

        # Condition 3: Realized Financial Net Loss
        elif flagged >= 5 and realized_net_savings_inr < 0:
            drift_detected = True
            trigger_type = "FINANCIAL_DEGRADATION"
            severity = "CRITICAL"
            message = (
                f"Realized net financial impact turned negative (₹{realized_net_savings_inr:,.2f}). "
                f"False positive insult costs exceed avoided RTO savings."
            )

        signal = DriftSignal(
            drift_detected=drift_detected,
            trigger_type=trigger_type,
            severity=severity,
            window_size=n,
            realized_precision=round(realized_precision, 4),
            baseline_precision=round(self.baseline_precision, 4),
            realized_rto_rate=round(realized_rto_rate, 4),
            baseline_rto_rate=round(self.baseline_rto_rate, 4),
            realized_net_savings_inr=round(realized_net_savings_inr, 2),
            message=message,
        )

        if drift_detected:
            self.drift_signals.append(signal)

        return signal