# Three-Way Router Monotonicity & Score Interval Audit

> **Empirical Verification of Routing Condition Monotonicity and Score Bin Densities**  
> **Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager (Return-Risk Scorer & Adaptive Defense)**

---

## 📌 Executive Summary & Verdict

* **Is the routing condition monotonic in score?** **`YES`**.
* **Are there any order ID subset violations?** **`NO`** ($T_2 \subseteq T_1$ for all $T_2 > T_1$, 0 leaking orders).
* **Are $[0.75, 0.85]$ rows identical due to empty score bins?** **`YES`** (exactly 0 orders fall in $(0.75, 0.85)$ on the held-out test split).
* **Production Logic Integrity**: All production routing thresholds ($\text{Low} = 0.35$, $\text{High} = 0.70$) and cost-weighted acceptance gates remain unchanged.

---

## 🏛️ 1. Literal Membership Condition

From [`backend/app/engine/router.py`](file:///c:/Users/Dell/Razorpay_buildathon/backend/app/engine/router.py) (lines 143–157), decision assignment at threshold $T$ is defined as:

```python
if len(rules_matched) >= 2 or risk_score >= high_risk_threshold:
    decision = "AUTO_BLOCK"
    is_flagged = True
elif len(rules_matched) == 1 or risk_score >= low_risk_threshold:
    decision = "MANUAL_REVIEW"
    is_flagged = True
else:
    decision = "AUTO_APPROVE"
    is_flagged = False
```

---

## 🔬 2. Direct Monotonicity Subset Test (Held-Out Test Split, 2,641 Orders)

For every threshold transition $T_1 < T_2$, we empirically assert that the set of auto-blocked orders at $T_2$ is a **strict subset** of orders auto-blocked at $T_1$ ($\text{Blocked}_{T_2} \subseteq \text{Blocked}_{T_1}$):

| Threshold Transition ($T_1 \rightarrow T_2$) | Set Sizes ($|\text{Blocked}_{T_1}| \rightarrow |\text{Blocked}_{T_2}|$) | Subset Assertion (`T2 ⊆ T1`) | Violations ($T_2 \setminus T_1$) | Monotonicity Verdict |
|---|---|---|---|---|
| $T = 0.50 \rightarrow 0.55$ | $99 \rightarrow 99\text{ orders}$ | **`True`** | $\emptyset$ ($0\text{ orders}$) | ✅ Monotonic |
| $T = 0.55 \rightarrow 0.60$ | $99 \rightarrow 99\text{ orders}$ | **`True`** | $\emptyset$ ($0\text{ orders}$) | ✅ Monotonic |
| $T = 0.60 \rightarrow 0.65$ | $99 \rightarrow 99\text{ orders}$ | **`True`** | $\emptyset$ ($0\text{ orders}$) | ✅ Monotonic |
| **$T = 0.65 \rightarrow 0.70$** | **$99 \rightarrow 23\text{ orders}$** | **`True`** | $\emptyset$ ($0\text{ orders}$) | ✅ **Strict Monotonic Contraction** |
| **$T = 0.70 \rightarrow 0.75$** | **$23 \rightarrow 6\text{ orders}$** | **`True`** | $\emptyset$ ($0\text{ orders}$) | ✅ **Strict Monotonic Contraction** |
| $T = 0.75 \rightarrow 0.80$ | $6 \rightarrow 6\text{ orders}$ | **`True`** | $\emptyset$ ($0\text{ orders}$) | ✅ Monotonic |
| $T = 0.80 \rightarrow 0.85$ | $6 \rightarrow 6\text{ orders}$ | **`True`** | $\emptyset$ ($0\text{ orders}$) | ✅ Monotonic |
| $T = 0.85 \rightarrow 0.90$ | $6 \rightarrow 6\text{ orders}$ | **`True`** | $\emptyset$ ($0\text{ orders}$) | ✅ Monotonic |
| $T = 0.90 \rightarrow 0.95$ | $6 \rightarrow 6\text{ orders}$ | **`True`** | $\emptyset$ ($0\text{ orders}$) | ✅ Monotonic |

* **Direct Headline Check**: $\text{Blocked}_{T=0.70} \subseteq \text{Blocked}_{T=0.60} \implies \mathbf{True}$.
* Every single order auto-blocked at $0.70$ was also auto-blocked at $0.60$. No order enters auto-block when threshold is raised.

---

## 📐 3. Compound Condition Mechanics & Score Formulation

In [`router.py`](file:///c:/Users/Dell/Razorpay_buildathon/backend/app/engine/router.py), risk score is formulated as:
$$\text{risk\_score} = \text{ambient\_pincode\_risk} + (0.45 \times \text{rules\_matched})$$
where $\text{ambient\_pincode\_risk} = \text{pincode\_rolling\_rto\_rate} \times 0.8$ for COD orders ($\approx 0.10 \text{ to } 0.32$).

### Mathematical Behavior by Rule Match Tier:
1. **0 Rules Matched**:
   - $\text{risk} \in [0.05, 0.32] < 0.35$.
   - Fails both `AUTO_BLOCK` and `MANUAL_REVIEW` conditions $\implies$ **`AUTO_APPROVE`**.
2. **1 Rule Matched**:
   - $\text{risk} = \text{ambient} + 0.45 \in [0.55, 0.77]$.
   - If $T \le \text{risk}$ (e.g. $T = 0.60$): Matches `risk >= T` $\implies$ **`AUTO_BLOCK`**.
   - If $T > \text{risk}$ (e.g. $T = 0.70$): Fails `risk >= T`, but matches `len(rules_matched) == 1` $\implies$ cleanly shifts to **`MANUAL_REVIEW`**.
3. **2+ Rules Matched**:
   - $\text{risk} = \text{ambient} + 0.90 \ge 0.95$.
   - Matches both `len(rules_matched) >= 2` and `risk >= T` for all $T \le 0.95 \implies$ **`AUTO_BLOCK`**.

**Conclusion**: The compound condition is strictly monotonic with respect to $T$. Raising $T$ only re-routes single-rule borderline orders from `AUTO_BLOCK` into `MANUAL_REVIEW`.

---

## 📊 4. Exact Score Interval Distribution (Held-Out Test, 2,641 Orders)

| Score Interval | Order Count | Explanation & Operational Routing |
|---|---|---|
| **$[0.00, 0.35)$** | **2,542 orders** | Clean traffic (0 rules matched) $\rightarrow$ **Auto-Approve** |
| **$[0.35, 0.50)$** | **0 orders** | *Empty bin due to discrete +0.45 jump on first rule match.* |
| **$[0.50, 0.60)$** | **0 orders** | *Empty bin due to minimum ambient risk on COD orders.* |
| **$[0.60, 0.70)$** | **76 orders** | 1 rule matched in standard pincodes $\rightarrow$ Auto-Block at $T \le 0.65$, Review at $T \ge 0.70$. |
| **$[0.70, 0.75)$** | **17 orders** | 1 rule matched in elevated risk pincodes ($\ge 0.31$) $\rightarrow$ Auto-Block at $T \le 0.70$, Review at $T \ge 0.75$. |
| **$(0.75, 0.85)$** | **`0 orders`** | **Genuinely empty open interval.** |
| **$[0.85, 1.00]$** | **6 orders** | 2 rules matched ($\text{risk} \ge 0.95$) $\rightarrow$ High-confidence Auto-Block across all thresholds. |

### Explanation of Identical Rows ($T \in [0.75, 0.85]$):
Because the open interval $(0.75, 0.85)$ contains **strictly zero orders**, shifting $T$ from $0.75$ to $0.80$ to $0.85$ does not cross any order's score boundary. Therefore, the auto-blocked set remains identical (the 6 multi-rule orders with risk $\ge 0.95$).

---

## ❓ 5. Anticipated Panel FAQ

> **Judge**: *"Is your 3-way decision boundary strictly monotonic? What happens to borderline cases as the high-risk threshold increases?"*
> 
> **Answer**:  
> *"Yes, the router is strictly monotonic. Raising the high-risk threshold $T$ contracts the auto-blocked cohort strictly via $\text{Blocked}_{T_2} \subseteq \text{Blocked}_{T_1}$. 
> 
> When $T$ is increased from 0.60 to 0.70, single-match orders with composite risk in $[0.60, 0.70)$ are not approved or discarded—they are cleanly shifted into the **manual review queue** via the fallback tier (`len(rules_matched) == 1`). Multi-rule orders ($\ge 2$ matches, score $\ge 0.95$) remain firmly auto-blocked, ensuring extreme-risk transactions are never leaked."*
