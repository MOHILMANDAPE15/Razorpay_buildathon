# Dynamic Benchmark Wiring & UI Traceability Summary

> **Summary of Dynamic Data Wiring, Honest Ablation Layout, and Metric Traceability**  
> **Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager**

---

## 📌 1. Executive Summary

We completed the dynamic wiring of the Aegis-RTO frontend application. All hardcoded JSX numbers on the **Homepage (`/`)** and **Ablation Matrix (`/shadow-control`)** have been replaced with dynamic calls to a unified backend endpoint:

$$\text{Next.js Frontend} \xrightarrow{\text{GET /api/v1/benchmark/summary}} \text{FastAPI Backend} \xrightarrow{\text{Single-Source}} \texttt{shadow\_control\_results.json}$$

Every metric rendered in the interface is now **100% auditable and traceable** to our single-touch held-out test runs.

---

## 🔌 2. The Backend Unified Endpoint

* **Endpoint**: `GET /api/v1/benchmark/summary` (in [`backend/app/api/scoring.py`](file:///c:/Users/Dell/Razorpay_buildathon/backend/app/api/scoring.py))
* **Payload Structure**:
  1. `production_headline_metrics`: Single-threshold ($T=0.70$) held-out test headline results (2,641 orders, +₹2,458.91 net savings, 47.17% review density, 97.99% auto-decision rate).
  2. `ablation_matrix`: Full Model A vs. Model B vs. Model C comparison from [`shadow_control_results.json`](file:///c:/Users/Dell/Razorpay_buildathon/backend/scratch/shadow_control_results.json).
  3. `paired_bootstrap`: Exact $B=2,000$ paired bootstrap confidence intervals and empirical p-values.

---

## 🗺️ 3. End-to-End Metric Traceability Mapping

| Screen & Component | Displayed UI Metric | Backing API Field & JSON Source | Exact Benchmark Source |
|---|---|---|---|
| **`/` Hero Footer** | **`2,641 Orders`** | `production_headline_metrics.total_test_orders` | `held_out_test.csv` (Days 76–89) |
| **`/` Hero Footer** | **`+₹2,458.91`** | `production_headline_metrics.auto_decided_net_savings_inr` | Model B Champion ($T=0.70$) |
| **`/` Hero Footer** | **`47.17% (1.52x)`** | `production_headline_metrics.review_queue_rto_concentration` | Review Queue (25 TP / 53 cases) |
| **`/` Hero Footer** | **`97.99% Volume`** | `production_headline_metrics.auto_decided_pct` | 2,588 / 2,641 auto-decided orders |
| **`/shadow-control` Card 1** | **`Model A: 23 Orders (+₹1,715)`** | `ablation_matrix.models.model_a_frozen_v1.t_070` | Static Frozen v1 Baseline (3 rounds) |
| **`/shadow-control` Card 2** | **`Model C: 63 Orders (+₹4,387)`** | `ablation_matrix.models.model_c_shadow_control.t_070` | Shadow Control (5 pre-drift rounds) |
| **`/shadow-control` Card 3** | **`Model B: 51 Orders (+₹2,458)`** | `ablation_matrix.models.model_b_drift_champion.t_070` | Drift-Adapted Champion (5 rounds) |
| **`/shadow-control` Bootstrap** | **`Δ Net: -₹1,928.64`** | `paired_bootstrap_b_vs_c_t070.net_savings.point_delta_inr` | Paired Bootstrap ($B=2,000$) |
| **`/shadow-control` Bootstrap** | **`95% CI: [-₹4,721, +₹622]`** | `paired_bootstrap_b_vs_c_t070.net_savings.ci_95_lower/upper_inr` | Empirical $p=0.1510$ (Crosses Zero) |
| **`/shadow-control` Bootstrap** | **`Δ Precision: -5.60%`** | `paired_bootstrap_b_vs_c_t070.precision.point_delta_pct` | 95% CI: $[-19.93\%, +7.89\%]$ |
| **`/shadow-control` Bootstrap** | **`Δ Recall: -0.98%`** | `paired_bootstrap_b_vs_c_t070.recall.point_delta_pct` | 95% CI: $[-2.19\%, +0.13\%]$ |

---

## ⚖️ 4. Honesty-Preserving Shadow Control Layout

The `/shadow-control` page now prominently presents the paired bootstrap significance findings:
* **Headline Verdict**:
  > *"Statistically Indistinguishable at Production Threshold ($T=0.70$): All three paired bootstrap 95% confidence intervals cross zero ($p > 0.10$). The data at $T=0.70$ does not statistically resolve in favor of either drift adaptation or compute scaling alone."*
* **Secondary Observation**:
  > *"Under conservative operating thresholds ($T=0.75$), Model B establishes a higher precision ceiling (70.00% vs. 54.05%) with significantly reduced manual review overhead (3.56% vs. 7.04%), demonstrating operational specialization."*

---

## 🔮 5. Autonomous Discovery Lineage Highlighting

In the Knowledge Graph DAG ([`/lineage`](file:///c:/Users/Dell/Razorpay_buildathon/frontend/src/app/lineage/page.tsx)):
* Nodes with `discovery_type === "autonomous_discovery"` are styled in **Purple / Violet** with an `Autonomous Discovery` badge.
* A fixed evidence callout specifically highlights **`cluster_dyn_new_account_high_val_cod`** (67 unflagged misses, $1.72\times$ lift, $p=0.0000$) as proof of autonomous residual pattern mining without hand-coded static templates.
