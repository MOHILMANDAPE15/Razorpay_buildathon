"""Unit and integration tests for Knowledge Graph Lineage Engine and API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.main import app
from app.db.models import Base, EvolutionRun, Hypothesis, HypothesisLineage, EvaluationReportModel
from app.db.session import get_db
from app.engine.lineage import get_evolution_runs, get_run_lineage_graph, get_hypothesis_details

# Create in-memory SQLite database with StaticPool so all connections share the same memory DB
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def populate_sample_lineage_data():
    """Populates sample evolution run, hypotheses, lineages, and reports in test DB."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()
    try:
        run = EvolutionRun(
            run_id="run_clean_test_v1",
            total_rounds=2,
            hypotheses_tested=3,
            initial_best_net_savings_inr=500.0,
            final_best_net_savings_inr=24312.15,
            net_savings_delta_inr=23812.15,
            champion_hypothesis_id="hyp_child_02",
            status="COMPLETED",
        )
        session.add(run)

        h1 = Hypothesis(
            hypothesis_id="hyp_parent_01",
            run_id="run_clean_test_v1",
            generation_round=1,
            name="Parent COD Defense",
            target_signal="pincode_risk",
            description="Parent rule for COD orders",
            rationale="Initial baseline exploration",
            rule_code="def predict(df): return df['payment_mode'] == 'COD'",
            status="alive",
        )
        h2 = Hypothesis(
            hypothesis_id="hyp_child_02",
            run_id="run_clean_test_v1",
            generation_round=2,
            name="Low-Value COD Impulse Test Order Defense",
            target_signal="low_value_impulse",
            description="Mutated child rule capping order value",
            rationale="Reflector mutation adding order_value ceiling",
            rule_code="def predict(df): return (df['payment_mode'] == 'COD') & (df['order_value'] <= 500)",
            status="champion",
        )
        session.add_all([h1, h2])
        session.commit()

        lineage = HypothesisLineage(
            parent_hypothesis_id="hyp_parent_01",
            child_hypothesis_id="hyp_child_02",
            relationship_type="mutated_from",
            mutation_strategy="Lowered threshold and added order_value ceiling",
        )
        session.add(lineage)

        rep1 = EvaluationReportModel(
            hypothesis_id="hyp_parent_01",
            dataset_split="train_pre_drift",
            precision=0.25,
            recall=0.10,
            f1_score=0.14,
            accuracy=0.80,
            flag_rate=0.08,
            total_orders=1000,
            true_positives=25,
            false_positives=75,
            true_negatives=800,
            false_negatives=100,
            avoided_rto_loss_inr=6250.0,
            false_positive_insult_cost_inr=5000.0,
            net_financial_savings_inr=1250.0,
            cost_efficiency_ratio=1.25,
            gate_1_status="PASSED",
        )
        rep2 = EvaluationReportModel(
            hypothesis_id="hyp_child_02",
            dataset_split="train_pre_drift",
            precision=0.35,
            recall=0.15,
            f1_score=0.21,
            accuracy=0.85,
            flag_rate=0.07,
            total_orders=1000,
            true_positives=35,
            false_positives=35,
            true_negatives=850,
            false_negatives=80,
            avoided_rto_loss_inr=8750.0,
            false_positive_insult_cost_inr=2500.0,
            net_financial_savings_inr=24312.15,
            cost_efficiency_ratio=3.50,
            gate_1_status="PASSED",
        )
        session.add_all([rep1, rep2])
        session.commit()
    finally:
        session.close()


def test_health_check_endpoint():
    """Verifies the service health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["service"] == "Aegis-RTO"


def test_get_evolution_runs():
    """Verifies that evolution runs are retrieved with correct metadata."""
    session = TestingSessionLocal()
    try:
        runs = get_evolution_runs(session)
        assert len(runs) >= 1
        first_run = runs[0]
        assert first_run["run_id"] == "run_clean_test_v1"
        assert first_run["status"] == "COMPLETED"
        assert first_run["final_best_net_savings_inr"] == 24312.15
        assert first_run["total_rounds"] == 2
    finally:
        session.close()


def test_run_scoped_lineage_graph():
    """Verifies that get_run_lineage_graph returns a valid DAG scoped to a run."""
    session = TestingSessionLocal()
    try:
        graph = get_run_lineage_graph(session, run_id="run_clean_test_v1")
        assert graph["run_id"] == "run_clean_test_v1"
        assert len(graph["nodes"]) == 2
        assert len(graph["edges"]) == 1

        # Check nodes
        node_ids = {n["id"] for n in graph["nodes"]}
        assert "hyp_parent_01" in node_ids
        assert "hyp_child_02" in node_ids

        champ_node = next(n for n in graph["nodes"] if n["id"] == "hyp_child_02")
        assert champ_node["is_champion"] is True
        assert champ_node["parent_ids"] == ["hyp_parent_01"]

        # Check edge
        edge = graph["edges"][0]
        assert edge["source"] == "hyp_parent_01"
        assert edge["target"] == "hyp_child_02"
        assert edge["relationship_type"] == "mutated_from"
        assert "ceiling" in edge["mutation_strategy"]
    finally:
        session.close()


def test_hypothesis_details_retrieval():
    """Verifies single hypothesis detailed retrieval including parents, children, and reports."""
    session = TestingSessionLocal()
    try:
        details = get_hypothesis_details(session, "hyp_child_02")
        assert details is not None
        assert details["hypothesis_id"] == "hyp_child_02"
        assert len(details["parents"]) == 1
        assert details["parents"][0]["hypothesis_id"] == "hyp_parent_01"
        assert len(details["evaluation_reports"]) >= 1
        assert details["evaluation_reports"][0]["net_financial_savings_inr"] == 24312.15
    finally:
        session.close()


def test_lineage_api_endpoints():
    """Tests FastAPI lineage REST API endpoints via TestClient."""
    # 1. /api/v1/lineage/runs
    runs_res = client.get("/api/v1/lineage/runs")
    assert runs_res.status_code == 200
    runs = runs_res.json()
    assert len(runs) >= 1
    assert runs[0]["run_id"] == "run_clean_test_v1"

    # 2. /api/v1/lineage/graph?run_id=run_clean_test_v1
    graph_res = client.get("/api/v1/lineage/graph?run_id=run_clean_test_v1")
    assert graph_res.status_code == 200
    graph = graph_res.json()
    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1

    # 3. /api/v1/lineage/hypothesis/hyp_child_02
    hyp_res = client.get("/api/v1/lineage/hypothesis/hyp_child_02")
    assert hyp_res.status_code == 200
    hyp_data = hyp_res.json()
    assert hyp_data["hypothesis_id"] == "hyp_child_02"
    assert "payment_mode" in hyp_data["rule_code"]


def test_nonexistent_hypothesis_returns_404():
    """Verifies 404 error handling for non-existent hypothesis."""
    response = client.get("/api/v1/lineage/hypothesis/hyp_nonexistent_9999")
    assert response.status_code == 404
