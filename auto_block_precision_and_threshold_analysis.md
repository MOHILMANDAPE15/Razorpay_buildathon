# Auto-Block Precision & Routing Threshold Analysis

> **Quick Reference Guide: Precision, Economics & Threshold Dynamics**  
> **Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager**

---

## 📌 Executive Summary

* **Current Metric on Held-Out Test (2,641 Orders)**:
  - **Auto-Block Precision**: `37.25%` (19 True Positives, 32 False Positives out of 51 Auto-Blocked).
  - **Review Queue Concentration**: `47.17%` (25 True Positives out of 53 Review Cases $\rightarrow$ **1.52x Risk Multiplier**).
  - **Auto-Decided Net Financial Savings**: **`+₹2,458.91`** (Net positive profit).

---

## 💰 The Mathematical Proof: Why 37.25% Precision Is Economically Profitable

In e-commerce fraud management, precision cannot be judged in isolation from **Order Value (AOV)** and **Unit Economics**:

$$\text{Net ROI} = (\text{True Positives} \times ₹250\text{ Avoided RTO}) - \sum (\text{False Positive Order Value} \times 15\%\text{ Margin Loss})$$

### On Our Flagged Cohort:
* **Avoided RTO Benefit per Fraud**: **$+₹250.00$**
* **Average Flagged Order Value**: **$₹450.00$** (Low-ticket impulse items)
* **Customer Margin Loss per FP**: $₹450 \times 15\% = \mathbf{₹67.50}$
* **Break-Even Precision Ratio**:
  $$\text{Break-Even Precision} = \frac{₹67.50}{₹250.00 + ₹67.50} = \mathbf{21.26\%}$$

> **Key Insight**: Because the flagged orders are low-ticket COD items (₹450 AOV), any precision above **21.26%** yields **positive net financial savings**. At **37.25% precision**, the system generates **+₹2,458.91 in net profit**.

---

## 📊 Threshold Comparison (Validation Split: 3,885 Orders)

| Threshold Policy | Auto-Block Orders | Auto Precision | Auto Net Savings | Review Queue Vol | Review Risk Density | Trade-off Summary |
|---|---|---|---|---|---|---|
| **$\ge 0.60$ (Aggressive)** | 98 orders | 42.86% | **+₹6,567.62** | 0.00% | 0.00% | Maximum automated savings, zero human review. |
| **$\ge 0.70$ (Current Baseline)** | **26 orders** | **50.00%** | **+₹2,383.95** | **1.85%** | **40.28%** | **Balanced**: High automated efficiency + concentrated review queue. |
| **$\ge 0.80$ (Conservative)** | 7 orders | 42.86% | **+₹521.49** | **2.34%** | **42.86%** | Minimal auto-blocks; shifts financial recovery onto human review team. |

---

## 🎯 30-Second Pitch for the Judges (Section 10 FAQ)

> **Judge**: *"Why is your auto-block precision 37.25%? Doesn't that mean 6 out of 10 auto-blocked orders are legitimate customers?"*
> 
> **Your Answer**:  
> *"In COD risk management, precision must be weighted by order value. The orders our engine auto-blocks are low-ticket items (₹450 AOV), where blocking a false positive costs only ₹67.50 in lost margin, but catching an RTO saves ₹250 in logistics. The break-even precision is just 21.26% — so 37.25% precision yields **+₹2,458 in net automated savings**.
> 
> Meanwhile, for ambiguous orders, our 3-way router concentrates risk in the human review queue to **47.17% (a 1.52x multiplier over base rate)**, giving merchants the optimal balance of frictionless checkout (97.99% automated) and positive unit economics."*
