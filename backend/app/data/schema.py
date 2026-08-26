"""Data schema definitions, column whitelisting, and no-leakage feature sanitization."""

from typing import Any, Dict, List, Set, Tuple
import numpy as np
import pandas as pd


# 19 order-level feature columns available to online scoring & rule hypotheses
# (17 real + 2 decoy circularity-guard columns added per Section 5.4)
PERMISSIBLE_FEATURE_COLUMNS: List[str] = [
    "order_id",
    "order_date",
    "order_datetime",
    "day_index",
    "customer_id",
    "is_first_time_customer",
    "customer_account_age_days",
    "customer_prior_orders",
    "payment_mode",
    "order_value",
    "item_category",
    "pincode",
    "pincode_rolling_rto_rate",
    "promo_code_used",
    "device_id",
    "device_order_count_24h",
    "order_hour",
    # Circularity-guard decoy columns — NO causal link to is_rto (Section 5.4)
    "device_model_name",   # Random smartphone model string
    "app_theme_color",     # Random UI theme choice
]

# Columns strictly forbidden from hypothesis feature inputs
FORBIDDEN_COLUMNS: Set[str] = {
    "phase",         # Ground-truth drift schedule label (narrative/eval only)
    "drift_weight",  # Ground-truth drift intensity (narrative/eval only)
    "is_rto",        # Ground-truth target label (never exposed to hypothesis)
}

TARGET_LABEL_COLUMN: str = "is_rto"

# ---------------------------------------------------------------------------
# Blinded-naming map (Section 5.4 circularity guard — blinded ablation run)
#
# Maps real column names -> generic col_XX names.
# Used at the sandbox execution boundary: Generator sees only col_XX names in
# the prompt; rule code references col_XX; sandbox aliases col_XX -> real names
# before executing against the actual DataFrame.
# ---------------------------------------------------------------------------
BLINDED_COLUMN_MAP: Dict[str, str] = {
    "order_id":                  "col_01",
    "order_date":                "col_02",
    "order_datetime":            "col_03",
    "day_index":                 "col_04",
    "customer_id":               "col_05",
    "is_first_time_customer":    "col_06",
    "customer_account_age_days": "col_07",
    "customer_prior_orders":     "col_08",
    "payment_mode":              "col_09",
    "order_value":               "col_10",
    "item_category":             "col_11",
    "pincode":                   "col_12",
    "pincode_rolling_rto_rate":  "col_13",
    "promo_code_used":           "col_14",
    "device_id":                 "col_15",
    "device_order_count_24h":    "col_16",
    "order_hour":                "col_17",
    "device_model_name":         "col_18",
    "app_theme_color":           "col_19",
}

# Reverse map: col_XX -> real column name (used by sandbox to alias blinded rules)
BLINDED_COLUMN_REVERSE_MAP: Dict[str, str] = {v: k for k, v in BLINDED_COLUMN_MAP.items()}


DEFAULT_FEATURE_VALUES: Dict[str, Any] = {
    "is_first_time_customer": False,
    "customer_account_age_days": 30,
    "customer_prior_orders": 1,
    "payment_mode": "Prepaid",
    "order_value": 500.0,
    "item_category": "general",
    "pincode": "110001",
    "pincode_rolling_rto_rate": 0.20,
    "promo_code_used": False,
    "device_id": "DEV_DEFAULT",
    "device_order_count_24h": 1,
    "order_hour": 12,
    "device_model_name": "Standard",
    "app_theme_color": "light",
}


def sanitize_features(df: pd.DataFrame) -> pd.DataFrame:
    """Strips forbidden columns and returns a feature-only copy of the DataFrame.

    Guarantees that hypothesis functions cannot access 'phase', 'drift_weight',
    or the target label 'is_rto', and fills safe neutral defaults for any missing features.

    Args:
        df: Input DataFrame containing raw dataset columns.

    Returns:
        pd.DataFrame: Sanitized DataFrame containing only legitimate feature columns.
    """
    clean_df = df.copy()

    # Drop forbidden columns if present
    cols_to_drop = [col for col in clean_df.columns if col in FORBIDDEN_COLUMNS]
    if cols_to_drop:
        clean_df = clean_df.drop(columns=cols_to_drop)

    # Ensure all standard features exist with neutral defaults if omitted in streaming payload
    for col, default_val in DEFAULT_FEATURE_VALUES.items():
        if col not in clean_df.columns:
            clean_df[col] = default_val

    return clean_df


def get_blinded_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Renames real column names to blinded generic names (col_01..col_19).

    Used only at the sandbox execution boundary during blinded-mode ablation runs.
    The returned DataFrame has generic column names so that rules written with
    col_XX references execute correctly against the actual data.

    Args:
        df: Sanitized DataFrame with real column names.

    Returns:
        pd.DataFrame: Same data, but with columns renamed to col_XX.
    """
    rename_map = {col: BLINDED_COLUMN_MAP[col] for col in df.columns if col in BLINDED_COLUMN_MAP}
    return df.rename(columns=rename_map)


def get_real_dataframe(df_blinded: pd.DataFrame) -> pd.DataFrame:
    """Reverses blinded column names back to real names."""
    rename_map = {
        col: BLINDED_COLUMN_REVERSE_MAP[col]
        for col in df_blinded.columns
        if col in BLINDED_COLUMN_REVERSE_MAP
    }
    return df_blinded.rename(columns=rename_map)


def extract_features_and_labels(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Splits dataset into sanitized features, ground-truth labels, and order values.

    Args:
        df: Input DataFrame.

    Returns:
        Tuple containing:
            - sanitized_features (pd.DataFrame): Features with forbidden columns removed
            - y_true (np.ndarray): Binary ground-truth target labels (0 or 1)
            - order_values (np.ndarray): Numerical order value (INR) for cost computation
    """
    if TARGET_LABEL_COLUMN not in df.columns:
        raise ValueError(
            f"Required target label '{TARGET_LABEL_COLUMN}' not found in dataset."
        )
    if "order_value" not in df.columns:
        raise ValueError("Required column 'order_value' not found in dataset.")

    y_true = df[TARGET_LABEL_COLUMN].to_numpy().astype(int)
    order_values = df["order_value"].to_numpy().astype(float)
    sanitized_features = sanitize_features(df)

    return sanitized_features, y_true, order_values
