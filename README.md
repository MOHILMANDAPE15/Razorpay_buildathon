# 🛡️ Aegis-RTO: Autonomous Self-Evolving Fraud Defense Engine

> **Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager (Return-Risk Scorer & Adaptive Defense)**
> 
> *A production-grade, self-evolving risk engine that autonomously discovers, validates, and refines executable Python fraud defense rules to protect Indian e-commerce merchants from Return-to-Origin (RTO) and Cash-on-Delivery (COD) fraud.*

[![Tests](https://img.shields.io/badge/Tests-65%2F65%20Passing-emerald?style=for-the-badge&logo=pytest)](file:///c:/Users/Dell/Razorpay_buildathon/backend/tests)
[![Track](https://img.shields.io/badge/Track%202-AI%20Risk%20Manager-indigo?style=for-the-badge)](https://razorpay.com/buildathon)
[![Policy](https://img.shields.io/badge/Policy-100%25%20Defense--Only-blue?style=for-the-badge)](file:///c:/Users/Dell/Razorpay_buildathon/backend/app/engine/defense_audit.py)
[![Inference](https://img.shields.io/badge/Inference-%3C10ms%20Vectorized-purple?style=for-the-badge)](file:///c:/Users/Dell/Razorpay_buildathon/backend/app/core/sandbox.py)
[![Deploy](https://img.shields.io/badge/Deploy-Vercel%20%2B%20Docker-black?style=for-the-badge&logo=vercel)](https://vercel.com)

---

## 📌 Executive Summary (The Problem in Simple Terms)

In Indian e-commerce, **Cash-on-Delivery (COD)** accounts for over **60% of all checkouts**, with **Return-to-Origin (RTO)** rates frequently reaching **25%–35%**. 

Every failed delivery costs merchants **₹150 to ₹350 in forward shipping, reverse courier fees, repackaging, and inventory lockup**.

### Why Traditional Systems Fail:
1. **Fraud Tactics Change Constantly (Concept Drift)**: Static rules and machine learning models trained on past data decay rapidly as fraudsters switch to new tactics (e.g., promo-code stacking, virtual device pools, high-velocity midnight ordering).
2. **The "Customer Insult" Trap**: Blocking a genuine customer's ₹1,500 order costs the merchant **₹225 in gross profit margin (15%)** and destroys customer trust. Symmetric models that aggressively optimize for recall trigger excessive false alarms, driving net business profit negative.
3. **Black-Box Retraining Delays**: Retraining traditional ML models (XGBoost/LightGBM) requires data scientists, manual labeling lag (5–7 days), and days of downtime.

### How Aegis-RTO Solves This:
Aegis-RTO is an **autonomous, closed-loop risk engine**. When fraud tactics shift, Aegis detects the change, diagnoses why previous rules failed, autonomously synthesizes new transparent Python rules, verifies them across rigorous cost gates, and promotes champions into production with **zero downtime**.

---

## 🏛️ How Aegis-RTO Works (The Closed Loop)

```
   ┌─────────────┐       stream       ┌──────────────────┐       score        ┌──────────────────┐
   │ 1. New      │ ─────────────────> │ 2. Frozen Serving│ ─────────────────> │ 3. 3-Way         │
   │    Order    │                    │    Ensemble      │                    │    Router        │
   └─────────────┘                    └──────────────────┘                    └────────┬─────────┘
                                                ▲                                      │
                                                │ (if promoted: atomic snapshot update)│ action
                                                │                                      ▼
   ┌─────────────┐       agenda       ┌─────────┴────────┐      mature        ┌──────────────────┐
   │ 6. Multi-   │ <───────────────── │ 5. Autonomous    │ <───────────────── │ 4. Outcomes      │
   │    Agent    │                    │    Triggers      │                    │    Logged        │
   │    Evolution│                    │ (Spike/Drift/    │                    │ (5-Day Maturation│
   │    Loop     │                    │  Residual Miner) │                    │  Ground Truth)   │
   └─────────────┘                    └──────────────────┘                    └──────────────────┘
```

---


## 🚀 How It All Works — A Plain-English Walkthrough

> **Follow a single order through every module — and see how the system autonomously learns and rewrites its own defense rules.**

---

### Step 1 — A Customer Places a COD Order

A customer places a Cash-on-Delivery order for a ₹1,200 smartwatch at 2 AM — new phone number, freshly created account, high-RTO pincode. The moment the order is submitted, Aegis-RTO kicks in.

---

### Step 2 — The Frozen Serving Ensemble Scores It in Real Time

Aegis extracts **17 order signals** — account age, order hour, pincode RTO rate, device type, item value, and more — and runs them through a **locked set of Python AST rules** that are already deployed in production. No live AI model is called at this point. The entire scoring completes in **under 10 milliseconds**.

The ruleset is called "frozen" because it is an immutable snapshot. It only gets updated when a new champion rule successfully passes all safety gates (Step 7). This separation keeps inference fast and predictable.

---

### Step 3 — The 3-Way Router Makes a Decision

Every order gets routed to exactly one of three buckets:

| Bucket | Action | What it means |
|---|---|---|
| Low risk | ✅ **Auto-Approve** | Order goes straight to fulfillment — no customer friction |
| High risk | 🚫 **Auto-Block** | High-confidence fraud caught by the serving ensemble |
| Uncertain | 🟡 **Manual Review** | Queued for a human analyst — fraud density here is 1.52x concentrated |

The 2 AM new-account order above lands in Manual Review.

---

### Step 4 — The Outcome Is Logged and Waits to Mature

The decision is written to the database immediately. But Aegis does not use it as training signal yet — it waits a **5-day maturation window** for the courier to physically deliver or return the parcel. Only verified ground truth (actual RTO or delivery confirmation) enters the learning pipeline. This prevents the system from training on in-flight, unresolved orders.

---

### Step 5 — Three Sentinels Watch for Emerging Fraud Patterns

Three background monitors run continuously against the maturing outcome stream:

**📊 Spike Monitor** — Uses a sliding **binomial Z-score** to detect sudden, statistically abnormal surges in RTO rate at a pincode or account cohort level. It fires before any matured labels are even needed, catching coordinated fraud waves in near real time.

**〰️ Drift Detector** — Monitors the **Population Stability Index (PSI)** of incoming order features (value distribution, pincode spread, device mix). A significant PSI shift means the population of orders has changed — often because fraudsters have shifted tactics or geography — and the existing rules may no longer be aligned.

**🔍 Residual Miner** — After maturation, it scans all false negatives (orders the system approved that turned out to be fraudulent returns) and performs **statistical subgroup discovery** across behavioral feature dimensions. It isolates dense cohorts of unflagged fraud patterns without multiple-testing noise. Each cluster that passes a **Chi-Square significance test ($p < 0.05$)** and a **3-round cooldown guard** (to avoid proposing the same fix repeatedly) generates a **Defense Agenda** — a structured brief describing the shared feature profile of the cluster — which is handed to the evolution engine.

---

### Step 6 — The Multi-Agent Loop Writes, Evaluates, Reflects, and Prunes a New Rule

Four AI agents work in sequence:

**🧠 Generator** reads the Defense Agenda and synthesises a new candidate **Python AST boolean rule** — a transparent, human-readable condition like `order.hour >= 23 and order.account_age_days < 7 and order.pincode_rto_rate > 0.30`. The rule is expressed as an Abstract Syntax Tree so it can be statically validated before execution — no `eval()`, no arbitrary code.

**⚙️ Evaluator** executes the rule in an **isolated sandbox** (no database writes, no network calls, CPU time-limited) against the full historical dataset and computes: how many actual frauds does this catch, how many genuine orders does it wrongly flag, and what is the net INR savings after accounting for the cost of false positives?

**🔄 Reflector** reviews the Evaluator's output and performs **causal diagnosis** — if the rule has too many false positives, it identifies which feature boundary is responsible and feeds targeted correction instructions back to the Generator for the next iteration.

**⚖️ Selector & Pruner** applies **greedy forward selection** to decide whether the new rule earns a place in the ensemble. It checks for **collinearity** — if the new rule fires on almost the same orders as an existing rule, it adds no marginal value and is pruned. Only rules that improve the **Pareto frontier** of precision vs. recall vs. net savings get added to the candidate ensemble.

---

### Step 7 — Three Safety Gates Before Anything Goes Live

**Gate 1 — Pre-Drift Regression:** The candidate ensemble is tested on the original 55-day training split. If overall performance regresses by more than 5% compared to the baseline, the rule is rejected and sent back for revision.

**Gate 2 — Held-Out Validation:** The ensemble is evaluated exactly once on a physically isolated held-out split (Days 56–75) that was never touched during training or rule development. This single-touch constraint prevents data snooping and cherry-picking.

**Gate 3 — Decoy Guard & AST Audit:** The rule's AST is scanned for references to any decoy or circular features (signals that are only knowable after the outcome), and a honeypot perturbation test is applied. Any rule that reacts to planted nonsense signals is rejected immediately.

---

### Step 8 — The Champion Rule Goes Live. Zero Downtime.

If all three gates pass, the new rule is promoted. The Frozen Serving Ensemble is updated **atomically** — the serving snapshot is swapped in a single operation with no server restart and no redeployment. The next incoming order is instantly scored against the improved ruleset.

The fraud pattern from Step 1 is now encoded. Anyone attempting the same behaviour is caught automatically.


## 💰 The Financial ROI Equation

Aegis-RTO optimizes for **Merchant Net Profit**, not vanity metric accuracy:

$$\text{Net Value} = (\text{True Positives} \times ₹250\text{ Shipping Loss Avoided}) - \sum (\text{False Positive Order Value} \times 15\%\text{ Profit Margin Lost})$$

### The 22.26% Break-Even Precision Hurdle:
At an average order value (AOV) of ₹1,123.36:
* Saving 1 RTO prevents: $+₹250$
* Insulting 1 genuine customer loses: $₹1,123.36 \times 15\% = -₹168.50$
* **Minimum viable precision required**:
  $$\text{Break-Even Precision} = \frac{₹168.50}{₹250 + ₹168.50} = 22.26\%$$

Any fraud system operating below 22.26% precision destroys merchant wealth. Aegis-RTO operates at **37.25%–42.86% precision**, ensuring every automated decision delivers positive net cash flow.

---

## 📊 Empirical Results & Verification

### 1. Final Held-Out Test Set Proof (2,641 Unseen Orders, Days 76–89)

| Metric | Result | Operational Meaning |
|---|---|---|
| **Total Test Dataset** | **2,641 Orders** | 100% unseen post-drift chronological split |
| **Auto-Decision Rate** | **2,588 Orders (97.99%)** | Processed sub-millisecond without human labor |
| **Auto-Approved Orders** | **2,537 Orders** | Clean orders passed to fulfillment |
| **Auto-Blocked Orders** | **51 Orders** | High-confidence fraud intercepts |
| **Auto-Decided Precision** | **37.25%** | Far above the 22.26% break-even hurdle |
| **Manual Review Volume** | **53 Orders (2.01%)** | Ambiguous cases isolated for analysts |
| **Review Queue Risk Concentration** | **47.17% (1.52x)** | Concentrates fraud 1.52x for rapid human review |
| **Auto Net Financial Savings** | **+₹2,458.91** | Net profit after all customer insult costs deducted |

---

## 🛡️ Data Integrity & Security Safeguards

1. **Physical Table Segregation**: `orders_train` (Days 0–55), `orders_validation` (Days 56–75), and `orders_held_out_test` (Days 76–89) reside in physically isolated database tables.
2. **Sandboxed AST Execution**: All candidate rules execute in a restricted Python Abstract Syntax Tree (AST) runtime with CPU timeouts, blocking `eval()`, `exec()`, `import`, and disk access.
3. **Locked Single-Touch Test Split**: The 2,641 held-out test orders are evaluated strictly once at final Gate 2 verification.
4. **Decoy Features Audit**: Candidate rules referencing circular non-causal features (e.g. `device_model_name`, `app_theme_color`) are rejected automatically.

---

## 🚀 Local Recreation Guide (Step-by-Step)

### Option A: Local Run with Python + Node.js

#### 1. Clone & Setup Backend
```bash
# 1. Clone the repository
git clone https://github.com/MOHILMANDAPE15/Razorpay_buildathon.git
cd Razorpay_buildathon

# 2. Create and activate Python virtual environment
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# 3. Install backend dependencies
pip install -r backend/requirements.txt

# 4. Copy environment configuration
cp .env.example .env
# (Optional: Add your GROQ_API_KEY or GEMINI_API_KEY in .env for live LLM rule generation)

# 5. Ingest datasets into SQLite database
python -m app.db.ingest

# 6. Start FastAPI Backend (Port 8080)
python -m uvicorn app.api.main:app --port 8080 --host 127.0.0.1
```

#### 2. Setup & Start Frontend Dashboard
```bash
# Open a new terminal:
cd Razorpay_buildathon/frontend

# 1. Install Node.js dependencies
npm install

# 2. Start Next.js Development Server (Port 3300)
npm run dev -- -p 3300 -H 127.0.0.1
```

Visit the dashboard in your browser at: **`http://localhost:3300`**

---

### Option B: 1-Command Run with Docker Compose

```bash
# Clone the repository
git clone https://github.com/MOHILMANDAPE15/Razorpay_buildathon.git
cd Razorpay_buildathon

# Build and run both backend and frontend
docker compose up --build
```

The system will start automatically:
* **Frontend Dashboard**: `http://localhost:3300`
* **FastAPI Backend**: `http://localhost:8080`
* **API Documentation**: `http://localhost:8080/docs`

---

## ☁️ Deploying to Vercel (Production Setup)

Aegis-RTO is structured for seamless deployment with the Next.js frontend on Vercel and the FastAPI backend on any cloud provider (Render, Railway, Fly.io, or AWS).

### Step 1: Deploy Backend (e.g. Render / Railway)
1. Deploy `backend/` as a Python web service (or use the provided `backend/Dockerfile`).
2. Set the start command: `python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8080`.
3. Add environment variables: `GROQ_API_KEY` (or `GEMINI_API_KEY`).
4. Note your backend URL (e.g., `https://aegis-rto-api.onrender.com`).

### Step 2: Deploy Frontend on Vercel
1. Import the repository into [Vercel](https://vercel.com).
2. Set the **Root Directory** to `frontend`.
3. Framework Preset: **Next.js**.
4. In **Environment Variables**, add:
   * `NEXT_PUBLIC_API_URL` = `https://aegis-rto-api.onrender.com/api/v1`
   * `BACKEND_URL` = `https://aegis-rto-api.onrender.com`
5. Click **Deploy**. Vercel will build and launch the production dashboard.

---

## 🧪 Judge Automated Verification Checklist

You can verify the entire test suite and scientific scripts in seconds:

```bash
# 1. Run all 65 unit and integration tests (100% pass rate)
python -m pytest backend/tests/ -v

# 2. Run the live Evolution Engine demo
python backend/scratch/run_evolution_demo.py

# 3. Run the live Residual Miner execution demo
python backend/scratch/run_residual_miner_demo.py

# 4. Verify paired bootstrap significance & shadow control
python backend/scratch/run_shadow_control.py
```

---

## 📁 Repository Structure

```
├── backend/
│   ├── app/
│   │   ├── agents/          # Generator, Evaluator, Reflector, Selector agents
│   │   ├── api/             # FastAPI endpoints (scoring, lineage, monitor, review)
│   │   ├── core/            # AST sandbox runtime, LLM client factory, config
│   │   ├── data/            # Data loaders with single-touch split guards
│   │   ├── db/              # SQLAlchemy ORM models, session, CSV ingestion
│   │   └── engine/          # Router, Evaluator, Spike Monitor, Residual Miner
│   ├── Dockerfile           # Backend containerization
│   ├── requirements.txt     # Python dependencies
│   └── tests/               # 65 automated tests (100% pass rate)
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js pages: Overview, Knowledge Graph, Mining, Monitor, etc.
│   │   ├── components/      # ArchitectureDiagram, InfoTooltip, ChatWidget, Drawers
│   │   └── lib/             # Typed API client & centralized glossary
│   ├── Dockerfile           # Frontend containerization
│   ├── package.json         # Node.js dependencies
│   └── vercel.json          # Vercel deployment configuration
├── idea_and_data/
│   ├── train.csv            # Days 0–55 (10,807 orders, baseline pre-drift)
│   ├── validation.csv       # Days 56–75 (3,885 orders, drift ramp-in)
│   ├── held_out_test.csv    # Days 76–89 (2,641 orders, frozen test split)
│   └── data_card.md         # Full dataset documentation
├── docker-compose.yml       # 1-command fullstack local reproduction
├── .env.example             # Environment variables template
└── README.md                # Comprehensive documentation
```

---

## ❓ Frequently Asked Questions (FAQ)

#### Q1: "Why does Aegis auto-block 51 orders instead of hundreds?"
> **Answer**: In fraud risk management, an aggressive model flagging 500 orders will inevitably trigger hundreds of false positives. At ₹1,123 AOV, each false alarm destroys ₹168 in merchant margin. Aegis auto-blocks only high-confidence fraud ($T \ge 0.70$), while isolating ambiguous cases ($0.35 \le T < 0.70$) into the Analyst Review Queue where fraud density is concentrated by **1.52x**.

#### Q2: "How does the system prevent arbitrary code execution from generated rules?"
> **Answer**: Candidate rules execute inside [`sandbox.py`](file:///c:/Users/Dell/Razorpay_buildathon/backend/app/core/sandbox.py) using static Abstract Syntax Tree (AST) validation. The sandbox parses rule syntax before execution, blocking all `import`, `open`, `eval`, `exec`, `__subclasses__`, and OS operations.

#### Q3: "What prevents the Residual Miner from repeatedly proposing rejected rules?"
> **Answer**: Aegis enforces a **3-Round Cluster Cooldown**. When a candidate rule for a false-negative cluster is rejected by the cost gate or pruned, its cluster ID enters cooldown in the database. During cooldown, the cluster is suppressed unless miss volume surges by $>50\%$.

---

## 👥 Author & Contact

* **Author**: Mohil Mandape
* **GitHub**: [@MOHILMANDAPE15](https://github.com/MOHILMANDAPE15)
* **Email**: mohilmandpe33@gmail.com
* **Track**: Razorpay AI Buildathon 2026 — Track 2 (Return-Risk Scorer / AI Risk Manager)