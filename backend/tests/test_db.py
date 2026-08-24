"""Unit tests for the PostgreSQL / SQLAlchemy database layer and isolated table ingestion."""

import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import data_paths
from app.db.ingest import ingest_all_datasets, init_db
from app.db.models import (
    Base,
    EvaluationReportModel,
    EvolutionRun,
    Hypothesis,
    HypothesisLineage,
    OrderHeldOutTest,
    OrderTrain,
    OrderValidation,
    ScoringLog,
)


@pytest.fixture
def sqlite_test_engine():
    """Provides an in-memory SQL engine for isolated database testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    return engine


def test_schema_creation(sqlite_test_engine):
    """Verifies that all 9 tables are created properly."""
    table_names = list(Base.metadata.tables.keys())
    assert "orders_train" in table_names
    assert "orders_validation" in table_names
    assert "orders_held_out_test" in table_names
    assert "evolution_runs" in table_names
    assert "hypotheses" in table_names
    assert "hypothesis_lineages" in table_names
    assert "evaluation_reports" in table_names
    assert "scoring_logs" in table_names
    assert "human_review_queue" in table_names


def test_bulk_csv_ingestion_into_isolated_tables(sqlite_test_engine):
    """Verifies that ingest_all_datasets populates exact row counts into isolated tables."""
    counts = ingest_all_datasets(engine=sqlite_test_engine)

    assert counts["orders_train"] == 10807
    assert counts["orders_validation"] == 3885
    assert counts["orders_held_out_test"] == 2641
    assert counts["total"] == 17333

    # Verify querying each table directly
    with sqlite_test_engine.connect() as conn:
        train_count = conn.execute(text("SELECT COUNT(*) FROM orders_train")).scalar()
        val_count = conn.execute(text("SELECT COUNT(*) FROM orders_validation")).scalar()
        test_count = conn.execute(text("SELECT COUNT(*) FROM orders_held_out_test")).scalar()

    assert train_count == 10807
    assert val_count == 3885
    assert test_count == 2641


def test_orm_models_and_lineage_relations(sqlite_test_engine):
    """Verifies that SQLAlchemy ORM models handle creation, relations, and lineages correctly."""
    TestingSession = sessionmaker(bind=sqlite_test_engine)
    session = TestingSession()

    # 1. Create an evolution run
    run = EvolutionRun(
        run_id="run_test_01",
        total_rounds=2,
        hypotheses_tested=4,
        initial_best_net_savings_inr=1500.0,
        final_best_net_savings_inr=28000.0,
        net_savings_delta_inr=26500.0,
        status="COMPLETED",
    )
    session.add(run)

    # 2. Create parent hypothesis
    parent_hyp = Hypothesis(
        hypothesis_id="hyp_parent_001",
        run_id="run_test_01",
        generation_round=1,
        name="Parent Rule",
        rule_code="def predict(df): return df['payment_mode'] == 'COD'",
        status="alive",
    )
    session.add(parent_hyp)

    # 3. Create child mutated hypothesis
    child_hyp = Hypothesis(
        hypothesis_id="hyp_child_002",
        run_id="run_test_01",
        generation_round=2,
        name="Mutated Child Rule",
        rule_code="def predict(df): return (df['payment_mode'] == 'COD') & (df['device_order_count_24h'] >= 2)",
        status="champion",
    )
    session.add(child_hyp)
    session.commit()

    # 4. Create lineage edge
    edge = HypothesisLineage(
        parent_hypothesis_id="hyp_parent_001",
        child_hypothesis_id="hyp_child_002",
        relationship_type="mutated_from",
        mutation_strategy="Added device reuse condition",
    )
    session.add(edge)
    session.commit()

    # Query back
    fetched_parent = session.query(Hypothesis).filter_by(hypothesis_id="hyp_parent_001").first()
    assert fetched_parent is not None
    assert len(fetched_parent.child_lineages) == 1
    assert fetched_parent.child_lineages[0].child_hypothesis_id == "hyp_child_002"

    session.close()
