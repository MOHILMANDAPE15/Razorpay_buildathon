"""Dataset loading utilities with strict chronological split and single-touch held-out guards."""

import threading
from typing import Callable, Optional, Tuple, Any
import pandas as pd

from app.core.config import data_paths


class HeldOutTestAlreadyAccessedError(PermissionError):
    """Raised when held_out_test.csv is accessed more than once in a single run."""
    pass


# Thread-safe atomic flag to enforce single-touch methodology on held_out_test.csv
_HELD_OUT_LOCK = threading.Lock()
_HELD_OUT_TEST_ACCESSED: bool = False


def reset_held_out_access_guard_for_testing() -> None:
    """Internal test-only utility to reset the single-touch lock during unit test execution."""
    global _HELD_OUT_TEST_ACCESSED
    with _HELD_OUT_LOCK:
        _HELD_OUT_TEST_ACCESSED = False


def is_held_out_test_accessed() -> bool:
    """Returns whether the held_out_test set has already been accessed in this runtime."""
    with _HELD_OUT_LOCK:
        return _HELD_OUT_TEST_ACCESSED


def load_train_data() -> pd.DataFrame:
    """Loads the training dataset split (Days 0-55, baseline pre-drift).
    
    Queries isolated 'orders_train' PostgreSQL table if connected, else reads train.csv.
    """
    from app.db.session import check_db_connection, get_engine
    if check_db_connection():
        try:
            return pd.read_sql_table("orders_train", con=get_engine())
        except Exception:
            pass

    if not data_paths.train_path.exists():
        raise FileNotFoundError(f"Training dataset not found at: {data_paths.train_path}")
    return pd.read_csv(data_paths.train_path)


def load_validation_data() -> pd.DataFrame:
    """Loads the validation dataset split (Days 56-75, transition / drift ramp-in).
    
    Queries isolated 'orders_validation' PostgreSQL table if connected, else reads validation.csv.
    """
    from app.db.session import check_db_connection, get_engine
    if check_db_connection():
        try:
            return pd.read_sql_table("orders_validation", con=get_engine())
        except Exception:
            pass

    if not data_paths.validation_path.exists():
        raise FileNotFoundError(f"Validation dataset not found at: {data_paths.validation_path}")
    return pd.read_csv(data_paths.validation_path)


def load_full_dataset() -> pd.DataFrame:
    """Loads the full historical dataset (for narrative/debugging and offline analysis)."""
    if not data_paths.full_dataset_path.exists():
        raise FileNotFoundError(f"Full dataset not found at: {data_paths.full_dataset_path}")
    return pd.read_csv(data_paths.full_dataset_path)


def evaluate_on_held_out_test(
    evaluation_fn: Callable[[pd.DataFrame], Any]
) -> Any:
    """Executes an evaluation function against the isolated held-out test data strictly once per run.
    
    CRITICAL METHODOLOGY GUARANTEE:
    The held-out test set (Days 76-89) must only be scored after the evolved rule
    ensemble or baseline is completely frozen. Any second attempt to call this function
    will immediately raise a HeldOutTestAlreadyAccessedError.
    
    Args:
        evaluation_fn: A callable taking the raw held-out test DataFrame and returning results.
        
    Returns:
        The return value of evaluation_fn(df_held_out).
        
    Raises:
        HeldOutTestAlreadyAccessedError: If this function has already been executed in the current session.
        FileNotFoundError: If held_out_test data is missing.
    """
    global _HELD_OUT_TEST_ACCESSED

    with _HELD_OUT_LOCK:
        if _HELD_OUT_TEST_ACCESSED:
            raise HeldOutTestAlreadyAccessedError(
                "CRITICAL VIOLATION: 'orders_held_out_test' dataset has already been accessed in this session. "
                "Per the track methodology, held-out test data can only be evaluated strictly once "
                "after the final ensemble is frozen."
            )
        _HELD_OUT_TEST_ACCESSED = True

    from app.db.session import check_db_connection, get_engine
    if check_db_connection():
        try:
            df_test = pd.read_sql_table("orders_held_out_test", con=get_engine())
            return evaluation_fn(df_test)
        except Exception:
            pass

    if not data_paths.held_out_test_path.exists():
        raise FileNotFoundError(
            f"Held-out test dataset not found at: {data_paths.held_out_test_path}"
        )

    df_test = pd.read_csv(data_paths.held_out_test_path)
    return evaluation_fn(df_test)
