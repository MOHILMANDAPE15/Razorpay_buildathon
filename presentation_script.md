# 🎤 Aegis-RTO — Live Hackathon Presentation Script (Solo Delivery)

> **Speaker Perspective:** First-person singular ("I built", "I designed", "I am showing you").  
> **Delivery Target:** Natural conversational speed, live UI walkthrough, and deep architectural clarity.  
> **Estimated Duration:** **~3m 50s to 4m 10s**  
> `[Square brackets]` indicate screen actions, clicks, and tab switches — do not read them aloud.

---

### ⏱️ [0:00 – 0:10] Track & Problem Statement
`[Start on Overview Tab — screen showing architecture canvas and header]`

*"For the **Razorpay AI Buildathon, Track 2 — AI Risk Manager**, the problem statement is to stop merchants from losing money to fraud and returns. 

To solve this, I built **Aegis-RTO**: an autonomous, closed-loop risk engine that detects fraud drift in real time, mines unflagged fraud patterns from mature delivery outcomes, and synthesizes transparent, self-evolving Python defense rules with **zero downtime**."*

---

### ⏱️ [0:10 – 1:15] Overview Tab: Real-Time Serving Path & Autonomous Sentinels (Node 1 to Node 5)
`[Point to Nodes 1 to 4 at the top of the Overview diagram]`

*"Here on the **Overview tab**, Aegis-RTO operates as a complete closed-loop system.*

*At checkout (**Node 1**), raw order signals are evaluated in **sub-10ms** with zero live LLM dependency against **Node 2: the Frozen Serving Ensemble** — a locked snapshot of validated Python AST rules.*

***Node 3** routes every order through a 3-way policy:
- **Auto-Approve:** 96% of genuine orders pass with zero customer friction.
- **Auto-Block:** High-confidence fraud (Risk $\ge 0.70$) is blocked instantly.
- **Manual Review:** Borderline cases ($0.35 \le \text{Risk} < 0.70$) are isolated for analysts with a concentrated **1.52x fraud density**.*

***Node 4** logs decisions, enforcing a **5-day maturation window** for true courier delivery confirmation.*

`[Scroll down slightly to Node 5: Autonomous Adaptation Triggers]`

*In the background (**Node 5**), three continuous sentinels monitor the system:
- **Residual Miner:** This is what discovers missed fraud. It continuously scans mature orders that slipped past our rules and resulted in RTO, clusters these false negatives into multi-dimensional attack signatures, verifies statistical significance ($p < 0.01$), and compiles structured **Defense Agendas**.
- **Spike Monitor:** Tracks live flag rates over a sliding 40-order window using Z-scores ($Z \ge 2.5\sigma$) to catch coordinated velocity bursts instantly with zero label lag.
- **Drift Detector:** Evaluates Population Stability Index (PSI $> 0.25$) to alert when buyer demographics or feature distributions drift from baseline."*

---

### ⏱️ [1:15 – 2:10] Architecture Deep Dive: Node 6 — Multi-Agent Evolution Loop (While-Loop & Gates)
`[Scroll to Node 6: Core Multi-Agent Evolution Loop on diagram]`

*"When a trigger fires, it launches **Node 6: the Core Multi-Agent Evolution Loop**.*

*This runs an autonomous pair-programming while-loop cycle:
1. 🧠 **Generator Agent:** Reads the defense agenda and writes candidate fraud defense rules as sandboxed Python AST boolean logic.
2. ⚙️ **Evaluator Agent:** Executes the candidate AST code in a secure sandbox over validation data, computing exact net INR savings ($+₹250$ per caught RTO vs. a heavy $-15\%$ gross margin penalty for false-alarm customer insults).
3. 🔄 **Reflector Agent:** If a candidate rule causes false positives or fails execution, the Reflector diagnoses the root cause and directly synthesizes a corrected mutated child rule via its own LLM call — which is then sent back to the Evaluator for re-scoring in the same round. Its failure diagnosis is also persisted to the Notepad for the next-round Generator.
4. ⚖️ **Selector & Pruner:** Uses greedy forward selection to pick complementary rules on the Pareto frontier and eliminate redundant bloat.*

*Before deployment, candidate rules must clear **3 Strict Gates**:
- **Gate 1 (Pre-Drift Regression):** Verifies no degradation on historical baseline data ($> -5\%$).
- **Gate 2 (Held-Out Verification):** Proves generalization above our **22.26% break-even hurdle**.
- **Decoy Guard:** Ensures zero illegal imports, AST safety, and zero reliance on noisy decoy features.*

*Once verified, the champion rule travels up the return loop and hot-swaps into **Node 2** atomically with zero downtime."*

---

### ⏱️ [2:10 – 3:20] Live System Walkthrough — Across the Tabs & Use Cases

`[Click 'Spike Monitor' Tab]`
*"Now let's walk through the live tabs of the platform.*

*On the **Spike Monitor** tab, merchants get real-time anomaly detection with zero label delay. 
- *[Click 'Stream Genuine Traffic']*: Streaming normal traffic maintains our 8% baseline flag rate.
- *[Click 'Trigger RTO Drift Burst']*: Injected surge attacks immediately spike sliding-window Z-scores above $2.5\sigma$, firing a **Critical Spike Alert** within seconds."*

`[Click 'Residual Mining' Tab]`
*"On the **Residual Mining** tab, you can inspect the actual unflagged false-negative clusters discovered by the engine, their Chi-Square significance scores, and the generated Defense Agendas."*

`[Click 'Knowledge Graph' Tab]`
*"On the **Knowledge Graph** tab, I provide complete auditability. You can trace the full evolutionary lineage tree — showing parent hypotheses, mutations, fitness scores, and the exact Python AST code behind every rule."*

`[Click 'Human Review' Tab]`
*"The **Human Review** tab is the analyst workstation. It isolates uncertain borderline cases with 1.52x fraud density, allowing fraud teams to resolve edge cases efficiently with full risk breakdowns."*

`[Click 'Playground' Tab → Click 'Generate Validation Case']`
*"On the **Playground** tab, anyone can test live checkouts. You can generate synthetic test cases to witness sub-10ms AST execution alongside instant Gemini causal explanations."*

---

### ⏱️ [3:20 – 4:00] Empirical Proof & The LightGBM Contrast
`[Click 'Ablation Matrix / Shadow Control' Tab]`

*"Finally, looking at empirical proof on **2,641 unseen held-out test orders**:
- **97.99% Auto-Decision Rate** with zero manual backlog.
- **37.25% Precision** — well above our **22.26% break-even hurdle**.
- **+₹2,458.91 Net Financial Profit**.*

*Why not LightGBM? Under concept drift, LightGBM suffered 113 false positives, resulting in a **net loss of -₹3,941.66**. Aegis-RTO delivered positive cash flow with fully auditable, transparent Python AST rules.*

*Static rules decay. ML models drift. Aegis-RTO adapts autonomously.*

*Thank you, and I am now ready for your questions!"*

---

## 📋 Quick Reference Card for Q&A

| Question / Topic | Verified Ground Truth to State |
|---|---|
| **Track & Scope** | **Razorpay AI Buildathon — Track 2: AI Risk Manager** (Defense-only autonomous risk engine for fraud, returns, and chargebacks) |
| **Residual Miner** | Clusters mature unflagged misses (`is_rto = 1`, `AUTO_APPROVE`), validates via $\chi^2$ ($p < 0.01$), outputs structured Defense Agendas |
| **Spike Monitor** | Zero-label-lag sliding 40-order window with binomial Z-score ($Z \ge 2.50\sigma$) & CUSUM change-point detection |
| **Drift Detector** | Tracks Population Stability Index (PSI $> 0.25$) on 14-day rolling cohorts against Day 0–55 baseline |
| **Node 6 While-Loop** | Generator (AST code) $\rightarrow$ Evaluator (net INR economics) $\rightarrow$ Reflector (error diagnosis) $\rightarrow$ Selector (pruning) $\rightarrow$ 3 Verification Gates |
| **Break-Even Precision Hurdle** | **22.26%** ($\frac{₹71.60}{₹250.00 + ₹71.60}$ where ₹71.60 is 15% margin on mean FP order value ₹477.31) |
| **Aegis vs LightGBM (Held-Out)** | Aegis: **+₹2,458.91** net profit (37.25% precision) vs. LightGBM: **-₹3,941.66** net loss (113 false positives) |
| **Held-Out Test Size** | **2,641 unseen orders** (Days 76–89), 97.99% auto-decided, 51 auto-blocked |
| **Inference SLA** | **<10ms vectorized AST execution**, zero live LLM in critical scoring path |
