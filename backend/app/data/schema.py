"""Data schema definitions, column whitelisting, and no-leakage feature sanitization."""

from typing import List, Set, Tuple
import numpy as np
import pandas as pd


# 17 legitimate order-level feature columns available to online scoring & rule hypotheses
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
]

# Columns strictly forbidden from hypothesis feature inputs
FORBIDDEN_COLUMNS: Set[str] = {
    "phase",         # Ground-truth drift schedule label (narrative/eval only)
    "drift_weight",  # Ground-truth drift intensity (narrative/eval only)
    "is_rto",        # Ground-truth target label (never exposed to hypothesis)
}

TARGET_LABEL_COLUMN: str = "is_rto"


def sanitize_features(df: pd.DataFrame) -> pd.DataFrame:
    """Strips forbidden columns and returns a feature-only copy of the DataFrame.
    
    Guarantees that hypothesis functions cannot access 'phase', 'drift_weight',
    or the target label 'is_rto'.
    
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
        
    return clean_df


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
