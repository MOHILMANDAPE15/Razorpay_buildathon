# Residual Mining & Cooldown Lifecycle Guide

> **Architecture, API Reference, and Frontend Guide for Mature False Negative Mining**  
> **Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager**

---

## 🔍 1. Overview & Methodological Rationale

The **Residual Miner** is an offline analytical engine that discovers unflagged RTO patterns from mature delivery outcomes and drives targeted hypothesis synthesis:

```
[Mature Orders (>5 Days Resolved)]
              │
              ▼
   [Extract False Negatives]
              │
              ▼
 [Subgroup Clustering (Depth ≤ 3)]
              │
              ▼
 [Chi-Square Significance Guard (p < 0.05, Cohort ≥ 30)]
              │
              ├── (p ≥ 0.05 or Cohort < 30) ──► [Significance Guard Filtered]
              ▼
  [Cooldown & Surge-Bypass Filter]
              │
              ├── (Active Cooldown & Surge < 50%) ──► [Cooldown Suppressed]
              ▼
 [Deterministic Generator Agenda] ──► [Generator Agent] ──► [Full Acceptance Gate 1]
```

### Core Methodological Guarantees:
1. **Label Maturity Gate**: Strictly filters orders where `day_index <= current_day - 5`, ensuring fulfillment has completely resolved without in-flight delivery leakage.
2. **Statistical Significance Guard**: Enforces $p < 0.05$ (Chi-Square) and cohort size $\ge 30$ to prevent combinatorial false discoveries and circular decoy exploitation.
3. **Deterministic Zero-Cost Agenda Templating**: Agendas are templated directly from feature signatures without LLM calls, saving API tokens for code synthesis.
4. **Cooldown & Surge Bypass**: Suppresses re-proposing clusters for $N=3$ rounds, with an automated bypass override if miss volume surges by $>50\%$.

---

## 🔌 2. Backend API Reference

### 1. `GET /api/v1/residual-mining/latest-scan`
Returns the complete scan output across mature orders:
* `scan_metadata`: Mature order count, deferred in-flight orders, total false negatives, false negative rate, current round, maturity window.
* `discovered_clusters`: List of statistically significant clusters ($p < 0.05$) with signatures, miss counts, lift, cooldown status, generator agenda, and synthesized hypothesis code.
* `rejected_candidates`: List of candidates blocked by the significance guard with exact rejection reasons.

### 2. `GET /api/v1/residual-mining/cluster-history/{cluster_id}`
Returns the cross-scan evolutionary lifecycle for a cluster:
* Discovery round, peak miss volume, current status (`PROMOTED`, `ON_COOLDOWN`, `BYPASSED_SURGE`).
* Step-by-step timeline from initial discovery to agenda dispatch, hypothesis synthesis, Gate 1 evaluation, and cooldown monitoring.

---

## 🖥️ 3. Frontend Screen (`/mining`) & Component Catalog

The new **Residual Mining** page is positioned as the 6th navigation item in the Aegis-RTO sidebar:

### A. Header KPI Strip
* **Mature Orders Scanned**: Total fulfillment-resolved orders (`9,840` in training split).
* **Realized False Negatives**: Total unflagged returns (`1,912` orders).
* **False Negative Rate**: Baseline miss rate (`19.4%`).
* **Significant Clusters Discovered**: Clusters clearing $p < 0.05$ (`4`).
* **Significance Guard Filtered**: Non-significant candidates safely blocked (`2`).

### B. Discovered Clusters Grid
* **Autonomous Discovery Highlight**: Dedicated purple card for `cluster_dyn_new_account_high_val_cod` with note: *"Mined dynamically with zero hand-coded static equivalent"*.
* **Readable Feature Tags**: `payment_mode=COD`, `max_account_age_days=2`, `min_order_value=2500`.
* **Stats Pill**: Miss volume, Cohort size, Statistical Lift ($1.72\times$).
* **Synthesized Rule Preview**: Resulting Python code, acceptance gate status (`PROMOTED`), and net financial delta ($+\text{₹}3,120.80$).
* **Cooldown Badges**: `🟡 On Cooldown (Until R5)` or `🔴 Surge Bypass Active`.

### C. Significance Guard Blocked Candidates
* Displays candidates failing $p < 0.05$ or cohort size $< 30$.
* Labeled with positive framing: *"Significance guard is working as intended, protecting against multiple-testing overfitting and decoy features"*.

### D. Interactive Cluster Lifecycle Timeline Drawer
* Clicking any cluster opens a slide-out modal displaying its chronological cross-scan progression across evolution rounds.

---

## 🗺️ 4. End-to-End Metric Traceability Mapping

| UI Element on `/mining` | Displayed Value | Backing API Field & JSON Source |
|---|---|---|
| **Mature Orders Scanned** | `9,840` | `scan_metadata.mature_orders_count` |
| **Realized False Negatives** | `1,912` | `scan_metadata.total_false_negatives` |
| **False Negative Rate** | `19.4%` | `scan_metadata.false_negative_rate` |
| **Autonomous Cluster Miss Volume** | `67 orders` | `discovered_clusters[id].miss_volume` |
| **Autonomous Cluster Lift** | `1.72x` | `discovered_clusters[id].statistical_lift` |
| **Autonomous Cluster p-value** | `p = 0.0000` | `discovered_clusters[id].p_value` |
| **Autonomous Cluster Net Delta** | `+₹3,120.80` | `discovered_clusters[id].resulting_hypothesis.net_financial_delta_inr` |
| **Promotional COD Burst Misses** | `104 orders` | `discovered_clusters[id].miss_volume` |
| **Promotional COD Burst Lift** | `1.54x` | `discovered_clusters[id].statistical_lift` |
| **Decoy Feature Guard Rejection** | `p = 0.4412` | `rejected_candidates[0].p_value` |
| **Small-Cohort Guard Rejection** | `Cohort = 18` | `rejected_candidates[1].cohort_size` |
