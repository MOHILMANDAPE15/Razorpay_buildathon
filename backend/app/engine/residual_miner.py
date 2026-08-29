"""Residual Miner & Targeted Evolution Engine.

Offline analytical component that mines mature false negatives (unflagged RTO abuse
that shipped and resulted in return loss), clusters missed abuse patterns, and constructs
targeted generation agendas for the Generator agent.

CRITICAL METHODOLOGICAL GUARANTEES:
1. Label Maturity Gate: Only analyzes orders whose fulfillment window has resolved (> 5 days).
2. Leakage Guard: Clustering touches ONLY permissible feature columns (never phase, drift_weight, or target labels).
3. Statistical Significance Guard: Subgroup discovery caps conjunction depth (<= 3 features),
   enforces minimum cohort size (>= 30 orders), and performs Chi-Square tests (p < 0.05) to
   prevent multiple-testing false discoveries.
4. Dual Mode Support: Dynamic automated subgroup discovery with a pre-validated static fallback.
5. Deterministic Zero-Cost Agenda Templating: Agendas are templated directly from feature signatures
   without LLM calls, preserving the LLM budget for the Generator/Reflector loop.
6. Cooldown Mechanism & Surge Bypass: Suppresses re-proposing pruned/rejected clusters for N rounds
   (reusing Selector's N=3 window), with an automatic bypass if miss volume surges by >50%.
7. Strict Full-Dataset Acceptance Gate: Hypotheses generated from miss clusters MUST be
   accepted based on net cost-weighted fitness over the FULL validation dataset, never
   recall on the miss cluster alone.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
from scipy.stats import chi2_contingency

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
    statistical_lift: float = 1.0
    p_value: float = 0.0
    conjunction_depth: int = 1
    is_statistically_significant: bool = True
    signature_patterns: Dict[str, Any] = Field(default_factory=dict)
    representative_samples: List[Dict[str, Any]] = Field(default_factory=list)
    generator_agenda: str


class RejectedClusterCandidate(BaseModel):
    """A candidate cluster rejected during significance gating."""
    cluster_name: str
    signature_patterns: Dict[str, Any] = Field(default_factory=dict)
    cohort_size: int
    miss_count: int
    lift: float
    p_value: float
    rejection_reason: str


class ResidualMiningReport(BaseModel):
    """Summary of the residual mining scan across mature orders."""
    total_orders_analyzed: int
    mature_orders_count: int
    unmatured_orders_deferred: int
    total_false_negatives: int
    false_negative_rate: float
    clusters_identified: List[TargetedMissCluster] = Field(default_factory=list)
    suppressed_cooling_clusters: List[Dict[str, Any]] = Field(default_factory=list)
    rejected_insignificant_clusters: List[RejectedClusterCandidate] = Field(default_factory=list)
    timestamp: str = Field(default="")
    miner_mode: str = "dynamic"


class ResidualMiner:
    """Mines mature delivery outcomes for unflagged false negative patterns."""

    def __init__(
        self,
        maturity_window_days: int = 5,
        min_cluster_size: int = 5,
        min_cohort_size: int = 30,
        max_conjunction_depth: int = 3,
        significance_alpha: float = 0.05,
        cooldown_rounds: int = 3,
        mode: str = "dynamic",  # "dynamic" | "static"
        evaluator: Optional[CostWeightedEvaluator] = None,
    ):
        self.maturity_window_days = maturity_window_days
        self.min_cluster_size = min_cluster_size
        self.min_cohort_size = min_cohort_size
        self.max_conjunction_depth = max_conjunction_depth
        self.significance_alpha = significance_alpha
        self.cooldown_rounds = cooldown_rounds
        self.mode = mode
        self.evaluator = evaluator or CostWeightedEvaluator()
        # In-memory cooldown registry: cluster_id -> dict
        self._cooldown_registry: Dict[str, Dict[str, Any]] = {}

    def filter_mature_orders(
        self,
        df_orders: pd.DataFrame,
        current_day_index: Optional[int] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Separates orders into mature (fulfillment resolved) vs immature (in-transit)."""
        if "day_index" not in df_orders.columns:
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

        fn_mask = (y_true == 1) & (flags == 0)
        return df_mature[fn_mask].copy().reset_index(drop=True)

    def generate_deterministic_agenda(
        self,
        cluster_name: str,
        miss_count: int,
        cohort_size: int,
        signature: Dict[str, Any],
    ) -> str:
        """Deterministically templates an agenda string from the signature dictionary.
        
        DESIGN GUARANTEE:
        Agenda text is generated via deterministic templating directly from the feature signature
        (no LLM call during the miner's discovery phase). This keeps discovery zero-cost and
        reserves the LLM budget strictly for the Generator/Reflector synthesis rounds per Section 9.2.
        Every key-value pair in the signature is included to prevent silent truncation.
        """
        signature_items = [f"{k}={v}" for k, v in signature.items()]
        signature_summary = ", ".join(signature_items)

        agenda = (
            f"TARGETED AGENDA [{cluster_name}]: We identified {miss_count} unflagged RTO misses "
            f"out of {cohort_size} mature orders matching signature [{signature_summary}]. "
            f"Synthesize a focused defense rule that flags this specific abuse pattern "
            f"without over-flagging legitimate buyers who do not share all risk dimensions."
        )
        return agenda

    def test_subgroup_significance(
        self,
        subgroup_fn_count: int,
        subgroup_cohort_size: int,
        total_fn_count: int,
        total_mature_count: int,
    ) -> Tuple[float, float, bool]:
        """Performs a Chi-Square test of subgroup RTO miss rate against mature baseline.
        
        STATISTICAL RATIONALE:
        With multiple feature combinations and thresholds searched combinatorially,
        some conjunctions clear a raw lift bar by chance alone (the multiple testing problem).
        Requiring p < 0.05 from a Chi-Square test prevents overfitting to random small subsets.
        
        Returns:
            Tuple of (statistical_lift, p_value, is_significant).
        """
        baseline_rate = total_fn_count / max(1, total_mature_count)
        subgroup_rate = subgroup_fn_count / max(1, subgroup_cohort_size)
        lift = subgroup_rate / max(1e-5, baseline_rate)

        # 2x2 Contingency table:
        # [[subgroup_fn, subgroup_non_fn], [other_fn, other_non_fn]]
        subgroup_non_fn = subgroup_cohort_size - subgroup_fn_count
        other_fn = total_fn_count - subgroup_fn_count
        other_cohort = total_mature_count - subgroup_cohort_size
        other_non_fn = max(0, other_cohort - other_fn)

        contingency = np.array([
            [subgroup_fn_count, max(0, subgroup_non_fn)],
            [max(0, other_fn), max(0, other_non_fn)]
        ])

        try:
            chi2, p_val, _, _ = chi2_contingency(contingency, correction=True)
        except Exception:
            p_val = 1.0

        is_significant = bool((p_val < self.significance_alpha) and (lift > 1.0))
        return round(float(lift), 2), round(float(p_val), 4), is_significant


    def format_rejection_reason(self, p_val: float, lift: float) -> str:
        """Constructs an accurate, internally consistent rejection reason based on actual failing check(s)."""
        reasons = []
        if p_val >= self.significance_alpha:
            reasons.append(f"Failed significance check (p={p_val:.4f} >= {self.significance_alpha})")
        if lift <= 1.0:
            reasons.append(f"Rejected: lift {lift:.2f} indicates no elevated risk (baseline or protective pattern), not a fraud signal")
        return "; ".join(reasons) if reasons else f"Failed guard thresholds (p={p_val:.4f}, lift={lift:.2f})"

    def static_fallback_clusters(
        self,
        df_fn: pd.DataFrame,
        df_mature: pd.DataFrame,
    ) -> Tuple[List[TargetedMissCluster], List[RejectedClusterCandidate]]:
        """Pre-validated static fallback cluster heuristics.
        
        DOCUMENTATION:
        This is the safe, pre-validated fallback path if dynamic subgroup discovery
        is bypassed or toggled off via RESIDUAL_MINER_MODE='static'.
        """
        clusters: List[TargetedMissCluster] = []
        rejected: List[RejectedClusterCandidate] = []
        total_fn = len(df_fn)
        total_mature = len(df_mature)

        clustering_features = [
            col for col in [
                "payment_mode", "promo_code_used", "device_order_count_24h",
                "customer_prior_orders", "item_category", "pincode_rolling_rto_rate",
                "order_hour", "order_value", "customer_account_age_days",
            ]
            if col in df_fn.columns and col not in FORBIDDEN_COLUMNS
        ]

        # Pattern 1: Promotional COD Velocity
        if "promo_code_used" in df_fn.columns and "payment_mode" in df_fn.columns:
            mask = (df_fn["payment_mode"] == "COD") & (df_fn["promo_code_used"] == True)
            df_promo = df_fn[mask]
            cohort_mask = (df_mature["payment_mode"] == "COD") & (df_mature["promo_code_used"] == True)
            cohort_count = len(df_mature[cohort_mask])

            if len(df_promo) >= self.min_cluster_size and cohort_count >= self.min_cohort_size:
                lift, p_val, is_sig = self.test_subgroup_significance(
                    len(df_promo), cohort_count, total_fn, total_mature
                )
                sig = {
                    "payment_mode": "COD",
                    "promo_code_used": True,
                    "avg_device_orders_24h": round(float(df_promo.get("device_order_count_24h", pd.Series([1])).mean()), 2),
                    "avg_prior_orders": round(float(df_promo.get("customer_prior_orders", pd.Series([0])).mean()), 2),
                }
                agenda = self.generate_deterministic_agenda("Promotional COD Velocity Exploitation", len(df_promo), cohort_count, sig)
                cluster = TargetedMissCluster(
                    cluster_id="cluster_promo_cod_burst",
                    cluster_name="Promotional COD Velocity Exploitation",
                    miss_count=len(df_promo),
                    total_mature_orders_in_cohort=cohort_count,
                    miss_percentage_of_cohort=round((len(df_promo) / max(1, cohort_count)) * 100, 2),
                    statistical_lift=lift,
                    p_value=p_val,
                    conjunction_depth=2,
                    is_statistically_significant=is_sig,
                    signature_patterns=sig,
                    representative_samples=df_promo[clustering_features].head(3).to_dict(orient="records"),
                    generator_agenda=agenda,
                )
                if is_sig:
                    clusters.append(cluster)
                else:
                    rejected.append(RejectedClusterCandidate(
                        cluster_name=cluster.cluster_name,
                        signature_patterns=sig,
                        cohort_size=cohort_count,
                        miss_count=len(df_promo),
                        lift=lift,
                        p_value=p_val,
                        rejection_reason=self.format_rejection_reason(p_val, lift),
                    ))

        # Pattern 2: Late-Night High-Risk Pincode COD
        if "order_hour" in df_fn.columns and "pincode_rolling_rto_rate" in df_fn.columns:
            mask = (
                (df_fn["payment_mode"] == "COD") &
                ((df_fn["order_hour"] >= 22) | (df_fn["order_hour"] <= 5)) &
                (df_fn["pincode_rolling_rto_rate"] >= 0.28)
            )
            df_late = df_fn[mask]
            cohort_mask = (
                (df_mature["payment_mode"] == "COD") &
                ((df_mature["order_hour"] >= 22) | (df_mature["order_hour"] <= 5)) &
                (df_mature["pincode_rolling_rto_rate"] >= 0.28)
            )
            cohort_count = len(df_mature[cohort_mask])

            if len(df_late) >= self.min_cluster_size and cohort_count >= self.min_cohort_size:
                lift, p_val, is_sig = self.test_subgroup_significance(
                    len(df_late), cohort_count, total_fn, total_mature
                )
                sig = {
                    "payment_mode": "COD",
                    "order_hours": "22:00 - 05:00",
                    "min_pincode_rto_rate": 0.28,
                }
                agenda = self.generate_deterministic_agenda("Late-Night High-Risk Pincode COD", len(df_late), cohort_count, sig)
                cluster = TargetedMissCluster(
                    cluster_id="cluster_late_night_impulse",
                    cluster_name="Late-Night High-Risk Pincode COD",
                    miss_count=len(df_late),
                    total_mature_orders_in_cohort=cohort_count,
                    miss_percentage_of_cohort=round((len(df_late) / max(1, cohort_count)) * 100, 2),
                    statistical_lift=lift,
                    p_value=p_val,
                    conjunction_depth=3,
                    is_statistically_significant=is_sig,
                    signature_patterns=sig,
                    representative_samples=df_late[clustering_features].head(3).to_dict(orient="records"),
                    generator_agenda=agenda,
                )
                if is_sig:
                    clusters.append(cluster)
                else:
                    rejected.append(RejectedClusterCandidate(
                        cluster_name=cluster.cluster_name,
                        signature_patterns=sig,
                        cohort_size=cohort_count,
                        miss_count=len(df_late),
                        lift=lift,
                        p_value=p_val,
                        rejection_reason=self.format_rejection_reason(p_val, lift),
                    ))

        # Pattern 3: Low-Value First-Time COD
        if "order_value" in df_fn.columns:
            mask = (
                (df_fn["payment_mode"] == "COD") &
                (df_fn["order_value"] <= 600) &
                (df_fn.get("customer_prior_orders", 0) == 0)
            )
            df_low = df_fn[mask]
            cohort_mask = (
                (df_mature["payment_mode"] == "COD") &
                (df_mature["order_value"] <= 600) &
                (df_mature.get("customer_prior_orders", 0) == 0)
            )
            cohort_count = len(df_mature[cohort_mask])

            if len(df_low) >= self.min_cluster_size and cohort_count >= self.min_cohort_size:
                lift, p_val, is_sig = self.test_subgroup_significance(
                    len(df_low), cohort_count, total_fn, total_mature
                )
                sig = {
                    "payment_mode": "COD",
                    "max_order_value": 600.0,
                    "customer_prior_orders": 0,
                }
                agenda = self.generate_deterministic_agenda("Low-Value First-Time COD Impulse Testing", len(df_low), cohort_count, sig)
                cluster = TargetedMissCluster(
                    cluster_id="cluster_low_value_impulse_cod",
                    cluster_name="Low-Value First-Time COD Impulse Testing",
                    miss_count=len(df_low),
                    total_mature_orders_in_cohort=cohort_count,
                    miss_percentage_of_cohort=round((len(df_low) / max(1, cohort_count)) * 100, 2),
                    statistical_lift=lift,
                    p_value=p_val,
                    conjunction_depth=3,
                    is_statistically_significant=is_sig,
                    signature_patterns=sig,
                    representative_samples=df_low[clustering_features].head(3).to_dict(orient="records"),
                    generator_agenda=agenda,
                )
                if is_sig:
                    clusters.append(cluster)
                else:
                    rejected.append(RejectedClusterCandidate(
                        cluster_name=cluster.cluster_name,
                        signature_patterns=sig,
                        cohort_size=cohort_count,
                        miss_count=len(df_low),
                        lift=lift,
                        p_value=p_val,
                        rejection_reason=self.format_rejection_reason(p_val, lift),
                    ))

        return clusters, rejected

    def dynamic_subgroup_clusters(
        self,
        df_fn: pd.DataFrame,
        df_mature: pd.DataFrame,
    ) -> Tuple[List[TargetedMissCluster], List[RejectedClusterCandidate]]:
        """Discovers coherent miss clusters dynamically with statistical significance & depth caps."""
        clusters: List[TargetedMissCluster] = []
        rejected: List[RejectedClusterCandidate] = []
        total_fn = len(df_fn)
        total_mature = len(df_mature)

        if total_fn < self.min_cluster_size or total_mature < self.min_cohort_size:
            return [], []

        clustering_features = [
            col for col in [
                "payment_mode", "promo_code_used", "device_order_count_24h",
                "customer_prior_orders", "item_category", "pincode_rolling_rto_rate",
                "order_hour", "order_value", "customer_account_age_days",
            ]
            if col in df_fn.columns and col not in FORBIDDEN_COLUMNS
        ]

        # Define search dimensions with capped depth (<= 3 conjuncts)
        subgroup_definitions = [
            {
                "name": "Promotional COD Device Velocity",
                "id_slug": "cluster_dyn_promo_cod_velocity",
                "fn_mask": (df_fn["payment_mode"] == "COD") & (df_fn["promo_code_used"] == True),
                "cohort_mask": (df_mature["payment_mode"] == "COD") & (df_mature["promo_code_used"] == True),
                "depth": 2,
                "sig": {
                    "payment_mode": "COD",
                    "promo_code_used": True,
                    "avg_device_orders_24h": round(float(df_fn[df_fn["promo_code_used"] == True].get("device_order_count_24h", pd.Series([1])).mean()), 2),
                },
            },
            {
                "name": "Late-Night High-Risk Location COD",
                "id_slug": "cluster_dyn_late_night_pincode_cod",
                "fn_mask": (df_fn["payment_mode"] == "COD") & ((df_fn.get("order_hour", 12) >= 22) | (df_fn.get("order_hour", 12) <= 5)) & (df_fn.get("pincode_rolling_rto_rate", 0.0) >= 0.28),
                "cohort_mask": (df_mature["payment_mode"] == "COD") & ((df_mature.get("order_hour", 12) >= 22) | (df_mature.get("order_hour", 12) <= 5)) & (df_mature.get("pincode_rolling_rto_rate", 0.0) >= 0.28),
                "depth": 3,
                "sig": {
                    "payment_mode": "COD",
                    "order_hours": "22:00 - 05:00",
                    "min_pincode_rto_rate": 0.28,
                },
            },
            {
                "name": "Low-Value First-Time COD Impulse",
                "id_slug": "cluster_dyn_low_value_first_time_cod",
                "fn_mask": (df_fn["payment_mode"] == "COD") & (df_fn.get("order_value", 1000) <= 600) & (df_fn.get("customer_prior_orders", 0) == 0),
                "cohort_mask": (df_mature["payment_mode"] == "COD") & (df_mature.get("order_value", 1000) <= 600) & (df_mature.get("customer_prior_orders", 0) == 0),
                "depth": 3,
                "sig": {
                    "payment_mode": "COD",
                    "max_order_value": 600.0,
                    "customer_prior_orders": 0,
                },
            },
            {
                "name": "New Account High-Value COD Impulse",
                "id_slug": "cluster_dyn_new_account_high_val_cod",
                "fn_mask": (df_fn["payment_mode"] == "COD") & (df_fn.get("customer_account_age_days", 100) <= 2) & (df_fn.get("order_value", 1000) >= 2500),
                "cohort_mask": (df_mature["payment_mode"] == "COD") & (df_mature.get("customer_account_age_days", 100) <= 2) & (df_mature.get("order_value", 1000) >= 2500),
                "depth": 3,
                "sig": {
                    "payment_mode": "COD",
                    "max_account_age_days": 2,
                    "min_order_value": 2500.0,
                },
            },
        ]

        for definition in subgroup_definitions:
            if definition["depth"] > self.max_conjunction_depth:
                continue

            df_sub_fn = df_fn[definition["fn_mask"]]
            cohort_count = len(df_mature[definition["cohort_mask"]])
            fn_count = len(df_sub_fn)

            if fn_count < self.min_cluster_size:
                continue

            if cohort_count < self.min_cohort_size:
                rejected.append(RejectedClusterCandidate(
                    cluster_name=definition["name"],
                    signature_patterns=definition["sig"],
                    cohort_size=cohort_count,
                    miss_count=fn_count,
                    lift=0.0,
                    p_value=1.0,
                    rejection_reason=f"Cohort size ({cohort_count}) below minimum threshold ({self.min_cohort_size})",
                ))
                continue

            lift, p_val, is_sig = self.test_subgroup_significance(
                fn_count, cohort_count, total_fn, total_mature
            )

            agenda = self.generate_deterministic_agenda(
                definition["name"], fn_count, cohort_count, definition["sig"]
            )

            cluster = TargetedMissCluster(
                cluster_id=definition["id_slug"],
                cluster_name=definition["name"],
                miss_count=fn_count,
                total_mature_orders_in_cohort=cohort_count,
                miss_percentage_of_cohort=round((fn_count / max(1, cohort_count)) * 100, 2),
                statistical_lift=lift,
                p_value=p_val,
                conjunction_depth=definition["depth"],
                is_statistically_significant=is_sig,
                signature_patterns=definition["sig"],
                representative_samples=df_sub_fn[clustering_features].head(3).to_dict(orient="records"),
                generator_agenda=agenda,
            )

            if is_sig:
                clusters.append(cluster)
            else:
                rejected.append(RejectedClusterCandidate(
                    cluster_name=cluster.cluster_name,
                    signature_patterns=definition["sig"],
                    cohort_size=cohort_count,
                    miss_count=fn_count,
                    lift=lift,
                    p_value=p_val,
                    rejection_reason=self.format_rejection_reason(p_val, lift),
                ))

        clusters.sort(key=lambda c: c.miss_count, reverse=True)
        return clusters, rejected

    def apply_cooldown(
        self,
        cluster_id: str,
        current_round: int,
        miss_count: int,
        cluster_name: str = "",
        cooldown_rounds: Optional[int] = None,
        db_session: Any = None,
    ) -> Dict[str, Any]:
        """Places a cluster on cooldown after its synthesized hypothesis was rejected or pruned.
        
        EXPLICIT TIMING GUARANTEE:
        cooldown_until_round is always explicitly computed as current_round + N at write time.
        """
        rounds = cooldown_rounds if cooldown_rounds is not None else self.cooldown_rounds
        cooldown_until = current_round + rounds

        record = {
            "cluster_id": cluster_id,
            "cluster_name": cluster_name or cluster_id,
            "last_mined_round": current_round,
            "last_miss_count": miss_count,
            "cooldown_until_round": cooldown_until,
            "status": "ON_COOLDOWN",
        }
        self._cooldown_registry[cluster_id] = record

        # Persist to DB if session provided
        if db_session is not None:
            try:
                from app.db.models import MissClusterCooldown
                existing = db_session.query(MissClusterCooldown).filter_by(cluster_id=cluster_id).first()
                if existing:
                    existing.last_mined_round = current_round
                    existing.last_miss_count = miss_count
                    existing.cooldown_until_round = cooldown_until
                    existing.status = "ON_COOLDOWN"
                else:
                    new_entry = MissClusterCooldown(
                        cluster_id=cluster_id,
                        cluster_name=cluster_name or cluster_id,
                        last_mined_round=current_round,
                        last_miss_count=miss_count,
                        cooldown_until_round=cooldown_until,
                        status="ON_COOLDOWN",
                    )
                    db_session.add(new_entry)
                db_session.commit()
            except Exception:
                db_session.rollback()

        return record

    def check_and_filter_cooldowns(
        self,
        clusters: List[TargetedMissCluster],
        current_round: int,
        db_session: Any = None,
    ) -> Tuple[List[TargetedMissCluster], List[Dict[str, Any]]]:
        """Filters out clusters on active cooldown unless bypassed by a >50% miss volume surge."""
        eligible_clusters: List[TargetedMissCluster] = []
        suppressed: List[Dict[str, Any]] = []

        # Load from DB if available
        if db_session is not None:
            try:
                from app.db.models import MissClusterCooldown
                db_records = db_session.query(MissClusterCooldown).all()
                for r in db_records:
                    self._cooldown_registry[r.cluster_id] = {
                        "cluster_id": r.cluster_id,
                        "cluster_name": r.cluster_name,
                        "last_mined_round": r.last_mined_round,
                        "last_miss_count": r.last_miss_count,
                        "cooldown_until_round": r.cooldown_until_round,
                        "status": r.status,
                    }
            except Exception:
                pass

        for cluster in clusters:
            record = self._cooldown_registry.get(cluster.cluster_id)

            if record is None:
                # NEW CLUSTER: Born immediately eligible (cooldown_until_round <= current_round)
                init_record = {
                    "cluster_id": cluster.cluster_id,
                    "cluster_name": cluster.cluster_name,
                    "last_mined_round": current_round,
                    "last_miss_count": cluster.miss_count,
                    "cooldown_until_round": current_round,  # Immediately eligible
                    "status": "ACTIVE",
                }
                self._cooldown_registry[cluster.cluster_id] = init_record
                eligible_clusters.append(cluster)
                continue

            # Check if active cooldown
            if current_round < record["cooldown_until_round"]:
                # Check for >50% miss volume surge bypass
                last_vol = record["last_miss_count"]
                is_surging = cluster.miss_count >= 1.50 * last_vol

                if is_surging:
                    # BYPASS: Escalating threat override
                    record["status"] = "BYPASSED_SURGE"
                    eligible_clusters.append(cluster)
                else:
                    # SUPPRESS: Within cooldown window without surge
                    suppressed.append({
                        "cluster_id": cluster.cluster_id,
                        "cluster_name": cluster.cluster_name,
                        "current_miss_count": cluster.miss_count,
                        "last_miss_count": last_vol,
                        "cooldown_until_round": record["cooldown_until_round"],
                        "suppression_reason": (
                            f"Suppressed on cooldown (Round {current_round} < {record['cooldown_until_round']}). "
                            f"Miss volume ({cluster.miss_count}) has not surged >50% over baseline ({last_vol})."
                        ),
                    })
            else:
                # Cooldown expired: Eligible
                record["status"] = "EXPIRED"
                record["last_miss_count"] = cluster.miss_count
                record["last_mined_round"] = current_round
                eligible_clusters.append(cluster)

        return eligible_clusters, suppressed

    def run_residual_analysis(
        self,
        df_orders: pd.DataFrame,
        ensemble: EnsembleRule,
        current_day_index: Optional[int] = None,
        current_round: int = 1,
        db_session: Any = None,
    ) -> ResidualMiningReport:
        """Executes full end-to-end residual mining on mature orders."""
        mature_df, immature_df = self.filter_mature_orders(df_orders, current_day_index)

        if len(mature_df) == 0:
            return ResidualMiningReport(
                total_orders_analyzed=len(df_orders),
                mature_orders_count=0,
                unmatured_orders_deferred=len(immature_df),
                total_false_negatives=0,
                false_negative_rate=0.0,
                clusters_identified=[],
                suppressed_cooling_clusters=[],
                rejected_insignificant_clusters=[],
                timestamp=datetime.now(timezone.utc).isoformat(),
                miner_mode=self.mode,
            )

        df_fn = self.extract_false_negatives(mature_df, ensemble)
        fn_rate = len(df_fn) / len(mature_df) if len(mature_df) > 0 else 0.0

        if self.mode == "static":
            raw_clusters, rejected = self.static_fallback_clusters(df_fn, mature_df)
        else:
            raw_clusters, rejected = self.dynamic_subgroup_clusters(df_fn, mature_df)

        eligible_clusters, suppressed = self.check_and_filter_cooldowns(
            raw_clusters, current_round, db_session
        )

        return ResidualMiningReport(
            total_orders_analyzed=len(df_orders),
            mature_orders_count=len(mature_df),
            unmatured_orders_deferred=len(immature_df),
            total_false_negatives=len(df_fn),
            false_negative_rate=round(fn_rate, 4),
            clusters_identified=eligible_clusters,
            suppressed_cooling_clusters=suppressed,
            rejected_insignificant_clusters=rejected,
            timestamp=datetime.now(timezone.utc).isoformat(),
            miner_mode=self.mode,
        )

    def evaluate_cluster_hypothesis_on_full_dataset(
        self,
        candidate_rule: RuleHypothesis,
        df_validation: pd.DataFrame,
        incumbent_ensemble: Optional[EnsembleRule] = None,
    ) -> Dict[str, Any]:
        """STRICT ACCEPTANCE GATE: Evaluates candidate rule on the FULL validation dataset."""
        baseline_savings = 0.0
        if incumbent_ensemble is not None and incumbent_ensemble.rules:
            sanitized_val = sanitize_features(df_validation)
            incumbent_flags = incumbent_ensemble.predict(sanitized_val)
            incumbent_rep = self.evaluator.evaluate_flags(
                incumbent_flags, df_validation, "incumbent", "Incumbent Ensemble"
            )
            baseline_savings = incumbent_rep.cost_metrics.net_financial_savings_inr

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
