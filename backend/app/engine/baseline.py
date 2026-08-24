"""Static v1 Baseline Model (Pre-drift standard classifier trained on orders_train).

Establishes the immutable baseline benchmark representing traditional fraud detection
before self-evolution is applied.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

from app.core.config import data_paths, cost_config
from app.data.loader import load_train_data, load_validation_data
from app.data.schema import PERMISSIBLE_FEATURE_COLUMNS
from app.engine.evaluator import CostWeightedEvaluator
from app.engine.types import CostMetrics, EvaluationReport, StandardMetrics


SNAPSHOT_PATH = Path(__file__).resolve().parent / "v1_lightgbm_baseline_snapshot.json"

MODEL_FEATURES = [
    "day_index",
    "is_first_time_customer",
    "customer_account_age_days",
    "customer_prior_orders",
    "order_value",
    "pincode_rolling_rto_rate",
    "promo_code_used",
    "device_order_count_24h",
    "order_hour",
    "payment_mode",
    "item_category",
    "pincode",
    "device_id",
]


class StaticV1Baseline:
    """Pre-drift baseline classifier trained exclusively on orders_train (Days 0-55)."""

    def __init__(self, optimal_threshold: float = 0.5):
        self.model: Optional[lgb.LGBMClassifier] = None
        self.encoder: Optional[OrdinalEncoder] = None
        self.categorical_cols = ["payment_mode", "item_category", "pincode", "device_id"]
        self.numeric_cols = [
            col for col in MODEL_FEATURES if col not in self.categorical_cols
        ]
        self.feature_order = self.numeric_cols + self.categorical_cols
        self.optimal_threshold = optimal_threshold
        self.evaluator = CostWeightedEvaluator()

    def _prepare_features(self, df: pd.DataFrame, is_training: bool = False) -> pd.DataFrame:
        """Sanitizes, extracts permitted features, and encodes categoricals."""
        df_feat = df[self.feature_order].copy()

        # Handle booleans
        if "is_first_time_customer" in df_feat.columns:
            df_feat["is_first_time_customer"] = df_feat["is_first_time_customer"].astype(int)
        if "promo_code_used" in df_feat.columns:
            df_feat["promo_code_used"] = df_feat["promo_code_used"].astype(int)

        if is_training:
            self.encoder = OrdinalEncoder(
                handle_unknown="use_encoded_value",
                unknown_value=-1,
            )
            df_feat[self.categorical_cols] = self.encoder.fit_transform(
                df_feat[self.categorical_cols].astype(str)
            )
        else:
            if self.encoder is None:
                raise RuntimeError("Encoder has not been fitted. Call train() first.")
            df_feat[self.categorical_cols] = self.encoder.transform(
                df_feat[self.categorical_cols].astype(str)
            )

        return df_feat

    def train(self, df_train: Optional[pd.DataFrame] = None) -> "StaticV1Baseline":
        """Trains the LightGBM baseline on orders_train dataset."""
        df = df_train if df_train is not None else load_train_data()
        X = self._prepare_features(df, is_training=True)
        y = df["is_rto"].values

        # class_weight='balanced' corrects the ~26% RTO class imbalance;
        # without it the model suppresses RTO probabilities and threshold sweep cannot fix it.
        self.model = lgb.LGBMClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=6,
            num_leaves=31,
            class_weight="balanced",
            random_state=42,
            verbose=-1,
        )
        self.model.fit(X, y)
        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """Returns risk probabilities for input orders."""
        if self.model is None:
            raise RuntimeError("Model is not trained. Call train() first.")
        X = self._prepare_features(df, is_training=False)
        return self.model.predict_proba(X)[:, 1]

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Returns binary fraud predictions based on the decision threshold."""
        probas = self.predict_proba(df)
        return (probas >= self.optimal_threshold).astype(bool)

    def evaluate(self, df: pd.DataFrame, split_name: str = "validation") -> EvaluationReport:
        """Evaluates baseline against cost-weighted financial fitness formula."""
        flags = self.predict(df)
        return self.evaluator.evaluate_flags(
            flags=flags,
            df=df,
            hypothesis_id=f"baseline_v1_{split_name}",
            hypothesis_name=f"Static v1 Baseline ({split_name.capitalize()})",
        )

    def tune_threshold_on_train(self, df_train: pd.DataFrame) -> float:
        """Finds the decision threshold maximizing Net Financial Savings on train data (Vectorized)."""
        probas = self.predict_proba(df_train)
        y_true = df_train["is_rto"].values
        order_values = df_train["order_value"].values

        best_threshold = 0.5
        best_savings = -float("inf")

        # 81-step sweep gives 0.011 granularity (0.05 → 0.95) for a well-calibrated model
        for threshold in np.linspace(0.05, 0.95, 81):
            flags = probas >= threshold
            tp_mask = flags & (y_true == 1)
            fp_mask = flags & (y_true == 0)

            tp_count = np.sum(tp_mask)
            fp_cost = np.sum(order_values[fp_mask] * cost_config.fp_margin_loss_rate)
            net_savings = (tp_count * cost_config.avoided_rto_cost_inr) - fp_cost

            if net_savings > best_savings:
                best_savings = float(net_savings)
                best_threshold = float(threshold)

        self.optimal_threshold = best_threshold
        return best_threshold


def generate_and_save_v1_snapshot() -> Dict[str, Any]:
    """Trains static v1 baseline on actual train data and saves immutable benchmark snapshot."""
    print("[Baseline] Loading actual training and validation datasets...")
    df_train = load_train_data()
    df_val = load_validation_data()

    baseline = StaticV1Baseline()
    baseline.train(df_train)
    opt_thresh = baseline.tune_threshold_on_train(df_train)
    print(f"[Baseline] Optimal decision threshold on train: {opt_thresh:.2f}")

    train_report = baseline.evaluate(df_train, split_name="train")
    val_report = baseline.evaluate(df_val, split_name="validation")

    snapshot_data = {
        "model_name": "Static LightGBM Baseline (v1) [Section 4.8 Benchmark]",
        "training_data": "orders_train (10,807 orders, Days 0-55)",
        "optimal_threshold": opt_thresh,
        "performance_train_pre_drift": {
            "total_orders": train_report.standard_metrics.total_orders,
            "precision": train_report.standard_metrics.precision,
            "recall": train_report.standard_metrics.recall,
            "f1_score": train_report.standard_metrics.f1,
            "avoided_rto_loss_inr": train_report.cost_metrics.avoided_rto_loss_inr,
            "false_positive_insult_cost_inr": train_report.cost_metrics.false_positive_insult_cost_inr,
            "net_financial_savings_inr": train_report.cost_metrics.net_financial_savings_inr,
        },
        "performance_validation_drift": {
            "total_orders": val_report.standard_metrics.total_orders,
            "precision": val_report.standard_metrics.precision,
            "recall": val_report.standard_metrics.recall,
            "f1_score": val_report.standard_metrics.f1,
            "avoided_rto_loss_inr": val_report.cost_metrics.avoided_rto_loss_inr,
            "false_positive_insult_cost_inr": val_report.cost_metrics.false_positive_insult_cost_inr,
            "net_financial_savings_inr": val_report.cost_metrics.net_financial_savings_inr,
        },
    }

    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, indent=2)

    print(f"[Baseline Snapshot] Saved to {SNAPSHOT_PATH}")
    print(
        f"  -> Train Net Savings:      Rs. {train_report.cost_metrics.net_financial_savings_inr:,.2f}"
    )
    print(
        f"  -> Validation Net Savings: Rs. {val_report.cost_metrics.net_financial_savings_inr:,.2f} "
        f"(Precision: {val_report.standard_metrics.precision*100:.1f}%, Recall: {val_report.standard_metrics.recall*100:.1f}%)"
    )

    return snapshot_data


if __name__ == "__main__":
    generate_and_save_v1_snapshot()
