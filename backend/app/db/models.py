"""SQLAlchemy ORM models for isolated order tables, hypotheses, lineages, and evaluations."""

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


def get_utc_now():
    """Returns current UTC timestamp without timezone offset for clean SQL compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class OrderBaseMixin:
    """Base mixin defining the 17 order features + 2 decoy columns, drift schedule, and target label."""
    order_id = Column(String(64), primary_key=True, index=True)
    order_date = Column(Date, nullable=False)
    order_datetime = Column(DateTime, nullable=False)
    day_index = Column(Integer, nullable=False)
    customer_id = Column(String(64), nullable=False, index=True)
    is_first_time_customer = Column(Boolean, nullable=False)
    customer_account_age_days = Column(Integer, nullable=False)
    customer_prior_orders = Column(Integer, nullable=False)
    payment_mode = Column(String(16), nullable=False)
    order_value = Column(Numeric(10, 2), nullable=False)
    item_category = Column(String(64), nullable=False)
    pincode = Column(String(16), nullable=False, index=True)
    pincode_rolling_rto_rate = Column(Numeric(6, 4), nullable=False)
    promo_code_used = Column(Boolean, nullable=False)
    device_id = Column(String(64), nullable=False, index=True)
    device_order_count_24h = Column(Integer, nullable=False)
    order_hour = Column(Integer, nullable=False)
    phase = Column(String(32))
    drift_weight = Column(Numeric(6, 4))
    is_rto = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=get_utc_now)
    # Circularity-guard decoy columns (Section 5.4): random, NO causal link to is_rto
    device_model_name = Column(String(64), nullable=True)
    app_theme_color = Column(String(16), nullable=True)


class OrderTrain(Base, OrderBaseMixin):
    """Physically isolated table for Training Split orders (Days 0-55, 10,807 rows)."""
    __tablename__ = "orders_train"


class OrderValidation(Base, OrderBaseMixin):
    """Physically isolated table for Validation Split orders (Days 56-75, 3,885 rows)."""
    __tablename__ = "orders_validation"


class OrderHeldOutTest(Base, OrderBaseMixin):
    """Physically isolated table for Held-Out Test Split orders (Days 76-89, 2,641 rows)."""
    __tablename__ = "orders_held_out_test"


class EvolutionRun(Base):
    """Evolutionary run metadata and fitness trajectory."""
    __tablename__ = "evolution_runs"

    run_id = Column(String(64), primary_key=True)
    started_at = Column(DateTime, default=get_utc_now)
    completed_at = Column(DateTime, nullable=True)
    total_rounds = Column(Integer, nullable=False, default=1)
    hypotheses_tested = Column(Integer, nullable=False, default=0)
    initial_best_net_savings_inr = Column(Numeric(12, 2), default=0.0)
    final_best_net_savings_inr = Column(Numeric(12, 2), default=0.0)
    net_savings_delta_inr = Column(Numeric(12, 2), default=0.0)
    champion_hypothesis_id = Column(String(64), nullable=True)
    status = Column(String(32), default="RUNNING")

    hypotheses = relationship("Hypothesis", back_populates="evolution_run", cascade="all, delete-orphan")


class Hypothesis(Base):
    """Registered fraud rules and executable code."""
    __tablename__ = "hypotheses"

    hypothesis_id = Column(String(64), primary_key=True)
    run_id = Column(String(64), ForeignKey("evolution_runs.run_id", ondelete="SET NULL"), nullable=True)
    generation_round = Column(Integer, nullable=False, default=1, index=True)
    name = Column(String(255), nullable=False)
    target_signal = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    rationale = Column(Text, nullable=True)
    rule_code = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="candidate", index=True)
    created_at = Column(DateTime, default=get_utc_now)

    evolution_run = relationship("EvolutionRun", back_populates="hypotheses")
    evaluation_reports = relationship("EvaluationReportModel", back_populates="hypothesis", cascade="all, delete-orphan")
    child_lineages = relationship(
        "HypothesisLineage",
        foreign_keys="HypothesisLineage.parent_hypothesis_id",
        back_populates="parent_hypothesis",
        cascade="all, delete-orphan",
    )


class HypothesisLineage(Base):
    """Knowledge graph parent-child mutation edges."""
    __tablename__ = "hypothesis_lineages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_hypothesis_id = Column(String(64), ForeignKey("hypotheses.hypothesis_id", ondelete="CASCADE"), index=True)
    child_hypothesis_id = Column(String(64), ForeignKey("hypotheses.hypothesis_id", ondelete="CASCADE"), index=True)
    relationship_type = Column(String(32), nullable=False, default="mutated_from")
    mutation_strategy = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    parent_hypothesis = relationship("Hypothesis", foreign_keys=[parent_hypothesis_id], back_populates="child_lineages")
    child_hypothesis = relationship("Hypothesis", foreign_keys=[child_hypothesis_id])


class EvaluationReportModel(Base):
    """Evaluator performance scores and Gate 1 verification results."""
    __tablename__ = "evaluation_reports"

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    hypothesis_id = Column(String(64), ForeignKey("hypotheses.hypothesis_id", ondelete="CASCADE"), index=True)
    dataset_split = Column(String(32), nullable=False, index=True)
    precision = Column(Numeric(6, 4), nullable=False)
    recall = Column(Numeric(6, 4), nullable=False)
    f1_score = Column(Numeric(6, 4), nullable=False)
    accuracy = Column(Numeric(6, 4), nullable=False)
    flag_rate = Column(Numeric(6, 4), nullable=False)
    total_orders = Column(Integer, nullable=False)
    true_positives = Column(Integer, nullable=False)
    false_positives = Column(Integer, nullable=False)
    true_negatives = Column(Integer, nullable=False)
    false_negatives = Column(Integer, nullable=False)
    avoided_rto_loss_inr = Column(Numeric(12, 2), nullable=False)
    false_positive_insult_cost_inr = Column(Numeric(12, 2), nullable=False)
    net_financial_savings_inr = Column(Numeric(12, 2), nullable=False)
    cost_efficiency_ratio = Column(Numeric(8, 2), nullable=False)
    gate_1_status = Column(String(16), default="PASSED")
    gate_1_reasons = Column(JSON, default=list)
    evaluated_at = Column(DateTime, default=get_utc_now)

    hypothesis = relationship("Hypothesis", back_populates="evaluation_reports")


class ScoringLog(Base):
    """Online scoring events and drift tracking."""
    __tablename__ = "scoring_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(64), nullable=False)
    active_hypothesis_id = Column(String(64), ForeignKey("hypotheses.hypothesis_id", ondelete="SET NULL"), nullable=True)
    risk_score = Column(Numeric(6, 4), nullable=True)
    decision = Column(String(32), nullable=False, index=True)
    decision_latency_ms = Column(Numeric(8, 2), nullable=True)
    is_flagged = Column(Boolean, nullable=False)
    ground_truth_outcome = Column(String(32), default="PENDING")
    timestamp = Column(DateTime, default=get_utc_now, index=True)


class HumanReviewItem(Base):
    """Low-confidence review queue."""
    __tablename__ = "human_review_queue"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(64), nullable=False)
    risk_score = Column(Numeric(6, 4), nullable=False)
    triggered_signals = Column(JSON, default=dict)
    status = Column(String(32), default="PENDING", index=True)
    analyst_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
