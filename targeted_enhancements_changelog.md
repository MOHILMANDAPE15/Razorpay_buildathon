# Aegis-RTO: Targeted Enhancements & Novelty Verification Changelog

> **Summary of Targeted Fixes, Significance Guard Visibility, and Dynamic Novelty Verification**  
> **Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager (Return-Risk Scorer & Adaptive Defense)**

---

## 📌 Overview of Enhancements

This document summarizes the three targeted additions made to the **Aegis-RTO Residual Mining Engine**, confirming zero regression across held-out splits, routing thresholds, or cost acceptance logic.

---

## 🛠️ 1. Itemized List of Changes Made

### 1. Output Label Normalization
* **Old Label**: `False Positives Insulted`
* **Updated Label**: `False Positives Incurred`
* **Files Updated**:
  - `backend/scratch/run_residual_miner_demo.py`
  - `residual_mining_and_cooldown_report.md`
  - Codebase docstrings across `backend/app/engine/`
* **Verification**: Verified zero remaining instances of "False Positives Insulted" across `backend/`.

---

### 2. Visibility & Empirical Testing of the Significance Guard
* **Demo Script Visibility**:
  - Updated `run_residual_miner_demo.py` to explicitly display the count and rejection reasons of candidate clusters filtered out by the Chi-Square significance check or minimum cohort size guard:
    ```
    -> Insignificant Candidates Filtered: 1
       * [Late-Night High-Risk Location COD] Rejected: Failed significance check (p=0.0821 >= 0.05)
    ```
* **New Unit Test**:
  - Added `test_significance_guard_populates_rejected_clusters` in `backend/tests/test_residual_miner.py`.
  - Injects a synthetic small-cohort/low-significance distribution and asserts that `rejected_insignificant_clusters` is populated with `RejectedClusterCandidate` models containing full diagnostic reasons.

---

### 3. Dynamic Discovery Novelty Verification
* **New Standalone Script**:
  - Created `backend/scratch/verify_dynamic_discovery_novelty.py`.
  - Runs the dynamic subgroup miner on real post-drift validation data (Days 56–75, 3,885 orders) with `static_fallback_clusters()` disabled (`mode="dynamic"`).
  - Automatically compares discovered cluster signatures against the 3 static baseline patterns (`cluster_promo_cod_burst`, `cluster_late_night_impulse`, `cluster_low_value_impulse_cod`).
* **Live Discovery Results**:
  ```
  ================================================================================
  AEGIS-RTO: DYNAMIC DISCOVERY NOVELTY VERIFICATION
  ================================================================================

  [1] Evaluating Post-Drift Distribution (3,885 orders, Days 56–75)...
      Mode: DYNAMIC SUBGROUP MINER (Static fallback disabled)

  [2] Discovery Results:
      -> Realized False Negatives Mined: 750
      -> Dynamically Discovered Clusters: 3
      -> Insignificant Candidates Filtered: 1

  --------------------------------------------------------------------------------
  A. REPRODUCED / REFINED BASELINE PATTERNS (Statistical Verification):
      * [cluster_dyn_promo_cod_velocity] 'Promotional COD Device Velocity'
        Matched Against: Promotional COD Velocity (Static)
        Miss Volume:     266 orders (Lift: 1.47x, p-value: 0.0)
        Signature:       {'payment_mode': 'COD', 'promo_code_used': True, 'avg_device_orders_24h': 0.14}
      * [cluster_dyn_low_value_first_time_cod] 'Low-Value First-Time COD Impulse'
        Matched Against: Low-Value First-Time COD (Static)
        Miss Volume:     106 orders (Lift: 1.21x, p-value: 0.0189)
        Signature:       {'payment_mode': 'COD', 'max_order_value': 600.0, 'customer_prior_orders': 0}

  --------------------------------------------------------------------------------
  B. NOVEL DISCOVERED ABUSE PATTERNS (Beyond Static Fallback):
      * [NOVEL] [cluster_dyn_new_account_high_val_cod] 'New Account High-Value COD Impulse'
        Novelty Status:  DISCOVERED AUTONOMOUSLY (No hand-coded static equivalent)
        Miss Volume:     67 orders (Lift: 1.72x, p-value: 0.0)
        Conjunctions:    Depth 3 (<= 3 feature cap)
        Signature:       {'payment_mode': 'COD', 'max_account_age_days': 2, 'min_order_value': 2500.0}
        Agenda String:   "TARGETED AGENDA [New Account High-Value COD Impulse]: We identified 67 unflagged RTO misses out of 150 mature orders matching signature [payment_mode=COD, max_account_age_days=2, min_order_value=2500.0]. Synthesize a focused defense rule that flags this specific abuse pattern without over-flagging legitimate buyers who do not share all risk dimensions."

  ================================================================================
  NOVELTY VERIFICATION SUMMARY:
  Total Discovered: 3 | Matched/Refined: 2 | Novel: 1
  ================================================================================
  ```
* **New Unit Test**:
  - Added `test_dynamic_discovery_novelty_finds_unseen_patterns` in `backend/tests/test_residual_miner.py` asserting that novel patterns beyond static handcoded baselines are discovered autonomously.

---

## 🧪 2. Verification & Test Suite Summary

* **Test Command**: `python -m pytest backend/tests/ -v`
* **Test Suite Pass Rate**: **65 / 65 PASSED (100%)**

| Test Module | Total Tests | Status |
|---|---|---|
| `backend/tests/test_residual_miner.py` | 12 | **12 / 12 PASSED** |
| `backend/tests/test_agents.py` | 4 | **4 / 4 PASSED** |
| `backend/tests/test_concerns2_fixes.py` | 5 | **5 / 5 PASSED** |
| `backend/tests/test_db.py` | 3 | **3 / 3 PASSED** |
| `backend/tests/test_drift_and_promotion.py` | 6 | **6 / 6 PASSED** |
| `backend/tests/test_evaluator.py` | 6 | **6 / 6 PASSED** |
| `backend/tests/test_lineage.py` | 6 | **6 / 6 PASSED** |
| `backend/tests/test_regression.py` | 4 | **4 / 4 PASSED** |
| `backend/tests/test_router.py` | 3 | **3 / 3 PASSED** |
| `backend/tests/test_sandbox.py` | 8 | **8 / 8 PASSED** |
| `backend/tests/test_selector.py` | 4 | **4 / 4 PASSED** |
| `backend/tests/test_shadow_control.py` | 1 | **1 / 1 PASSED** |
| `backend/tests/test_spike_monitor.py` | 3 | **3 / 3 PASSED** |
| **TOTAL** | **65** | **65 / 65 PASSED (100%)** |

---

## 🔒 3. Invariance Guarantees Maintained
* **Held-Out Test Set**: Untouched and isolated via `evaluate_on_held_out_test()`.
* **Routing Thresholds**: Untouched (Auto-Approve $< 0.35$, Auto-Block $\ge 0.70$, Review Queue $0.35–0.70$).
* **Cost Acceptance Gate**: Untouched ($\text{Net Savings} = ₹250 \times \text{TP} - \sum \text{Order Value} \times 15\% \times \text{FP} > 0$).
