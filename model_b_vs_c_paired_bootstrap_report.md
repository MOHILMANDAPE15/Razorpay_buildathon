# Paired Bootstrap Significance Report: Model B vs. Model C at T=0.70

> **Follow-Up Statistical Significance Audit on Held-Out Test Data**  
> **Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager (Return-Risk Scorer & Adaptive Defense)**

---

## 📌 Executive Summary

Per Section 4.7 of the Aegis-RTO design doc, we conducted a rigorous **paired bootstrap significance test ($B=2,000$ resamples)** comparing:
* **Model B**: Self-Evolved Drift-Adapted Champion (5 rounds, exposed to Days 56–75 drift).
* **Model C**: Rounds-Matched Shadow Control (5 rounds, trained strictly on Days 0–55 pre-drift data, 0% drift exposure).

Both models were evaluated order-for-order on the **identical held-out test dataset (Days 76–89, 2,641 unseen orders)** at the production operating threshold **$T = 0.70$**.

---

## 📊 1. Point Estimates & Paired Difference at T=0.70

*Base ground-truth RTO rate: **31.01%** (819 RTOs / 2,641 orders).*

| Metric | Model B (Drift Champion) | Model C (Shadow Control) | Point Delta ($\Delta = B - C$) |
|---|---|---|---|
| **Auto-Blocked Volume** | 51 orders (1.93%) | 63 orders (2.39%) | **$-12\text{ orders}$** |
| **True Positives (TP)** | 19 orders | 27 orders | **$-8\text{ orders}$** |
| **False Positives (FP)** | 32 orders | 36 orders | **$-4\text{ orders}$** |
| **Auto-Block Precision** | **37.25%** | **42.86%** | **$-5.60\%\text{ pts}$** |
| **Auto-Block Recall** | **2.32%** | **3.30%** | **$-0.98\%\text{ pts}$** |
| **Auto-Decided Net Savings** | **+₹2,458.91** | **+₹4,387.55** | **$-₹1,928.64$** |

---

## 🔬 2. Paired Bootstrap 95% Confidence Intervals (B=2,000 Resamples)

To evaluate whether these observed point differences represent statistically real effects or sample variance, we computed empirical paired bootstrap distributions over 2,000 resamples:

| Metric Evaluated | Point Estimate ($\Delta$) | Paired 95% Bootstrap CI | Empirical $p$-value | Contains Zero ($H_0: \Delta = 0$)? | Statistical Significance ($\alpha = 0.05$) |
|---|---|---|---|---|---|
| **$\Delta$ Net Financial Savings** | **$-₹1,928.64$** | **$[-₹4,721.01, +₹622.37]$** | $p = 0.1510$ | **`YES`** | ❌ **Not Significant** |
| **$\Delta$ Precision** | **$-5.60\%$** | **$[-19.93\%, +7.89\%]$** | $p = 0.4300$ | **`YES`** | ❌ **Not Significant** |
| **$\Delta$ Recall** | **$-0.98\%$** | **$[-2.19\%, +0.13\%]$** | $p = 0.1170$ | **`YES`** | ❌ **Not Significant** |

---

## 🎯 3. Plain-English Statistical Conclusion & Scoped Limitations

> **Statistical Verdict**:  
> *"All three paired bootstrap confidence intervals (Net Savings, Precision, and Recall) cross zero at the 95% confidence level ($p > 0.10$ across all metrics). 
> 
> At the production operating threshold $T = 0.70$, **Model B and Model C are statistically indistinguishable** on the held-out test split. 
> 
> **Reported Limitation**: Because the confidence interval on net savings $[-₹4,721.01, +₹622.37]$ spans both positive and negative values, the held-out test data at $T=0.70$ does not statistically resolve in favor of either drift adaptation or compute scaling alone. Statistical divergence emerges only under tighter operating thresholds ($T=0.75$), where Model B achieves a higher precision ceiling (70.00% vs 54.05%) at a significantly reduced review queue volume (2.01% vs 7.04%)."*
