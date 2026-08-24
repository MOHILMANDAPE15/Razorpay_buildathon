"""Unit tests for the AST-validated sandbox execution engine."""

import numpy as np
import pandas as pd
import pytest

from app.core.sandbox import (
    ASTSecurityValidator,
    RuleExecutionError,
    RuleTimeoutError,
    SecurityError,
    execute_rule_sandboxed,
    validate_rule_code,
)


@pytest.fixture
def sample_features_df():
    """Provides a sample sanitized feature DataFrame."""
    return pd.DataFrame({
        "order_id": ["ord_1", "ord_2", "ord_3", "ord_4"],
        "order_value": [500.0, 3000.0, 1200.0, 4500.0],
        "payment_mode": ["Prepaid", "COD", "COD", "COD"],
        "is_first_time_customer": [0, 1, 1, 0],
        "pincode_rolling_rto_rate": [0.05, 0.35, 0.42, 0.10],
        "promo_code_used": [0, 1, 1, 0],
        "device_order_count_24h": [0, 3, 4, 1],
    })


def test_valid_rule_execution(sample_features_df):
    """Verifies that legitimate rule logic executes correctly and returns expected boolean/int flags."""
    rule_code = """
def predict(df):
    # Flag high-risk COD first-time orders with high pincode RTO rate
    condition = (
        (df['payment_mode'] == 'COD') &
        (df['is_first_time_customer'] == 1) &
        (df['pincode_rolling_rto_rate'] > 0.30)
    )
    return condition
"""
    preds = execute_rule_sandboxed(rule_code, sample_features_df)
    assert isinstance(preds, np.ndarray)
    assert len(preds) == 4
    # Rows 1 and 2 match the condition
    np.testing.assert_array_equal(preds, np.array([0, 1, 1, 0]))


def test_security_blocks_os_import(sample_features_df):
    """Verifies that attempts to import 'os' are blocked at AST validation stage."""
    malicious_code = """
import os
def predict(df):
    os.system("echo malicious")
    return [0] * len(df)
"""
    with pytest.raises(SecurityError) as exc_info:
        execute_rule_sandboxed(malicious_code, sample_features_df)
    assert "Forbidden module import: 'os'" in str(exc_info.value)


def test_security_blocks_subprocess_import(sample_features_df):
    """Verifies that attempts to import 'subprocess' are blocked."""
    malicious_code = """
from subprocess import Popen
def predict(df):
    return [0] * len(df)
"""
    with pytest.raises(SecurityError) as exc_info:
        execute_rule_sandboxed(malicious_code, sample_features_df)
    assert "Forbidden module import" in str(exc_info.value)


def test_security_blocks_open_and_eval(sample_features_df):
    """Verifies that forbidden builtin calls like open() or eval() are blocked."""
    code_with_open = """
def predict(df):
    with open('/etc/passwd', 'r') as f:
        pass
    return [0] * len(df)
"""
    with pytest.raises(SecurityError) as exc_info:
        execute_rule_sandboxed(code_with_open, sample_features_df)
    assert "Forbidden function call: 'open()'" in str(exc_info.value)


def test_security_blocks_class_subclasses_introspection(sample_features_df):
    """Verifies that reflection attacks using __subclasses__ are blocked."""
    code_with_introspection = """
def predict(df):
    sub = ().__class__.__bases__[0].__subclasses__()
    return [0] * len(df)
"""
    with pytest.raises(SecurityError) as exc_info:
        execute_rule_sandboxed(code_with_introspection, sample_features_df)
    assert "Forbidden attribute access" in str(exc_info.value)


def test_syntax_error_handling(sample_features_df):
    """Verifies that malformed syntax raises a clean SyntaxError."""
    broken_code = """
def predict(df
    return 1
"""
    with pytest.raises(SyntaxError):
        execute_rule_sandboxed(broken_code, sample_features_df)


def test_runtime_error_handling(sample_features_df):
    """Verifies that runtime exceptions inside the rule are caught as RuleExecutionError."""
    broken_runtime_code = """
def predict(df):
    # Non-existent column access
    return df['non_existent_column'] > 5
"""
    with pytest.raises(RuleExecutionError) as exc_info:
        execute_rule_sandboxed(broken_runtime_code, sample_features_df)
    assert "Runtime error" in str(exc_info.value)


def test_rule_timeout(sample_features_df):
    """Verifies that infinite loops or slow rules are terminated with RuleTimeoutError."""
    infinite_loop_code = """
import time
def predict(df):
    # Busy spin to trigger timeout
    t_end = time.time() + 2.0
    while time.time() < t_end:
        pass
    return [0] * len(df)
"""
    with pytest.raises(RuleTimeoutError):
        execute_rule_sandboxed(infinite_loop_code, sample_features_df, timeout_sec=0.2)
