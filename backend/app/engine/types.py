"""Data types and schemas for rule hypotheses, cost-weighted metrics, and regression reports."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RuleHypothesis(BaseModel):
    """Represents an executable fraud detection hypothesis."""
    id: str = Field(description="Unique identifier for the hypothesis (e.g. hyp_001)")
    name: str = Field(description="Short human-readable title of the rule")
    code: str = Field(description="Executable Python code containing a predict(df) function")
    description: str = Field(default="", description="Summary of the rule logic")
    rationale: str = Field(default="", description="Plain-English explanation of the causal fraud signal")
    target_signal: Optional[str] = Field(default=None, description="Primary targeted signal (e.g. promo_stacking, device_abuse)")
    generation_round: int = Field(default=0, description="Evolution round in which this rule was generated")
    parent_ids: List[str] = Field(default_factory=list, description="IDs of parent hypotheses if this was mutated/merged")
    status: str = Field(default="candidate", description="Status: candidate, alive, mutated, merged, pruned, dead")


class CostMetrics(BaseModel):
    """Cost-weighted financial impact metrics (in INR ₹)."""
    avoided_rto_loss_inr: float = Field(description="Total RTO loss prevented (TP * avoided_cost_per_order)")
    false_positive_insult_cost_inr: float = Field(description="Total merchant profit lost on genuine false alarms (sum of FP order_value * margin)")
    net_financial_savings_inr: float = Field(description="Net financial impact: Avoided Loss - False Positive Cost")
    cost_efficiency_ratio: float = Field(description="Ratio of avoided loss to false positive insult cost")
    avg_fp_insult_cost_inr: float = Field(default=0.0, description="Average insult cost per false positive order")


class StandardMetrics(BaseModel):
    """Standard statistical classification metrics."""
    precision: float
    recall: float
    f1: float
    accuracy: float
    total_orders: int
    flagged_orders: int
    flag_rate: float
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int


class DiagnosticOrder(BaseModel):
    """A concrete misclassified order passed to the Reflector LLM for error diagnosis."""
    order_id: str
    order_value: float
    true_label: int  # 1 for RTO, 0 for genuine
    predicted_label: int
    cost_impact_inr: float  # High insult cost for FP, or high order value for FN
    error_type: str  # "FALSE_POSITIVE" or "FALSE_NEGATIVE"
    features: Dict[str, Any]  # Sanitized feature dict without forbidden columns
    diagnostic_reason: str


class EvaluationReport(BaseModel):
    """Comprehensive evaluation results combining standard metrics, financial fitness, and diagnostics."""
    hypothesis_id: str
    hypothesis_name: str
    is_valid: bool = True
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    standard_metrics: Optional[StandardMetrics] = None
    cost_metrics: Optional[CostMetrics] = None
    top_false_positives: List[DiagnosticOrder] = Field(default_factory=list)
    top_false_negatives: List[DiagnosticOrder] = Field(default_factory=list)


class RegressionReport(BaseModel):
    """Gate 1 Regression validation report comparing candidate against baseline performance."""
    gate_name: str = "Gate 1: Regression Suite"
    status: str = Field(description="'PASSED' or 'FAILED'")
    candidate_hypothesis_id: str
    baseline_net_savings_inr: float
    candidate_net_savings_inr: float
    delta_net_savings_inr: float
    baseline_recall: float
    candidate_recall: float
    delta_recall: float
    regressed_order_count: int
    reasons: List[str] = Field(default_factory=list)
    details: str = ""
