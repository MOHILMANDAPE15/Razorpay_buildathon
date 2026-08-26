# Auto-Block Count Reconciliation Audit: 51 vs. 23 Orders

> **Diagnostic Audit Reconciling Auto-Block Counts at Threshold T=0.70**  
> **Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager (Return-Risk Scorer & Adaptive Defense)**

---

## 📌 Executive Summary

This audit reconciles why two prior runs reported different auto-blocked order volumes at the same threshold ($T=0.70$) on the **held-out test split (Days 76–89, 2,641 orders)**:

* **Run A**: `51 Orders Auto-Blocked` (19 TP / 32 FP, 37.25% Precision, 53 Review Cases, +₹2,458.91 Net Savings).
* **Run B**: `23 Orders Auto-Blocked` (10 TP / 13 FP, 43.48% Precision, 76 Review Cases, +₹1,715.25 Net Savings).

### 🔍 The Finding:
**Both numbers are mathematically correct, but evaluate two different model ensemble versions on the identical dataset**:
1. **51 Auto-Blocked Orders** is the performance of the **Self-Evolved Drift-Adapted Champion (Model B, 3 Rules)**.
2. **23 Auto-Blocked Orders** is the performance of the **Static Frozen v1 Baseline (Model A, 2 Rules)**.

---

## 🔬 1. Dataset Verification (Identical Data & SHA-256 Checksum)

Both runs loaded the exact same file with zero variance at the data layer:
* **File Path**: `idea_and_data/held_out_test.csv`
* **Total Volume**: `2,641 rows`
* **Date Range**: `Day 76 to Day 89`
* **Ground Truth RTO Base Rate**: `31.01%` (819 RTOs / 2,641 orders)
* **SHA-256 Checksum**: `85a69a77986168033c3e1ae1b6a477bede31723817ea375153217c1738981e05`

---

## ⚖️ 2. Side-by-Side Model Comparison at T=0.70

Both runs used the **identical ThreeWayRouter formula** (`risk_score = ambient_risk + 0.45 * rules_matched`), but scored with different active ensembles:

| Attribute | Run B: Static Frozen v1 (Model A) | Run A: Drift-Adapted Champion (Model B) |
|---|---|---|
| **Model Name** | `frozen_v1_baseline` | `drift_adapted_champion_v2` |
| **Model Description** | Static pre-drift baseline model | Self-evolved drift-adapted model |
| **Active Rules** | **2 Rules**:<br>1. `hyp_r3_3_f4b4`<br>2. `hyp_r2_3_bd99` | **3 Rules**:<br>1. `hyp_evolved_promo_burst_cod`<br>2. `hyp_evolved_late_night_impulse_cod`<br>3. `hyp_r3_3_f4b4` |
| **Auto-Blocked Volume** | **23 orders** | **51 orders** |
| **Auto-Blocked TP / FP** | **10 TP / 13 FP** | **19 TP / 32 FP** |
| **Auto-Block Precision** | **43.48%** | **37.25%** |
| **Manual Review Volume** | **76 orders (2.88%)** | **53 orders (2.01%)** |
| **Review Queue RTO Density** | **48.68% (1.57x base rate)** | **47.17% (1.52x base rate)** |
| **Auto Net Financial Savings** | **+₹1,715.25** | **+₹2,458.91** |

---

## 📊 3. Complete Threshold Sweep for Both Models on Held-Out Test Split

### Model A: Static Frozen v1 Ensemble (2 Rules)
*Trained on Days 0–55 pre-drift; evaluated on unseen post-drift test split (2,641 orders):*

| Threshold | Auto-Block Volume | Auto Precision | Auto TP | Auto FP | Manual Review Volume | Review Queue RTO% | Auto Net Savings (INR) |
|---|---|---|---|---|---|---|---|
| **$0.60$** | 99 orders | 47.47% | 47 | 52 | 0 orders (0.00%) | 0.00% | **+₹8,072.21** |
| **$0.65$** | 99 orders | 47.47% | 47 | 52 | 0 orders (0.00%) | 0.00% | **+₹8,072.21** |
| **$0.70$ (Baseline)** | **23 orders** | **43.48%** | **10** | **13** | **76 orders (2.88%)** | **48.68% (1.57x)** | **+₹1,715.25** |
| **$0.75$** | 6 orders | 50.00% | 3 | 3 | 93 orders (3.52%) | 47.31% | **+₹535.62** |
| **$0.80$** | 6 orders | 50.00% | 3 | 3 | 93 orders (3.52%) | 47.31% | **+₹535.62** |
| **$0.85$** | 6 orders | 50.00% | 3 | 3 | 93 orders (3.52%) | 47.31% | **+₹535.62** |
| **$0.90$** | 6 orders | 50.00% | 3 | 3 | 93 orders (3.52%) | 47.31% | **+₹535.62** |

---

### Model B: Self-Evolved Drift-Adapted Champion (3 Rules)
*Autonomously adapted on Days 56–75; evaluated on unseen post-drift test split (2,641 orders):*

| Threshold | Auto-Block Volume | Auto Precision | Auto TP | Auto FP | Manual Review Volume | Review Queue RTO% | Auto Net Savings (INR) |
|---|---|---|---|---|---|---|---|
| **$0.60$** | 104 orders | 42.31% | 44 | 60 | 0 orders (0.00%) | 0.00% | **+₹6,861.66** |
| **$0.65$** | 103 orders | 41.75% | 43 | 60 | 1 order (0.04%) | 100.00% | **+₹6,611.66** |
| **$0.70$ (Champion)** | **51 orders** | **37.25%** | **19** | **32** | **53 orders (2.01%)** | **47.17% (1.52x)** | **+₹2,458.91** |
| **$0.75$** | 10 orders | 70.00% | 7 | 3 | 94 orders (3.56%) | 39.36% | **+₹1,571.13** |
| **$0.80$** | 10 orders | 70.00% | 7 | 3 | 94 orders (3.56%) | 39.36% | **+₹1,571.13** |
| **$0.85$** | 10 orders | 70.00% | 7 | 3 | 94 orders (3.56%) | 39.36% | **+₹1,571.13** |
| **$0.90$** | 10 orders | 70.00% | 7 | 3 | 94 orders (3.56%) | 39.36% | **+₹1,571.13** |

---

## 🎯 4. Key Takeaways for Panel Presentations

1. **Why Model B Auto-Blocks 51 Orders (vs 23 for Model A)**:
   The self-evolving engine added targeted defense rules against promotional COD velocity abuse and late-night ordering. This allows the champion to flag emerging fraud vectors that the static baseline missed, nearly doubling auto-blocked True Positives from **10 to 19 TP** and increasing automated net savings to **+₹2,458.91**.
2. **Consistency Across Documentation**:
   - The headline metric **51 auto-blocks / 37.25% precision / +₹2,458.91 savings** represents the **Self-Evolved Champion**.
   - The **23 auto-blocks / 43.48% precision / +₹1,715.25 savings** represents the **Static Frozen v1 Baseline**.
