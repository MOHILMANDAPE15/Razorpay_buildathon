"""Unit and integration tests for Three-Way Router and Section 6.2 Metrics Engine."""

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.main import app
from app.db.models import Base, HumanReviewItem, ScoringLog
from app.db.session import get_db
from app.engine.router import ThreeWayRouter
from app.engine.selector import EnsembleRule
from app.engine.types import RuleHypothesis

# Create test SQLite in-memory DB
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


@pytest.fixture(autouse=True)
def setup_test_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


client = TestClient(app)


@pytest.fixture
def dummy_ensemble():
    r1 = RuleHypothesis(
        id="r1_test",
        name="COD High Risk Pincode",
        code="def predict(df):\n    return (df['payment_mode'] == 'COD') & (df['pincode_rolling_rto_rate'] >= 0.40)",
    )
    r2 = RuleHypothesis(
        id="r2_test",
        name="New Account High Value COD",
        code="def predict(df):\n    return (df['payment_mode'] == 'COD') & (df['customer_account_age_days'] <= 10) & (df['order_value'] >= 1000)",
    )
    return EnsembleRule([r1, r2])


def test_three_way_routing_tiers(dummy_ensemble):
    """Verifies that orders correctly segment into AUTO_APPROVE, AUTO_BLOCK, and MANUAL_REVIEW."""
    router = ThreeWayRouter(low_risk_threshold=0.35, high_risk_threshold=0.70)

    test_df = pd.DataFrame([
        # 1. Low risk prepaid -> AUTO_APPROVE
        {
            "order_id": "ORD_LOW",
            "payment_mode": "Prepaid",
            "order_value": 500.0,
            "pincode_rolling_rto_rate": 0.10,
            "customer_account_age_days": 100,
            "customer_id": "C1",
            "pincode": "110001",
        },
        # 2. Moderate risk (1 rule match or moderate ambient risk) -> MANUAL_REVIEW
        {
            "order_id": "ORD_MID",
            "payment_mode": "COD",
            "order_value": 400.0,
            "pincode_rolling_rto_rate": 0.45,
            "customer_account_age_days": 80,
            "customer_id": "C2",
            "pincode": "110002",
        },
        # 3. High risk (compounding multi-rule match) -> AUTO_BLOCK
        {
            "order_id": "ORD_HIGH",
            "payment_mode": "COD",
            "order_value": 2500.0,
            "pincode_rolling_rto_rate": 0.50,
            "customer_account_age_days": 2,
            "customer_id": "C3",
            "pincode": "110003",
        },
    ])

    decisions = router.route_batch(test_df, dummy_ensemble)

    assert len(decisions) == 3
    assert decisions[0].decision == "AUTO_APPROVE"
    assert decisions[0].is_flagged is False

    assert decisions[1].decision in ["MANUAL_REVIEW", "AUTO_BLOCK"]
    assert decisions[1].is_flagged is True

    assert decisions[2].decision == "AUTO_BLOCK"
    assert decisions[2].is_flagged is True
    assert len(decisions[2].triggered_rules) >= 1


def test_section_6_2_honest_metrics_split(dummy_ensemble):
    """Verifies that Section 6.2 metrics report Auto-decided vs Review-routed separately."""
    router = ThreeWayRouter()

    df_eval = pd.DataFrame({
        "order_id": [f"ORD_{i}" for i in range(10)],
        "payment_mode": ["Prepaid"] * 5 + ["COD"] * 5,
        "order_value": [600.0] * 10,
        "pincode_rolling_rto_rate": [0.1] * 5 + [0.45] * 5,
        "customer_account_age_days": [100] * 5 + [5] * 5,
        "customer_id": [f"C{i}" for i in range(10)],
        "pincode": ["110001"] * 10,
        "is_rto": [0, 0, 0, 0, 0, 1, 1, 1, 0, 1],
    })

    decisions = router.route_batch(df_eval, dummy_ensemble)
    breakdown = router.evaluate_section_6_2_split(df_eval, decisions)

    assert breakdown.total_orders == 10
    assert (breakdown.auto_decided_count + breakdown.manual_review_count) == 10
    assert breakdown.auto_decided_pct + breakdown.manual_review_pct == pytest.approx(100.0)
    assert breakdown.auto_decided_precision >= 0.0
    assert "Section 6.2 Compliance" in breakdown.methodological_notice


def test_scoring_api_endpoints():
    """Verifies POST /api/v1/orders/score and GET /api/v1/review/queue API endpoints."""
    # Test batch scoring
    payload = {
        "orders": [
            {
                "order_id": "ORD_TEST_API_01",
                "payment_mode": "Prepaid",
                "order_value": 750.0,
                "pincode": "560001",
                "pincode_rolling_rto_rate": 0.12,
                "customer_account_age_days": 60,
                "customer_id": "C_TEST_01",
            },
            {
                "order_id": "ORD_TEST_API_02",
                "payment_mode": "COD",
                "order_value": 1500.0,
                "pincode": "110001",
                "pincode_rolling_rto_rate": 0.45,
                "customer_account_age_days": 2,
                "customer_id": "C_TEST_02",
            }
        ]
    }
    resp = client.post("/api/v1/orders/score", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["decision"] == "AUTO_APPROVE"

    # Test review metrics
    resp_metrics = client.get("/api/v1/review/metrics")
    assert resp_metrics.status_code == 200
    metrics_data = resp_metrics.json()
    assert "auto_decided_count" in metrics_data
    assert "manual_review_count" in metrics_data
    assert "auto_decided_precision" in metrics_data

    # Test review queue
    resp_queue = client.get("/api/v1/review/queue")
    assert resp_queue.status_code == 200
    assert "queue" in resp_queue.json()