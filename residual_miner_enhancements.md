# Aegis-RTO: Dynamic Residual Mining & Cooldown Architecture

> **Technical Architecture & Verification Summary**  
> **Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager (Return-Risk Scorer & Adaptive Defense)**

---

## 📌 Overview

This document details the design and implementation of the **Dynamic Residual Miner**, **Miss-Cluster Cooldown Mechanism**, **Statistical Significance Guards**, and **SQLAlchemy Database State Persistence** in Aegis-RTO.

---

## 🏛️ Key Architectural Features Implemented

### 1. Statistical Significance & Depth Guards on Subgroup Discovery
* **Conjunction Depth Cap ($\le 3$ Features)**: Discovered subgroups are restricted to combining at most 3 features. Deeper combinatorial conjunctions are rejected to prevent overfitting to small sample slices.
* **Minimum Cohort Size ($\ge 30$ Orders)**: Ensures statistical lift is only computed on robust sample sizes, preventing artificial high-lift scores on tiny samples (e.g. 2 misses out of 3 orders).
* **Chi-Square Significance Test ($p < 0.05$)**: Every candidate cluster is evaluated using `scipy.stats.chi2_contingency` against the mature baseline distribution. Candidates clearing raw lift purely by chance ($p \ge 0.05$) are rejected and logged in `rejected_insignificant_clusters` for complete audit transparency.

```python
# Statistical Rationale:
# With multiple feature combinations and thresholds searched combinatorially,
# some conjunctions clear a raw lift bar by chance alone (multiple-testing problem).
# Requiring p < 0.05 from a Chi-Square test prevents overfitting to random small subsets.
```

---

### 2. Dual-Mode Support (Dynamic Discovery + Pre-Validated Static Fallback)
* **Switchable Engine Mode**: Added `mode = "dynamic" | "static"` to `ResidualMiner` (defaults to `"dynamic"`).
* **Pre-Validated Fallback**: `static_fallback_clusters()` preserves the original 3 pre-validated heuristic clusters (`cluster_promo_cod_burst`, `cluster_late_night_impulse`, `cluster_low_value_impulse_cod`) as a safe, pre-tested fallback path.

---

### 3. Deterministic Zero-Cost Agenda Templating
* **Zero Discovery LLM Overhead**: Agendas are generated via deterministic templating directly from the feature signature dictionary (e.g., `payment_mode=COD, promo_code_used=True, avg_device_orders_24h=0.14`).
* **Preserves Token Budget**: Discovery itself incurs **0 LLM API calls**, strictly reserving token budget for the Generator/Reflector synthesis rounds per Section 9.2's budget cap.
* **No Silent Truncation**: Guarantees that every key-value condition in the feature signature is preserved in the prompt delivered to the Generator agent.

---

### 4. Miss-Cluster Cooldown & Persistent Database Lifecycle
* **Database State Persistence**: Added the `MissClusterCooldown` SQLAlchemy ORM model (`miss_cluster_cooldowns` table) in `backend/app/db/models.py` to persist cooldown states across server restarts and distributed workers.
* **Explicit Cooldown Window ($N = 3$ Rounds)**: When a synthesized hypothesis is rejected by the strict cost gate or pruned by the Selector, its `cluster_id` enters an $N=3$ round cooldown (matching the Selector's unused-pruning window).
* **New Cluster Eligibility**: Freshly discovered clusters are initialized with `cooldown_until_round <= current_round`, ensuring new attack patterns are immediately eligible and never born on cooldown.
* **$>50\%$ Miss Volume Surge Bypass**: If an attack vector escalates and realized false negatives grow by $>50\%$ over the last mined baseline, the cooldown is automatically bypassed (`status="BYPASSED_SURGE"`) so emerging threats are never ignored.

---

## 📊 Live Verification & Test Suite

### Full Verification Suite (63/63 Tests Passing)
```bash
python -m pytest backend/tests/ -v
```

| Test Component | Tests | Status |
|---|---|---|
| `test_agents.py` (Generator, Reflector, Repair, Notepad) | 4 | **PASSED** |
| `test_concerns2_fixes.py` (Blinded mapping, Bootstrap CI, Defense Audit) | 5 | **PASSED** |
| `test_db.py` (Schema creation, CSV ingestion, ORM models) | 3 | **PASSED** |
| `test_drift_and_promotion.py` (Z-Score, CUSUM, Champion-Challenger) | 6 | **PASSED** |
| `test_evaluator.py` (Cost formulas, Single-touch test lock, Sanitization) | 6 | **PASSED** |
| `test_lineage.py` (Graph lineage, Node inspection, Endpoints) | 6 | **PASSED** |
| `test_regression.py` (Gate 1 tolerance buffer, Cold start checks) | 4 | **PASSED** |
| `test_residual_miner.py` (Maturity gate, Chi-Square test, Cooldowns, Surge) | 10 | **PASSED** |
| `test_router.py` (3-Way tiers, Section 6.2 metric split, Scoring APIs) | 3 | **PASSED** |
| `test_sandbox.py` (AST security, timeout protection, import blocks) | 7 | **PASSED** |
| `test_selector.py` (Submodular forward selection, Jaccard pruning) | 4 | **PASSED** |
| `test_shadow_control.py` (3-Way rounds-matched ablation matrix) | 1 | **PASSED** |
| `test_spike_monitor.py` (2.5σ alerts, burst traffic, APIs) | 4 | **PASSED** |
| **TOTAL** | **63** | **100% PASS RATE** |

---

### Live Execution Demonstration Output
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
    False Positives Insulted:        56

    FINAL GATE VERDICT:              [PROMOTED]
    Decision Reason:                 ACCEPTED: Targeted rule added +Rs. 250.00 net financial savings on full validation (TP=43, FP=56, Net=Rs. 6,817.62).
===========================================================================
```

---

## ❓ Anticipated Panel Q&A

#### Q: "What stops the same miss cluster from being re-proposed every round after it's rejected or pruned?"
> **Answer**: Aegis-RTO enforces a **Miss-Cluster Cooldown Window** ($N=3$ rounds, matching the Selector's unused-pruning window). When a hypothesis synthesized for a cluster is rejected by the cost gate or pruned by the Selector, its `cluster_id` is placed on cooldown and persisted in the `miss_cluster_cooldowns` DB table. During cooldown, the cluster is suppressed from the Generator's agenda to avoid wasting LLM budget. **Surge Exception**: If the cluster's realized false-negative volume increases by **$>50\%$** over its last mined baseline, the cooldown is automatically bypassed so escalating attacks are never ignored.

#### Q: "How does the system avoid the multiple-testing problem during subgroup discovery?"
> **Answer**: By applying three cascading statistical filters:
> 1. **Conjunction Depth Cap ($\le 3$)**: Prevents searching overfitted high-dimensional combinations.
> 2. **Minimum Cohort Size ($\ge 30$)**: Restricts candidates to sufficiently populated segments.
> 3. **Chi-Square Contingency Test ($p < 0.05$)**: Requires formal statistical significance against the mature non-RTO baseline before an agenda is constructed.
