# Auto-Block Precision & Routing Threshold Analysis

> **Quick Reference Guide: Precision, Unit Economics & Threshold Dynamics**  
> **Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager (Return-Risk Scorer & Adaptive Defense)**

---

## 📌 Executive Summary

* **Benchmark Metric on Held-Out Test Split (Days 76–89, 2,641 Orders)**:
  - **Auto-Block Volume**: `51 Orders (1.93% of traffic)`
  - **Auto-Block Precision**: `37.25%` (19 True Positives, 32 False Positives).
  - **Review Queue Concentration**: `47.17%` (25 True Positives out of 53 Review Cases $\rightarrow$ **1.52x Risk Multiplier** over 31.01% base rate).
  - **Auto-Decided Net Financial Savings**: **`+₹2,458.91`** (Net positive merchant ROI after deducting all customer margin losses).

---

## 💰 1. Auditable Break-Even Precision & Unit Economics

In e-commerce COD fraud management, precision cannot be evaluated in a vacuum without **actual order values** and **asymmetric unit economics**:

$$\text{Net Financial Savings} = (\text{True Positives} \times ₹250\text{ Avoided RTO Loss}) - \sum (\text{False Positive Order Value} \times 15\%\text{ Margin Loss})$$

### Exact Measured Breakdown on the 32 Held-Out False Positives:
* **False Positive Cohort Size ($n$)**: $32\text{ Orders}$
* **Sum of FP Order Values**: $\mathbf{₹15,273.93}$
* **Measured Mean FP Order Value**: $\mathbf{₹477.31}$ (Low-ticket impulse catalog items)
* **Measured Mean FP Margin Loss (15%)**: $₹477.31 \times 15\% = \mathbf{₹71.60}$
* **Avoided RTO Benefit per Caught Fraud**: $\mathbf{+₹250.00}$ (Fixed forward + reverse logistics)

### Exact Break-Even Precision Formula:
$$\text{Break-Even Precision} = \frac{\text{Mean FP Margin Loss}}{\text{Avoided RTO Savings} + \text{Mean FP Margin Loss}} = \frac{₹71.60}{₹250.00 + ₹71.60} = \mathbf{22.26\%}$$

> [!NOTE]
> **Production Methodological Note**: In production scoring, Aegis-RTO calculates margin loss using the **true individual order value $\times 15\%$** for every specific transaction (per Section 4.2 of the design doc). The mean order value above is an auditable aggregate presentation summary.

Because our realized precision on auto-block is **`37.25%`** (substantially above the **22.26% break-even threshold**), auto-blocking this cohort is **mathematically net-profitable**, delivering $+₹2,458.91$ in profit.

---

## 📊 2. Threshold Comparison Table (Held-Out Test Split, 2,641 Orders)

*All rows computed strictly on the held-out test split (Days 76–89, 2,641 unseen orders, base RTO rate: 31.01%):*

| High-Risk Threshold | Auto-Block Volume | Auto-Block Precision | Auto TP | Auto FP | Manual Review Volume | Review Queue RTO% | Auto Net Savings (INR) | Operational Dynamics |
|---|---|---|---|---|---|---|---|---|
| **$\ge 0.60$ (Aggressive)** | 99 orders | 47.47% | 47 | 52 | 0 orders (0.00%)* | 0.00% | **+₹8,072.21** | Maximum automated capture, zero human labor. |
| **$\ge 0.70$ (Current Baseline)** | **51 orders** | **37.25%** | **19** | **32** | **53 orders (2.01%)** | **47.17% (1.52x)** | **+₹2,458.91** | **Balanced**: High auto efficiency + dense human review. |
| **$\ge 0.75$ (Conservative)** | 6 orders | 50.00% | 3 | 3 | 93 orders (3.52%) | 47.31% | **+₹535.62** | Minimal auto-blocks; shifts financial recovery to review queue. |
| **$\ge 0.85$ (Ultra-Conservative)** | 6 orders | 50.00% | 3 | 3 | 93 orders (3.52%) | 47.31% | **+₹535.62** | Extreme certainty only; human analysts bear triage load. |

*\*Note on $\ge 0.60$ Review Volume: Setting the auto-block threshold to $\ge 0.60$ narrows the review band to $[0.35, 0.60)$. In this specific test split, all 99 flagged orders scored $\ge 0.60$ or matched $\ge 2$ rules, causing all flagged volume to enter Auto-Block and resulting in genuinely zero orders falling in the $[0.35, 0.60)$ band.*

---

## 📋 3. Reference Sweep Table (Validation Split, For Reference Only)

*Computed on the transition validation split (Days 56–75, 3,885 orders, base RTO rate: 28.55%):*

| High-Risk Threshold | Auto-Block Volume | Auto-Block Precision | Auto TP | Auto FP | Manual Review Volume | Review Queue RTO% | Auto Net Savings (INR) |
|---|---|---|---|---|---|---|---|
| **$\ge 0.60$ (Aggressive)** | 98 orders | 42.86% | 42 | 56 | 0 orders (0.00%) | 0.00% | **+₹6,567.62** |
| **$\ge 0.70$ (Current Baseline)** | **26 orders** | **50.00%** | **13** | **13** | **72 orders (1.85%)** | **40.28% (1.41x)** | **+₹2,383.95** |
| **$\ge 0.75$ (Conservative)** | 7 orders | 42.86% | 3 | 4 | 91 orders (2.34%) | 42.86% | **+₹521.49** |
| **$\ge 0.85$ (Ultra-Conservative)** | 7 orders | 42.86% | 3 | 4 | 91 orders (2.34%) | 42.86% | **+₹521.49** |

---

## 🎯 4. Section 10 Panel Pitch & Limitation Scoping

> **Anticipated Judge Question**: *"Why is your auto-block precision 37.25%? Doesn't that mean roughly 6 out of 10 auto-blocked orders are legitimate customers blocked outright?"*
> 
> **Recommended Answer**:  
> *"In COD risk management, precision cannot be viewed symmetrically like a standard classification benchmark. Because the orders our engine auto-blocks are low-ticket items (mean order value of ₹477.31), a false positive incurs a 15% margin loss of ₹71.60, whereas catching an RTO saves ₹250.00 in fixed forward and reverse logistics.
> 
> The break-even precision on this specific cohort is **22.26%**. At our measured **37.25% precision**, auto-blocking generates **+₹2,458.91 in net automated profit** on the held-out test split.
> 
> **Scoped Limitation Acknowledgment**: Our cost model explicitly captures gross margin loss (15%), but does not quantify intangible customer lifetime value (LTV) or brand churn from false blocks. This is precisely why we introduced the **Three-Way Router**: ambiguous orders scoring between 0.35 and 0.70 are never blocked outright; they are routed to the **manual review queue**, where fraud risk is concentrated to **47.17% (1.52x base rate)** for human verification."*
