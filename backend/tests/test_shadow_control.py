"""Unit test for Section 4.7 3-way rounds-matched shadow control comparison matrix."""

import pytest
from scratch.run_shadow_control import run_3way_shadow_control


def test_3way_shadow_control_execution_and_matrix_consistency():
    """Verifies that the 3-way matrix runs and satisfies the distribution shift proof conditions."""
    results = run_3way_shadow_control()

    assert "models" in results
    assert results.get("experiment_tag") == "CONTROLLED_MECHANISM_PROOF_ONLY"
    models = results["models"]

    # 1. Check all three models exist
    assert "frozen_v1" in models
    assert "shadow_control" in models
    assert "drift_adapted" in models

    v1 = models["frozen_v1"]
    shadow = models["shadow_control"]
    adapted = models["drift_adapted"]

    # 2. Frozen v1 performance on train vs val (significant degradation)
    assert v1["train_metrics"]["net_savings_inr"] > 20000.0
    assert v1["val_metrics"]["net_savings_inr"] < 10000.0
    assert v1["val_performance_delta_pct"]["net_savings_drop_pct"] > 50.0

    # 3. Rounds-matched shadow control (5 rounds on pre-drift only)
    assert shadow["rounds_budget"] == 5
    assert shadow["train_metrics"]["net_savings_inr"] > 30000.0  # Explores and tunes on train
    assert shadow["val_metrics"]["net_savings_inr"] < 16000.0    # Suffers >50% drop on shifted val distribution
    assert shadow["val_performance_delta_pct"]["net_savings_drop_pct"] > 50.0

    # 4. Drift-adapted model performance recovery
    assert adapted["val_metrics"]["net_savings_inr"] > 20000.0
    assert adapted["val_metrics"]["recall"] > 0.15
    assert adapted["val_metrics"]["net_savings_inr"] > shadow["val_metrics"]["net_savings_inr"]
