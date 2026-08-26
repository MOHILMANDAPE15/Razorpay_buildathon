# Aegis-RTO: Residual-Driven Evolution, Dynamic Clustering & Cooldown Report

> **Comprehensive Technical Implementation & Empirical Results Summary**  
> **Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager (Return-Risk Scorer & Adaptive Defense)**

---

## 📑 Executive Overview

This document provides a complete technical walkthrough and verified empirical results for the **Dynamic Residual Mining & Miss-Cluster Cooldown Engine** implemented in Aegis-RTO.

---

## 🏛️ 1. Architecture & Key Mechanisms

```
                        ┌────────────────────────────────────────────────────────┐
                        │             Mature Delivered Orders (> 5 Days)         │
                        │                  (Fulfillment Resolved)                │
                        └──────────────────────────┬─────────────────────────────┘
                                                   │
                                                   ▼
                        ┌────────────────────────────────────────────────────────┐
                        │             Realized False Negative Filter             │
                        │             (is_rto == 1 & ensemble_flag == 0)         │
                        └──────────────────────────┬─────────────────────────────┘
                                                   │
                                                   ▼
                        ┌────────────────────────────────────────────────────────┐
                        │         Dynamic Subgroup Discovery & Gating            │
                        │  - Conjunction Depth Cap (<= 3 features)               │
                        │  - Minimum Cohort Size (>= 30 mature orders)           │
                        │  - Chi-Square Significance Check (p < 0.05)            │
                        │  - Deterministic Zero-Cost Agenda Templating (0 LLM $) │
                        └──────────────────────────┬─────────────────────────────┘
                                                   │
                                                   ▼
                        ┌────────────────────────────────────────────────────────┐
                        │         Database Cooldown & Surge Bypass Gate          │
                        │  - Persisted in `miss_cluster_cooldowns` DB Table      │
                        │  - IF on cooldown AND volume <= 1.5x: SUPPRESS         │
                        │  - IF volume > 1.5x: BYPASS_SURGE (Threat Override)    │
                        └──────────────────────────┬─────────────────────────────┘
                                                   │
                                                   ▼
                        ┌────────────────────────────────────────────────────────┐
                        │         Strict Full-Validation Acceptance Gate         │
                        │         Net Value = 250 * TP - 15% Margin * FP         │
                        │             (Must be strictly > 0 on Split)            │
                        └────────────────────────────────────────────────────────┘
```

---

## 🔬 2. Detailed Technical Implementations

### A. Statistical Significance & Depth Guards on Subgroup Discovery
* **Depth Cap ($\le 3$ Conjunctions)**: Candidate subgroups are restricted to combining at most 3 features. Deeper combinatorial conjunctions overfit to small samples by construction and are discarded.
* **Minimum Cohort Size ($\ge 30$ Orders)**: Ensures lift is only computed on robust sample cohorts rather than trivial subsets (e.g. 5 misses out of 6 orders).
* **Chi-Square Contingency Test ($p < 0.05$)**: Every candidate cluster is tested using `scipy.stats.chi2_contingency` against the mature cohort baseline. Candidates that clear raw lift by random noise ($p \ge 0.05$) are rejected and logged in `rejected_insignificant_clusters` for complete audit transparency.

### B. Dual Mode Support (Dynamic Discovery + Pre-Validated Static Fallback)
* Configurable via `ResidualMiner(mode="dynamic" | "static")`.
* `static_fallback_clusters()` retains the original pre-validated heuristic clusters as a safe, pre-tested fallback.

### C. Deterministic Zero-Cost Agenda Templating
* Discovery agendas are synthesized deterministically directly from the signature dictionary without invoking an LLM.
* **Preserves LLM Budget**: Discovery itself incurs **0 LLM token cost**, strictly reserving API quota for the Generator/Reflector synthesis rounds.
* Guarantees every key-value condition in the signature is included without silent truncation.

### D. Cluster Cooldown Mechanism & Database State Persistence
* Added the `MissClusterCooldown` SQLAlchemy ORM table in `backend/app/db/models.py`.
* **Explicit Round Timing**: `cooldown_until_round` is explicitly computed as `current_round + cooldown_rounds` ($N=3$ rounds, matching Selector's unused pruning window).
* **Surge Bypass Exception**: If an attack vector escalates by **$>50\%$** in realized false-negative volume over its baseline, the cooldown is automatically bypassed (`status="BYPASSED_SURGE"`).
* **Fresh Discovery Guarantee**: Freshly discovered clusters are initialized with `cooldown_until_round <= current_round`, ensuring new threats are immediately eligible for hypothesis generation.

---

## 📊 3. Empirical Results & Live Verifications

### A. Live Execution on Real Validation Dataset (3,885 Orders)
*Command: `python backend/scratch/run_residual_miner_demo.py`*

```
===========================================================================
AEGIS-RTO: RESIDUAL-DRIVEN EVOLUTION DEMONSTRATION
===========================================================================

[1] Loaded Validation Dataset: 3,885 orders (Days 56–75).
    Active Incumbent Ensemble: 2 frozen baseline rules.

[2] Executing Residual Miner Scan (Current Day: 75, Maturity Window: 5 Days)...
    -> Total Orders Scanned:          3,885
    -> Mature Orders Evaluated:       2,890 (Days <= 70)
    -> In-Flight Orders Deferred:      995 (Days > 70)
    -> Realized False Negatives:      750 unflagged RTO losses
    -> False Negative Rate:           25.9%
    -> Miss Clusters Discovered:      3

---------------------------------------------------------------------------
[3] PRIMARY DISCOVERED MISS CLUSTER: [cluster_dyn_promo_cod_velocity]
    Title:        Promotional COD Device Velocity
    Miss Volume:  266 unflagged RTOs (38.2% of cohort)
    Signature:    {'payment_mode': 'COD', 'promo_code_used': True, 'avg_device_orders_24h': 0.14}

    [Generator Agenda]:
    "TARGETED AGENDA [Promotional COD Device Velocity]: We identified 266 unflagged RTO misses out of 697 mature orders matching signature [payment_mode=COD, promo_code_used=True, avg_device_orders_24h=0.14]. Synthesize a focused defense rule that flags this specific abuse pattern without over-flagging legitimate buyers who do not share all risk dimensions."

---------------------------------------------------------------------------
[4] TARGETED HYPOTHESIS PROPOSED BY GENERATOR:
    Rule ID:   hyp_residual_promo_burst_shield
    Name:      Targeted Promotional COD Velocity Shield
    Code:
def predict(df):
    return (
        (df['payment_mode'] == 'COD') &
        (df['customer_prior_orders'] == 0) &
        (df['promo_code_used'] == True) &
        (df['device_order_count_24h'] >= 2)
    )

---------------------------------------------------------------------------
[5] STRICT ACCEPTANCE GATE EVALUATION (Full 3,885 Validation Orders):
    Baseline Net Financial Savings:  Rs. 6,567.62
    Combined Net Financial Savings:  Rs. 6,817.62
    Net Financial Delta:             +Rs. 250.00
    Full-Validation Precision:       43.43%
    Full-Validation Recall:          3.88%
    True Positives Caught:           43
    False Positives Incurred:        56

    FINAL GATE VERDICT:              [PROMOTED]
    Decision Reason:                 ACCEPTED: Targeted rule added +Rs. 250.00 net financial savings on full validation (TP=43, FP=56, Net=Rs. 6,817.62).
===========================================================================
```

---

### B. Full Test Suite Verification (63/63 Passing)
*Command: `python -m pytest backend/tests/ -v`*

| Test Module | Tests | Result | Coverage Area |
|---|---|---|---|
| `test_residual_miner.py` | 10 | **10 Passed** | Maturity gate, significance testing, depth cap, fallback mode, deterministic agendas, cooldown lifecycle, surge bypass, cost gate, leakage guard, shipped holdout. |
| `test_router.py` | 3 | **3 Passed** | 3-way routing tiers, Section 6.2 honest metrics split, scoring APIs. |
| `test_drift_and_promotion.py` | 6 | **6 Passed** | Z-score, CUSUM drift detection, precision collapse, automated rollback, single-touch isolation. |
| `test_spike_monitor.py` | 3 | **3 Passed** | Live stream baseline, critical spike alert injection, monitor APIs. |
| `test_lineage.py` | 6 | **6 Passed** | DAG endpoints, graph traversal, health checks. |
| `test_selector.py` | 4 | **4 Passed** | Submodular forward greedy selection, Jaccard redundancy pruning, baseline snapshotting. |
| `test_sandbox.py` | 8 | **8 Passed** | AST security blocks (`import`, `exec`, `eval`, `open`, `__subclasses__`), timeout enforcement, runtime error handling. |
| `test_evaluator.py` | 6 | **6 Passed** | Cost-weighted rupee objective, forbidden column stripping, diagnostic failure extraction. |
| `test_agents.py` | 4 | **4 Passed** | Generator, Reflector, Syntax Repair handler, Notepad ranking. |
| `test_db.py` | 3 | **3 Passed** | Schema creation, isolated table ingestion, ORM relationship cascades. |
| `test_regression.py` | 4 | **4 Passed** | Cold-start tolerance, regression buffer, financial drop rejection. |
| `test_concerns2_fixes.py` | 5 | **5 Passed** | Decoy columns, blinded feature mapping, paired bootstrap resampling, defense-only gate. |
| `test_shadow_control.py` | 1 | **1 Passed** | 3-way shadow control ablation matrix consistency. |
| **TOTAL** | **63** | **63 / 63 PASSED (100%)** | Full System Integration |

---

### C. Held-Out Test Split Benchmark (Single-Touch Isolation)

| Metric | Measured Value | Operational Meaning |
|---|---|---|
| **Test Volume** | **2,641 Orders** | 100% unseen post-drift chronological split (Days 76–89) |
| **Auto-Decided Volume** | **2,588 Orders (97.99%)** | Decided sub-millisecond without human labor |
| **Auto-Approved Orders** | **2,537 Orders** | Clean orders passed to fulfillment |
| **Auto-Blocked Orders** | **51 Orders** | High-confidence fraud intercepts |
| **Auto-Decided Precision** | **37.25%** | True fraud block rate |
| **Manual Review Queue** | **53 Orders (2.01%)** | Ambiguous cases routed to human triage |
| **Review Queue Risk Density** | **47.17% (1.52x)** | Concentrates fraud for human analysts |
| **Auto-Decided Net Savings** | **+₹2,458.91** | Net financial profit after all customer insult costs deducted |
| **Paired Bootstrap Delta ($B=2,000$)** | **+₹6,861.66 [$₹5,214.30$, $₹8,590.10$]** | Statistically significant lift ($p < 0.0001$) |

---

## ❓ 4. Anticipated Panel Questions & Answers

#### Q1: "What stops the same miss cluster from being re-proposed every round after it's rejected or pruned?"
> **Answer**: Aegis-RTO enforces a **Miss-Cluster Cooldown Window** ($N=3$ rounds, matching the Selector's unused-pruning window). When a hypothesis synthesized for a cluster is rejected by the cost gate or pruned by the Selector, its `cluster_id` is placed on cooldown and persisted in the `miss_cluster_cooldowns` DB table. During cooldown, the cluster is suppressed from the Generator's agenda to avoid wasting LLM budget. **Surge Exception**: If the cluster's realized false-negative volume increases by **$>50\%$** over its last mined baseline, the cooldown is automatically bypassed so escalating attacks are never ignored.

#### Q2: "Why cap conjunction depth at 3 features during dynamic clustering?"
> **Answer**: Combinatorial search over multiple features and continuous thresholds can easily discover 5-feature conjunctions that appear to have 100% RTO rate purely due to random chance on small sample slices. Restricting conjunction depth to $\le 3$, enforcing cohort size $\ge 30$, and requiring Chi-Square $p < 0.05$ guarantees that only robust, statistically significant fraud cohorts are surfaced.

#### Q3: "Does residual mining introduce token costs on every scan?"
> **Answer**: No. Subgroup discovery, Chi-Square significance testing, and agenda construction are completely deterministic and run in $\approx 20\text{ ms}$ on CPU with **0 LLM calls**. LLM calls are strictly reserved for the Generator and Reflector synthesis loops.
