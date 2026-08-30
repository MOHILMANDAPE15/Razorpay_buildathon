"""Sandboxed and AST-validated Python rule execution engine.

Restricts access to filesystem, OS, network, and reflection to safely execute
LLM-generated fraud detection hypotheses.
"""

import ast
import concurrent.futures
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


# Forbidden AST node types, functions, and modules
FORBIDDEN_MODULES = {
    "os", "sys", "subprocess", "socket", "http", "urllib", "requests",
    "shutil", "builtins", "__builtin__", "importlib", "pathlib", "ctypes",
    "pickle", "marshal", "pty", "commands", "posix", "nt"
}

FORBIDDEN_FUNCS = {
    "eval", "exec", "compile", "open", "input", "globals", "locals",
    "vars", "dir", "getattr", "setattr", "delattr", "hasattr", "__import__",
    "breakpoint", "exit", "quit"
}

FORBIDDEN_ATTRIBUTES = {
    "__class__", "__bases__", "__subclasses__", "__globals__", "__code__",
    "__closure__", "__func__", "__self__", "__module__", "__dict__"
}


class SecurityError(Exception):
    """Raised when unsafe code patterns are detected in rule AST."""
    pass


class RuleExecutionError(Exception):
    """Raised when rule execution fails during runtime."""
    pass


class RuleTimeoutError(Exception):
    """Raised when rule execution exceeds permitted time limit."""
    pass


class ASTSecurityValidator(ast.NodeVisitor):
    """Validates Python AST against forbidden modules, functions, and attributes."""

    def __init__(self):
        self.errors: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            base_mod = alias.name.split(".")[0]
            if base_mod in FORBIDDEN_MODULES:
                self.errors.append(f"Forbidden module import: '{alias.name}'")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            base_mod = node.module.split(".")[0]
            if base_mod in FORBIDDEN_MODULES:
                self.errors.append(f"Forbidden module import from: '{node.module}'")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_FUNCS:
            self.errors.append(f"Forbidden function call: '{node.func.id}()'")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if node.attr in FORBIDDEN_ATTRIBUTES:
            self.errors.append(f"Forbidden attribute access: '{node.attr}'")
        self.generic_visit(node)


def validate_rule_code(code_str: str) -> None:
    """Validates that python code does not violate security constraints.
    
    Raises:
        SecurityError: If forbidden operations or modules are detected.
        SyntaxError: If code fails to parse.
    """
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        raise SyntaxError(f"Rule code syntax error: {e}") from e

    validator = ASTSecurityValidator()
    validator.visit(tree)

    if validator.errors:
        raise SecurityError(
            f"Security violation(s) in rule code: {'; '.join(validator.errors)}"
        )


SAFE_ALLOWED_MODULES = {
    "math", "time", "datetime", "re", "json", "random", "itertools",
    "collections", "functools", "operator", "string", "numpy", "pandas",
}


def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    base_name = name.split(".")[0]
    if base_name in FORBIDDEN_MODULES:
        raise SecurityError(f"Import of forbidden module '{name}' is blocked.")
    if base_name not in SAFE_ALLOWED_MODULES and name not in SAFE_ALLOWED_MODULES:
        raise SecurityError(f"Import of module '{name}' is not permitted in sandbox.")
    return __import__(name, globals, locals, fromlist, level)


def _get_safe_globals() -> Dict[str, Any]:
    """Constructs a restricted namespace for rule execution."""
    safe_builtins = {
        "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
        "enumerate": enumerate, "filter": filter, "float": float, "int": int,
        "isinstance": isinstance, "len": len, "list": list, "map": map,
        "max": max, "min": min, "range": range, "round": round, "set": set,
        "str": str, "sum": sum, "tuple": tuple, "zip": zip, "True": True,
        "False": False, "None": None,
        "__import__": _safe_import,
    }
    return {
        "__builtins__": safe_builtins,
        "np": np,
        "numpy": np,
        "pd": pd,
        "pandas": pd,
    }


def execute_rule_sandboxed(
    code_str: str,
    df_features: pd.DataFrame,
    entry_point: str = "predict",
    timeout_sec: float = 3.0,
) -> np.ndarray:
    """Executes a rule function inside a safe sandbox with timeout protection.
    
    The rule function in `code_str` must define a function (default `predict(df)`)
    that accepts a pandas DataFrame and returns a boolean Series/array, a list of booleans/0-1s,
    or a numeric probability array.
    
    Args:
        code_str: Python source code defining the rule.
        df_features: Feature DataFrame (must NOT contain phase, drift_weight, or is_rto).
        entry_point: Name of the function in code_str to invoke (default: "predict").
        timeout_sec: Maximum permitted execution time.
        
    Returns:
        np.ndarray: Binary array (1 for predicted RTO risk, 0 for safe/genuine).
        
    Raises:
        SecurityError: If code violates security constraints.
        RuleExecutionError: If runtime execution fails.
        RuleTimeoutError: If execution exceeds timeout.
    """
    validate_rule_code(code_str)

    def _run() -> np.ndarray:
        execution_env = _get_safe_globals()
        
        try:
            exec(code_str, execution_env)
        except Exception as e:
            raise RuleExecutionError(f"Error compiling/executing rule definitions: {str(e)}") from e

        if entry_point not in execution_env:
            # Fallback: check callable functions
            funcs = [v for k, v in execution_env.items() if callable(v) and k not in _get_safe_globals()]
            if not funcs:
                raise RuleExecutionError(
                    f"Entry point '{entry_point}' not found in rule code."
                )
            target_func = funcs[0]
        else:
            target_func = execution_env[entry_point]

        from app.data.schema import sanitize_features
        df_clean = sanitize_features(df_features)

        try:
            raw_result = target_func(df_clean.copy())
        except Exception:
            try:
                # Row-by-row dictionary fallback for single-order AST rules
                records = df_clean.to_dict(orient="records")
                raw_result = np.array([1 if target_func(r) else 0 for r in records], dtype=int)
            except Exception as e:
                raise RuleExecutionError(f"Runtime error during rule execution: {str(e)}") from e

        # Normalize output to 1D binary numpy array
        try:
            if isinstance(raw_result, (pd.Series, pd.DataFrame)):
                arr = raw_result.to_numpy().flatten()
            elif isinstance(raw_result, list):
                arr = np.array(raw_result).flatten()
            elif isinstance(raw_result, np.ndarray):
                arr = raw_result.flatten()
            elif isinstance(raw_result, (bool, int, float, np.bool_)):
                arr = np.full(len(df_features), raw_result)
            else:
                raise ValueError(f"Unsupported return type: {type(raw_result)}")

            # Convert boolean or probability threshold (> 0.5) to binary int array
            if arr.dtype == bool or np.issubdtype(arr.dtype, np.bool_):
                binary_preds = arr.astype(int)
            elif np.issubdtype(arr.dtype, np.number):
                binary_preds = (arr >= 0.5).astype(int)
            else:
                binary_preds = np.array([1 if x else 0 for x in arr], dtype=int)

            if len(binary_preds) != len(df_features):
                raise ValueError(
                    f"Rule returned {len(binary_preds)} predictions, expected {len(df_features)}"
                )

            return binary_preds

        except Exception as e:
            raise RuleExecutionError(f"Failed to process rule predictions: {str(e)}") from e

    # Execute with timeout
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run)
        try:
            return future.result(timeout=timeout_sec)
        except concurrent.futures.TimeoutError:
            raise RuleTimeoutError(
                f"Rule execution exceeded timeout of {timeout_sec} seconds."
            )
