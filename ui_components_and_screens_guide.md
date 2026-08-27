# Aegis-RTO: Complete UI Architecture & Component Inventory

> **Comprehensive Frontend Guide & Screen-by-Screen Component Catalog**  
> **Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager (Return-Risk Scorer & Adaptive Defense)**

---

## 🎨 1. Design System & Global Layout

The Aegis-RTO user interface is built with **Next.js 14 (App Router)**, **React**, **Tailwind CSS**, and **Lucide React Icons**, engineered to deliver an institutional-grade, fintech-ready command center with sub-second responsiveness.

* **Primary Palette**: Indigo (`#4F46E5`), Slate Neutral (`#0F172A`), Emerald Success (`#059669`), Rose Critical (`#E11D48`), Amber Review (`#D97706`), Sky Telemetry (`#0284C7`).
* **Typography**: Inter (System UI Font) with Monospace (`font-mono`) accents for IDs, financial amounts, and statistical metrics.
* **Layout Structure**: Fixed Left Sidebar (`Sidebar.tsx`), Sticky Top Navigation (`Header.tsx`), and a responsive Main Viewport with smooth entry transitions (`animate-fade-in`).

---

## 🧭 2. Global Navigation Components

### 2.1. Left Sidebar Navigation (`Sidebar.tsx`)
Located on every page (`frontend/src/components/Sidebar.tsx`), providing sticky access to all 5 core modules:
* **Brand Logo**: Gradient shield badge with live pulsating status indicator (`Aegis-RTO: Live COD Fraud Defense`).
* **Navigation Links**:
  1. **Overview** (`/`): System overview, headline savings, and architecture highlights.
  2. **Knowledge Graph** (`/lineage`): Multi-round hypothesis lineage DAG and parent-child mutation trees.
  3. **Ablation Matrix** (`/shadow-control`): Section 4.7 scientific proof isolating drift-adaptation from compute-scaling.
  4. **Spike Monitor** (`/monitor`): Real-time sliding-window Z-score and CUSUM telemetry stream.
  5. **Human Review** (`/review`): Section 6.2 honest 3-way triage queue with interactive approval actions.
* **Live Engine Footer**: Real-time heartbeat widget displaying `Engine Active: Autonomous · Self-Evolving`.

### 2.2. Top Sticky Header (`Header.tsx`)
Located at `frontend/src/components/Header.tsx`, providing:
* **Responsive Breadcrumb Navigation**: Fast-switching tabs with status badges (`5-Round DAG`, `Sec 4.7`, `Sec 6.2`).
* **System Health Badge**: Pulsating ping dot with `Engine: Live Active` indicator.

---

## 🖥️ 3. Screen-by-Screen Component Breakdown

---

### Screen 1: Mission Control Overview (`/` — `HomePage`)
**File**: [`frontend/src/app/page.tsx`](file:///c:/Users/Dell/Razorpay_buildathon/frontend/src/app/page.tsx)

```
+-----------------------------------------------------------------------------------+
|  [Track 2 Badge] Autonomous, Self-Evolving RTO & COD Fraud Defense                |
|  [CTA: Explore Knowledge Graph]   [CTA: Analyst Review Queue]                     |
|  Verified Stats: 2,641 Test Orders | +₹8,072.21 Savings | 47.17% Review Density  |
+-----------------------------------------------------------------------------------+
| [Knowledge Graph Card] | [Review Queue Card] | [Ablation Matrix] | [Spike Monitor] |
+-----------------------------------------------------------------------------------+
```

#### Interactive Elements & Components:
1. **Hero Banner Section**:
   - **Track 2 Pill**: Indigo badge highlighting *Track 2: Return-Risk Scorer & Adaptive Defense*.
   - **Headline & Narrative**: Clear explanation of closed-loop Python rule synthesis vs. static ML decay.
   - **Primary Action Buttons**: Deep-links with hover animations to `/lineage` and `/review`.
   - **Verified Metric Footer**: 4-column KPI strip showing **Test Dataset (2,641 Orders)**, **Net Savings (+₹8,072.21)**, **Review Queue Density (47.17% / 1.52x)**, and **Auto-Decision Rate (97.99%)**.
2. **Feature Module Navigation Grid**:
   - 4 hover-elevated cards (`hover:shadow-card-hover`, `group-hover:translate-x-1`) linking directly to the core workflows.

---

### Screen 2: Knowledge Graph & Hypothesis Lineage (`/lineage`)
**Files**: [`frontend/src/app/lineage/page.tsx`](file:///c:/Users/Dell/Razorpay_buildathon/frontend/src/app/lineage/page.tsx), [`LineageGraph.tsx`](file:///c:/Users/Dell/Razorpay_buildathon/frontend/src/components/LineageGraph.tsx), [`RuleInspectorDrawer.tsx`](file:///c:/Users/Dell/Razorpay_buildathon/frontend/src/components/RuleInspectorDrawer.tsx)

```
+-----------------------------------------------------------------------------------+
|  Knowledge Graph & Lineage   [Evolution Run Selector: run_01 ▼]   [Refresh DAG ⟳] |
+-----------------------------------------------------------------------------------+
|  [🏆 Champion Savings]   [Total Hypotheses]   [Mutation Links]   [Run Status]     |
|       +₹24,312.15             12 Nodes             8 Edges           COMPLETED    |
+-----------------------------------------------------------------------------------+
|  DAG CANVAS:  [Filter: All | Champion | Alive | Pruned]   [Zoom: − 100% + Reset]   |
|   Round 1               Round 2               Round 3               Round 4       |
|  [Node Card 1] -----> [Node Card 3] =======> [🏆 Champion]                        |
|  [Node Card 2] (Pruned) -------------------> [Node Card 4]                        |
+-----------------------------------------------------------------------------------+
|  SLIDE-OUT DRAWER: [Python Code Block] | [P/R/ROI Scorecard] | [Parent Lineage]   |
+-----------------------------------------------------------------------------------+
```

#### Interactive Elements & Components:
1. **Evolution Run Selector Bar**:
   - Dropdown menu dynamically querying backend PostgreSQL runs (`fetchEvolutionRuns`).
   - Animated refresh button (`RefreshCw`) for re-fetching live DAG state.
2. **Summary KPI Strip**:
   - **Champion Savings Card**: Shows best net Rupee savings found in the run.
   - **Total Hypotheses Card**: Count of synthesized rules across all rounds.
   - **Mutation Links Card**: Count of Reflector diagnostic parent-to-child edges.
   - **Run Status Card**: Status pill (`COMPLETED` / `RUNNING`) with active Champion ID.
3. **Interactive Lineage DAG Canvas (`LineageGraph.tsx`)**:
   - **Stage Column Headers**: Multi-round vertical columns (`Round 1` to `Round 5`).
   - **Dynamic SVG Bezier Edges**: Smooth cubic bezier curves connecting parent rules to mutated child rules.
   - **Active Lineage Highlighting**: Hovering over any rule highlights its complete ancestry tree in emerald green (`strokeWidth=3`, active arrowhead markers, and mutation strategy tags like `🧬 refine_thresholds`).
   - **Status-Colored Node Cards**:
     - 🏆 **Champion Node**: Emerald border, trophy badge, financial profit metrics.
     - 🧬 **Mutated Child Node**: Indigo border, sparkle badge, parent reference.
     - ❌ **Pruned Node**: Rose border, strikethrough styling, regression failure reason.
   - **Toolbar Controls**: Filter pills (`All`, `Champion`, `Alive`, `Pruned`) and canvas Zoom buttons (`70%` to `130%`).
4. **Slide-Out Rule Inspector Drawer (`RuleInspectorDrawer.tsx`)**:
   - Slides smoothly from the right when clicking any node.
   - **Performance Scorecard**: Net Savings (₹), Precision (%), Recall (%).
   - **Hypothesis Rationale**: Human-readable explanation of why the rule was generated and what fraud pattern it targets.
   - **Vectorized Python Code Block**: Full executable Python rule inside a dark syntax container with a **1-click Copy Code** button.
   - **Lineage Connection Buttons**: Clickable parent pills allowing users to jump directly to ancestor hypotheses.

---

### Screen 3: Human Review & Honest 3-Way Triage (`/review`)
**File**: [`frontend/src/app/review/page.tsx`](file:///c:/Users/Dell/Razorpay_buildathon/frontend/src/app/review/page.tsx)

```
+-----------------------------------------------------------------------------------+
|  Human Review & Honest Metrics  [Held-Out Test (2,641) | Validation]  [Refresh ⟳] |
+-----------------------------------------------------------------------------------+
|  [1. Auto-Decided Cohort]  |  [2. Review Queue Cohort]  |  [3. Full System Total] |
|   - 97.99% of traffic       |   - 2.01% of traffic        |   - 100% of volume      |
|   - Auto-Approved: 2,537    |   - Queue Volume: 53 orders |   - 0% Cherry-Picking   |
|   - Auto-Blocked: 51        |   - RTO Conc.: 47.17% (1.52x|   - Net: +₹2,458.91     |
|   - Net: +₹2,458.91         |   - Triaged Val: ₹22,783    |                         |
+-----------------------------------------------------------------------------------+
|  ACTIVE TRIAGE QUEUE (53 Orders):                                                 |
|  Order ID | Risk Score | Value | Triggered Signals       | Status | Action        |
|  ORD_9482 |   68.2%    |  ₹450 | Late night + new acct   | PENDING| [✓ Appr] [✗]  |
|  ORD_8291 |   54.1%    |  ₹620 | Promo burst device >=2  | PENDING| [✓ Appr] [✗]  |
+-----------------------------------------------------------------------------------+
```

#### Interactive Elements & Components:
1. **Cohort Selector Bar**:
   - Toggle button between **Held-Out Test Benchmark (2,641 Orders)** and **Validation Cohort**.
2. **Methodological Notice Banner**:
   - Institutional callout verifying Section 6.2 compliance: marginal orders are routed to review rather than dropped to inflate precision.
3. **Three-Way Accounting Split Cards**:
   - **Auto-Decided Card**: Displays auto-approved count, auto-blocked count, auto precision, and automated net savings.
   - **Review Queue Card**: Displays review volume (2.01%), RTO concentration (47.17% vs 31.01% base rate $\rightarrow$ **1.52x multiplier**), and total protected rupee value (₹22,783.20).
   - **Full System Card**: Total 100% accounting showing zero leakage.
4. **Interactive Analyst Triage Table**:
   - **Order Metadata**: Order ID, Risk Score pill, Order Value (₹), and Triggered Rule Explanation.
   - **Live Adjudication Buttons**:
     - `[✓]` **Approve Order (Dispatch)**: Instantly marks order as `APPROVED` and records analyst note via `/api/v1/review/decision`.
     - `[✗]` **Reject Order (Block Fraud)**: Instantly marks order as `REJECTED` and prevents RTO loss.

---

### Screen 4: Rounds-Matched Ablation Matrix (`/shadow-control`)
**File**: [`frontend/src/app/shadow-control/page.tsx`](file:///c:/Users/Dell/Razorpay_buildathon/frontend/src/app/shadow-control/page.tsx)

```
+-----------------------------------------------------------------------------------+
|  Rounds-Matched Ablation Matrix [Section 4.7 Scientific Proof]                    |
|  Proving that static rule decay is driven by distribution drift, not compute.     |
+-----------------------------------------------------------------------------------+
| [1. Static Frozen v1]     | [2. Shadow Control]         | [3. Drift-Adapted]      |
|  - 3 Rounds (Pre-drift)   |  - 5 Rounds (Pre-drift only)|  - 5 Rounds (Drift-aware|
|  - Train: ₹24,312         |  - Train: ₹34,441 (+₹10k)   |  - Train: ₹35,428       |
|  - Val:   ₹6,567 (-73.0%) |  - Val:   ₹13,273 (-61.5%)  |  - Val:   ₹22,734 (+246%)
|  - Collapse under drift   |  - Extra compute still falls|  - Autonomous recovery  |
+-----------------------------------------------------------------------------------+
```

#### Interactive Elements & Components:
1. **Scientific Proof Banner**:
   - Explanation of Section 4.7's isolation of feedback-guided adaptation vs pre-drift compute scaling.
2. **Three-Way Comparison Cards**:
   - **Frozen v1 Card**: Illustrates the -73.0% collapse of static rules under concept drift.
   - **Shadow Control Card**: Proves that adding 2 extra compute rounds on historical data only (+₹34k on train) still suffers a -61.5% drop on drifted traffic.
   - **Drift-Adapted Evolved Card**: Shows autonomous recovery (+246.2% lift to ₹22,734.77 net savings, recall quadrupled to 21.20%).

---

### Screen 5: Real-Time Spike Monitor & Telemetry (`/monitor`)
**File**: [`frontend/src/app/monitor/page.tsx`](file:///c:/Users/Dell/Razorpay_buildathon/frontend/src/app/monitor/page.tsx)

```
+-----------------------------------------------------------------------------------+
|  Real-Time Spike Monitor  [● Live Telemetry]  [Auto-Polling (3s) ⟳]  [Refresh]    |
+-----------------------------------------------------------------------------------+
|  [Stream Health]    |  [Rolling Flag Rate]  |  [Drift Z-Score]   | [CUSUM Meter]  |
|    HEALTHY / CRIT   |   8.4% (vs 8.0% base) |     0.32σ / 2.50σ  |  0.012 / 0.150 |
+-----------------------------------------------------------------------------------+
|  ROLLING FLAG RATE TRAJECTORY (SVG Chart):                                        |
|  |             - - - - - - - - - - - - - - - - - - - (2.5σ Threshold Bound)       |
|  |  |||||||||||||||||||||||||||||||||||||||||||||||                               |
|  +-------------------------------------------------- (8.0% Baseline Reference)   |
+-----------------------------------------------------------------------------------+
|  TRAFFIC SIMULATION TRIGGERS:           |  ACTIVE ANOMALY ALERTS (Real-Time):     |
|  [✓ Stream Genuine Traffic (8% flags)]  |  [⚠️ CRITICAL_SPIKE: Z=2.85σ detected]  |
|  [⚡ Trigger RTO Drift Burst (55% flags)] |  - Recommended: Trigger evolution loop  |
+-----------------------------------------------------------------------------------+
```

#### Interactive Elements & Components:
1. **Live Polling Toolbar**:
   - **Auto-Polling Toggle**: Toggles automated background polling every 3 seconds (`fetchMonitorStatus`, `fetchMonitorHistory`).
   - **Live Pulsating Ping Badge**: Visual confirmation of real-time stream connectivity.
2. **Primary Telemetry KPI Grid**:
   - **Stream Health Card**: Dynamic state (`HEALTHY` in emerald, `WARNING` in amber, `CRITICAL` in rose).
   - **Rolling Flag Rate Card**: Sliding 50-order window flag percentage vs. 8.0% baseline.
   - **Drift Z-Score Card**: Binomial Z-score with animated fill gauge (critical at $\ge 2.50\sigma$).
   - **CUSUM Anomaly Meter**: Cumulative sum change-point score with progress bar.
3. **Custom SVG Telemetry Chart**:
   - Real-time time-series bar chart rendering the last 40 scoring steps.
   - Color-coded bars (blue for normal, amber for elevated, red for critical spikes).
   - **Dashed Reference Lines**: Green dashed line for 8.0% baseline; Red dashed line for 2.5$\sigma$ critical threshold.
   - **Interactive Hover Tooltips**: Displays exact Step #, Flag Rate (%), and Z-Score ($\sigma$) on mouseover.
4. **Interactive Traffic Simulation Triggers**:
   - **Stream Genuine Traffic**: Injects 25 normal orders (~8% flag rate), keeping Z-score $< 1.0\sigma$ and health `HEALTHY`.
   - **Trigger RTO Drift Burst**: Injects 30 attack orders (~55% flag rate), breaching the 2.5$\sigma$ threshold, turning chart bars red, and firing real-time `CRITICAL_SPIKE` alerts.
5. **Real-Time Anomaly Alert Stream**:
   - Displays real-time alert cards with timestamp, severity level, diagnostic description, and automated mitigation recommendations.

---

## 📑 4. UI Component File Inventory Table

| Component Name | File Path | Type | Key Features & Responsibilities |
|---|---|---|---|
| **`Sidebar`** | `src/components/Sidebar.tsx` | Layout | Navigation menu, brand badge, active route highlights, live engine status widget. |
| **`Header`** | `src/components/Header.tsx` | Layout | Sticky navbar, section badges (`5-Round DAG`, `Sec 4.7`, `Sec 6.2`), responsive mobile layout. |
| **`HomePage`** | `src/app/page.tsx` | Page Route | Mission control hero, headline savings stats, 4-card feature module launcher. |
| **`LineagePage`** | `src/app/lineage/page.tsx` | Page Route | Knowledge graph manager, evolution run selector, summary KPIs, DAG integration. |
| **`LineageGraph`** | `src/components/LineageGraph.tsx` | Component | Custom SVG DAG canvas, cubic bezier edges, ancestry highlighting, zoom/filter controls. |
| **`RuleInspectorDrawer`** | `src/components/RuleInspectorDrawer.tsx` | Component | Slide-out node drawer, Python code viewer, 1-click copy, financial scorecard, parent navigation. |
| **`ReviewQueuePage`** | `src/app/review/page.tsx` | Page Route | Section 6.2 3-way split cards, cohort switcher, interactive analyst triage table with live POST actions. |
| **`ShadowControlPage`** | `src/app/shadow-control/page.tsx` | Page Route | Section 4.7 3-way ablation cards, train vs validation degradation deltas, scientific proof callouts. |
| **`SpikeMonitorPage`** | `src/app/monitor/page.tsx` | Page Route | Live telemetry KPIs, custom SVG time-series chart, genuine vs burst traffic simulators, alert feed. |
| **`api.ts`** | `src/lib/api.ts` | Service | TypeScript interfaces and fetch client methods connecting to FastAPI backend (Port 8080). |
| **`globals.css`** | `src/app/globals.css` | Styling | Custom scrollbars, glow effects, animation keyframes (`fade-in`, `slide-in`). |

---

## 🚀 5. How to Run and Experience the UI

```bash
# 1. Start the Backend API (FastAPI on Port 8080)
cd c:\Users\Dell\Razorpay_buildathon
$env:PYTHONPATH="backend"; .venv\Scripts\python.exe -m uvicorn app.api.main:app --port 8080 --host 127.0.0.1

# 2. Start the Frontend Application (Next.js on Port 3300)
cd c:\Users\Dell\Razorpay_buildathon\frontend
npm start -- -p 3300 -H 127.0.0.1
```

*Open your browser at **`http://127.0.0.1:3300`** to navigate the entire interface.*
