"""Residual Miner & Targeted Evolution Engine.

Offline analytical component that mines mature false negatives (unflagged RTO abuse
that shipped and resulted in return loss), clusters missed abuse patterns, and constructs
targeted generation agendas for the Generator agent.

CRITICAL METHODOLOGICAL GUARANTEES:
1. Label Maturity Gate: Only analyzes orders whose fulfillment window has resolved.
2. Leakage Guard: Clustering touches ONLY permissible feature columns (never phase, drift_weight, or target labels).
3. Strict Full-Dataset Acceptance Gate: Hypotheses generated from miss clusters MUST be
   accepted based on net cost-weighted fitness over the FULL validation dataset, never
   recall on the miss cluster alone.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from app.core.config import cost_config
from app.core.sandbox import execute_rule_sandboxed
from app.data.schema import FORBIDDEN_COLUMNS, PERMISSIBLE_FEATURE_COLUMNS, sanitize_features
from app.engine.evaluator import CostWeightedEvaluator
from app.engine.selector import EnsembleRule
from app.engine.types import EvaluationReport, RuleHypothesis


class TargetedMissCluster(BaseModel):
    """A coherent cluster of mature false negatives representing an emerging abuse tactic."""
    cluster_id: str
    cluster_name: str
    miss_count: int
    total_mature_orders_in_cohort: int
    miss_percentage_of_cohort: float
    signature_patterns: Dict[str, Any] = Field(default_factory=dict)
    representative_samples: List[Dict[str, Any]] = Field(default_factory=list)
    generator_agenda: str


class ResidualMiningReport(BaseModel):
    """Summary of the residual mining scan across mature orders."""
    total_orders_analyzed: int
    mature_orders_count: int
    unmatured_orders_deferred: int
    total_false_negatives: int
    false_negative_rate: float
    clusters_identified: List[TargetedMissCluster] = Field(default_factory=list)
    timestamp: str = Field(default="")


class ResidualMiner:
    """Mines mature delivery outcomes for unflagged false negative patterns."""

    def __init__(
        self,
        maturity_window_days: int = 5,
        min_cluster_size: int = 5,
        evaluator: Optional[CostWeightedEvaluator] = None,
    ):
        self.maturity_window_days = maturity_window_days
        self.min_cluster_size = min_cluster_size
        self.evaluator = evaluator or CostWeightedEvaluator()

    def filter_mature_orders(
        self,
        df_orders: pd.DataFrame,
        current_day_index: Optional[int] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Separates orders into mature (fulfillment resolved) vs immature (in-transit).
        
        Args:
            df_orders: Input dataset.
            current_day_index: Maximum day index representing the current system clock.
            
        Returns:
            Tuple of (mature_df, immature_df).
        """
        if "day_index" not in df_orders.columns:
            # If no day index, assume all orders are historical/mature
            return df_orders.copy(), pd.DataFrame()

        max_day = current_day_index if current_day_index is not None else df_orders["day_index"].max()
        maturity_cutoff = max_day - self.maturity_window_days

        mature_mask = df_orders["day_index"] <= maturity_cutoff
        mature_df = df_orders[mature_mask].copy().reset_index(drop=True)
        immature_df = df_orders[~mature_mask].copy().reset_index(drop=True)

        return mature_df, immature_df

    def extract_false_negatives(
        self,
        df_mature: pd.DataFrame,
        ensemble: EnsembleRule,
    ) -> pd.DataFrame:
        """Finds delivered orders that resulted in RTO but were unflagged by the active ensemble."""
        if "is_rto" not in df_mature.columns:
            raise ValueError("Cannot extract false negatives: 'is_rto' ground truth column is missing.")

        sanitized_features = sanitize_features(df_mature)
        flags = ensemble.predict(sanitized_features)
        y_true = df_mature["is_rto"].to_numpy().astype(int)

        # False negatives: actual RTO == 1, but model predicted 0 (shipped unflagged)
        fn_mask = (y_true == 1) & (flags == 0)
        return df_mature[fn_mask].copy().reset_index(drop=True)

    def cluster_misses(
        self,
        df_fn: pd.DataFrame,
        df_mature: pd.DataFrame,
    ) -> List[TargetedMissCluster]:
        """Clusters false negatives into structured emergent abuse groups.
        
        Guaranteed to use only permissible feature columns.
        """
        if len(df_fn) < self.min_cluster_size:
            return []

        clusters: List[TargetedMissCluster] = []

        # Safe feature subset for clustering
        clustering_features = [
            col for col in [
                "payment_mode",
                "promo_code_used",
                "device_order_count_24h",
                "customer_prior_orders",
                "item_category",
                "pincode_rolling_rto_rate",
                "order_hour",
                "order_value",
            ]
            if col in df_fn.columns and col not in FORBIDDEN_COLUMNS
        ]

        # Pattern 1: Promotional Abuse on COD (promo_code_used + COD + high device frequency)
        if "promo_code_used" in df_fn.columns and "payment_mode" in df_fn.columns:
            promo_cod_mask = (df_fn["payment_mode"] == "COD") & (df_fn["promo_code_used"] == True)
            df_promo_cod = df_fn[promo_cod_mask]

            if len(df_promo_cod) >= self.min_cluster_size:
                # Calculate cohort size in mature data
                mature_cohort_count = len(
                    df_mature[(df_mature["payment_mode"] == "COD") & (df_mature["promo_code_used"] == True)]
                )
                miss_pct = (len(df_promo_cod) / max(1, mature_cohort_count)) * 100

                samples = df_promo_cod[clustering_features].head(3).to_dict(orient="records")
                clusters.append(
                    TargetedMissCluster(
                        cluster_id="cluster_promo_cod_burst",
                        cluster_name="Promotional COD Velocity Exploitation",
                        miss_count=len(df_promo_cod),
                        total_mature_orders_in_cohort=mature_cohort_count,
                        miss_percentage_of_cohort=round(miss_pct, 2),
                        signature_patterns={
                            "payment_mode": "COD",
                            "promo_code_used": True,
                            "avg_device_orders_24h": round(float(df_promo_cod.get("device_order_count_24h", pd.Series([1])).mean()), 2),
                            "avg_prior_orders": round(float(df_promo_cod.get("customer_prior_orders", pd.Series([0])).mean()), 2),
                        },
                        representative_samples=samples,
                        generator_agenda=(
                            "TARGETED AGENDA: We identified a cluster of unflagged RTO misses using COD payment "
                            "combined with promo codes and multiple orders per device in 24h. "
                            "Synthesize a focused defense rule that flags this velocity abuse without over-flagging "
                            "legitimate single-order promotional buyers."
                        ),
                    )
                )

        # Pattern 2: Late-Night High-Risk Location Impulse Abuse
        if "order_hour" in df_fn.columns and "pincode_rolling_rto_rate" in df_fn.columns:
            late_night_mask = (
                (df_fn["payment_mode"] == "COD") &
                ((df_fn["order_hour"] >= 22) | (df_fn["order_hour"] <= 5)) &
                (df_fn["pincode_rolling_rto_rate"] >= 0.28)
            )
            df_late_night = df_fn[late_night_mask]

            if len(df_late_night) >= self.min_cluster_size:
                mature_cohort_count = len(
                    df_mature[
                        (df_mature["payment_mode"] == "COD") &
                        ((df_mature["order_hour"] >= 22) | (df_mature["order_hour"] <= 5)) &
                        (df_mature["pincode_rolling_rto_rate"] >= 0.28)
                    ]
                )
                miss_pct = (len(df_late_night) / max(1, mature_cohort_count)) * 100
                samples = df_late_night[clustering_features].head(3).to_dict(orient="records")

                clusters.append(
                    TargetedMissCluster(
                        cluster_id="cluster_late_night_impulse",
                        cluster_name="Late-Night High-Risk Pincode COD Ordering",
                        miss_count=len(df_late_night),
                        total_mature_orders_in_cohort=mature_cohort_count,
                        miss_percentage_of_cohort=round(miss_pct, 2),
                        signature_patterns={
                            "payment_mode": "COD",
                            "order_hours": "22:00 - 05:00",
                            "min_pincode_rto_rate": 0.28,
                            "avg_order_value": round(float(df_late_night.get("order_value", pd.Series([500])).mean()), 2),
                        },
                        representative_samples=samples,
                        generator_agenda=(
                            "TARGETED AGENDA: We identified a cluster of unflagged RTO misses placed late at night "
                            "(22:00 to 05:00) with COD in elevated RTO rate pincodes (>= 0.28). "
                            "Propose a targeted rule combining late-night ordering with pincode risk and new account status."
                        ),
                    )
                )

        # Pattern 3: Low-Value Rapid Test Orders in High-Risk Categories
        if "order_value" in df_fn.columns and "item_category" in df_fn.columns:
            low_val_mask = (
                (df_fn["payment_mode"] == "COD") &
                (df_fn["order_value"] <= 600) &
                (df_fn.get("customer_prior_orders", 0) == 0)
            )
            df_low_val = df_fn[low_val_mask]

            if len(df_low_val) >= self.min_cluster_size:
                mature_cohort_count = len(
                    df_mature[
                        (df_mature["payment_mode"] == "COD") &
                        (df_mature["order_value"] <= 600) &
                        (df_mature.get("customer_prior_orders", 0) == 0)
                    ]
                )
                miss_pct = (len(df_low_val) / max(1, mature_cohort_count)) * 100
                samples = df_low_val[clustering_features].head(3).to_dict(orient="records")

                clusters.append(
                    TargetedMissCluster(
                        cluster_id="cluster_low_value_impulse_cod",
                        cluster_name="Low-Value First-Time COD Impulse Testing",
                        miss_count=len(df_low_val),
                        total_mature_orders_in_cohort=mature_cohort_count,
                        miss_percentage_of_cohort=round(miss_pct, 2),
                        signature_patterns={
                            "payment_mode": "COD",
                            "max_order_value": 600.0,
                            "prior_orders": 0,
                        },
                        representative_samples=samples,
                        generator_agenda=(
                            "TARGETED AGENDA: We identified a cluster of low-value (<= ₹600) first-time COD test orders "
                            "that failed delivery. Synthesize a rule that guards against low-value COD impulse return risks "
                            "without catching genuine small-basket prepaid buyers."
                        ),
                    )
                )

        # Sort clusters by miss volume descending
        clusters.sort(key=lambda c: c.miss_count, reverse=True)
        return clusters

    def run_residual_analysis(
        self,
        df_orders: pd.DataFrame,
        ensemble: EnsembleRule,
        current_day_index: Optional[int] = None,
    ) -> ResidualMiningReport:
        """Executes full end-to-end residual mining on mature orders."""
        from datetime import datetime, timezone

        mature_df, immature_df = self.filter_mature_orders(df_orders, current_day_index)

        if len(mature_df) == 0:
            return ResidualMiningReport(
                total_orders_analyzed=len(df_orders),
                mature_orders_count=0,
                unmatured_orders_deferred=len(immature_df),
                total_false_negatives=0,
                false_negative_rate=0.0,
                clusters_identified=[],
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        df_fn = self.extract_false_negatives(mature_df, ensemble)
        fn_rate = len(df_fn) / len(mature_df) if len(mature_df) > 0 else 0.0
        clusters = self.cluster_misses(df_fn, mature_df)

        return ResidualMiningReport(
            total_orders_analyzed=len(df_orders),
            mature_orders_count=len(mature_df),
            unmatured_orders_deferred=len(immature_df),
            total_false_negatives=len(df_fn),
            false_negative_rate=round(fn_rate, 4),
            clusters_identified=clusters,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def evaluate_cluster_hypothesis_on_full_dataset(
        self,
        candidate_rule: RuleHypothesis,
        df_validation: pd.DataFrame,
        incumbent_ensemble: Optional[EnsembleRule] = None,
    ) -> Dict[str, Any]:
        """STRICT ACCEPTANCE GATE: Evaluates candidate rule on the FULL validation dataset.
        
        Guarantees that a rule synthesized to catch a miss cluster is NOT accepted on
        miss-cluster recall alone, but on cost-weighted net rupee savings across the
        entire distribution.
        
        Args:
            candidate_rule: The newly proposed targeted rule.
            df_validation: Full validation DataFrame.
            incumbent_ensemble: Currently active champion ensemble.
            
        Returns:
            Dict containing acceptance decision, full validation net savings, and rupee delta.
        """
        # 1. Evaluate baseline incumbent on full validation
        baseline_savings = 0.0
        if incumbent_ensemble is not None and incumbent_ensemble.rules:
            sanitized_val = sanitize_features(df_validation)
            incumbent_flags = incumbent_ensemble.predict(sanitized_val)
            incumbent_rep = self.evaluator.evaluate_flags(
                incumbent_flags, df_validation, "incumbent", "Incumbent Ensemble"
            )
            baseline_savings = incumbent_rep.cost_metrics.net_financial_savings_inr

        # 2. Evaluate candidate combined with incumbent
        combined_rules = (
            incumbent_ensemble.rules + [candidate_rule]
            if incumbent_ensemble and incumbent_ensemble.rules
            else [candidate_rule]
        )
        combined_ensemble = EnsembleRule(combined_rules)
        sanitized_val = sanitize_features(df_validation)
        combined_flags = combined_ensemble.predict(sanitized_val)
        combined_rep = self.evaluator.evaluate_flags(
            combined_flags, df_validation, "candidate_combined", "Candidate Combined"
        )

        candidate_savings = combined_rep.cost_metrics.net_financial_savings_inr
        delta_rupees = candidate_savings - baseline_savings
        precision = combined_rep.standard_metrics.precision
        recall = combined_rep.standard_metrics.recall
        false_positives = combined_rep.standard_metrics.false_positives
        true_positives = combined_rep.standard_metrics.true_positives

        # Acceptance Rule: Must deliver strictly positive net rupee savings improvement
        # on the FULL validation set (catches misses while keeping FP insult costs in check)
        is_accepted = delta_rupees > 0.0

        reasons = []
        if is_accepted:
            reasons.append(
                f"ACCEPTED: Targeted rule added +Rs. {delta_rupees:,.2f} net financial savings on full validation "
                f"(TP={true_positives}, FP={false_positives}, Net=Rs. {candidate_savings:,.2f})."
            )
        else:
            reasons.append(
                f"REJECTED BY COST ARITHMETIC: Targeted rule produced Rs. {delta_rupees:,.2f} delta vs baseline. "
                f"False positive insult costs (Rs. {combined_rep.cost_metrics.false_positive_insult_cost_inr:,.2f}) "
                f"exceed avoided RTO savings on full validation."
            )

        return {
            "accepted": is_accepted,
            "rule_id": candidate_rule.id,
            "rule_name": candidate_rule.name,
            "baseline_net_savings_inr": round(baseline_savings, 2),
            "candidate_net_savings_inr": round(candidate_savings, 2),
            "delta_net_savings_inr": round(delta_rupees, 2),
            "full_validation_precision": round(precision, 4),
            "full_validation_recall": round(recall, 4),
            "full_validation_tp": true_positives,
            "full_validation_fp": false_positives,
            "verdict": "PROMOTED" if is_accepted else "REJECTED_BY_COST_GATE",
            "reasons": reasons,
        }
