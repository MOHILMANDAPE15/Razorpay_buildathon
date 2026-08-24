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

    def __init__(self, **data):
        for k in ["name", "code", "description", "rationale"]:
            if k in data and isinstance(data[k], str):
                data[k] = (
                    data[k]
                    .replace("\u2011", "-")
                    .replace("\u2013", "-")
                    .replace("\u2014", "-")
                    .replace("\u2018", "'")
                    .replace("\u2019", "'")
                    .replace("\u201c", '"')
                    .replace("\u201d", '"')
                )
        super().__init__(**data)


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
    dataset_split: Optional[str] = "validation"
    is_valid: bool = True
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    standard_metrics: Optional[StandardMetrics] = None
    cost_metrics: Optional[CostMetrics] = None
    gate_status: Optional[str] = "PASSED"
    gate_reasons: List[str] = Field(default_factory=list)
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


class BootstrappedMetrics(BaseModel):
    """Bootstrap confidence intervals (e.g. 95% CI) computed over N resamples."""
    n_bootstrap: int
    ci_percentile: float = 95.0
    
    mean_precision: float
    std_precision: float
    ci_lower_precision: float
    ci_upper_precision: float

    mean_recall: float
    std_recall: float
    ci_lower_recall: float
    ci_upper_recall: float

    mean_f1: float
    std_f1: float
    ci_lower_f1: float
    ci_upper_f1: float

    mean_net_savings_inr: float
    std_net_savings_inr: float
    ci_lower_net_savings_inr: float
    ci_upper_net_savings_inr: float


class AuditResult(BaseModel):
    """Gate 3 Defense-Only Audit check result."""
    gate_name: str = "Gate 3: Defense-Only Audit"
    hypothesis_id: str
    is_defense_only: bool
    status: str = Field(description="'PASSED' or 'FAILED'")
    phase_1_keyword_passed: bool
    phase_2_llm_judge_passed: bool
    flagged_keywords: List[str] = Field(default_factory=list)
    judge_reasoning: str = ""
    details: str = ""
