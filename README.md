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

> **Follow a single order from checkout to decision — and see how the system learns and improves itself over time.**

### Step 1 — A Customer Places a COD Order

Imagine Rahul in Pune places a Cash-on-Delivery order for a ₹1,200 smartwatch at 2 AM using a new phone number, a freshly created account, and a pincode that has historically seen many returns.

The moment he hits **Place Order**, Aegis-RTO kicks in.

---

### Step 2 — The Frozen Serving Ensemble Scores It Instantly

Aegis reads 17 signals from that order — things like the hour of day, whether the account is new, the pincode's historical return rate, the device type, and the order value.

It then runs those signals through a locked set of **Python rules** that were validated before deployment. These rules are frozen — they don't call any AI model at runtime. The whole scoring happens in **under 10 milliseconds**.

Think of it like a trained security guard at the door who already knows the checklist by heart and doesn't need to call anyone for guidance.

---

### Step 3 — The 3-Way Router Makes a Decision

Based on the score, one of three things happens:

| Score | Action | What it means |
|---|---|---|
| Low risk | ✅ **Auto-Approve** | Order goes straight to fulfillment — no friction for the customer |
| High risk | 🚫 **Auto-Block** | High-confidence fraud, order is blocked automatically |
| Uncertain | 🟡 **Manual Review** | Sent to a human analyst for a quick judgment call |

In Rahul's case — 2 AM, new account, risky pincode — the system scores him medium-high and sends him to **Manual Review**.

---

### Step 4 — The Outcome Is Logged and Waits to Mature

Whatever decision was made gets logged. But Aegis does not immediately use that decision as training data.

Why? Because the courier still needs to physically deliver (or return) the package. Aegis waits **5 days** for the real outcome — was the order delivered or returned? — before using it as ground truth.

This prevents the system from learning from incomplete or misleading information.

---

### Step 5 — The Sentinels Watch for Changes in Fraud Patterns

While all of this is happening in real time, three background watchers are always running:

**📊 Spike Monitor** — If 50 orders suddenly pour in from the same pincode within one hour (far above normal), this raises an alert. It catches coordinated fraud surges early, even before any orders are actually returned.

**〰️ Drift Detector** — If the typical order values or geographic spread of orders starts shifting compared to last month, this fires. It means the nature of the incoming orders is changing — possibly because fraudsters have moved to a new city or tactic.

**🔍 Residual Miner** — After 5 days, this scans all orders that slipped through (the system approved them but they turned out to be fraudulent returns). It groups them by shared characteristics and looks for a pattern. For example: *"All the missed frauds came from Tier-3 cities, placed between midnight and 3 AM, with order values above ₹900."*

When any sentinel spots a real, statistically significant pattern, it writes a **Defense Agenda** — a plain brief describing the fraud behaviour — and passes it to the evolution engine.

---

### Step 6 — The Multi-Agent Loop Writes and Verifies a New Rule

This is where Aegis teaches itself. Four AI agents work in sequence:

**🧠 Generator** reads the Defense Agenda and writes a new Python rule. For example:

```python
# Block late-night high-value orders from brand-new accounts in high-RTO pincodes
order.hour >= 23 and order.account_age_days < 7 and order.pincode_rto_rate > 0.30 and order.item_value > 900
```

**⚙️ Evaluator** runs that rule safely in a sandboxed environment against historical orders and measures: how many real frauds does it catch vs. how many genuine customers does it wrongly block?

**🔄 Reflector** reviews those results. If the rule is catching fraud well but also blocking too many legitimate orders, it diagnoses why and tells the Generator to tighten the rule — for example, raise the value threshold from ₹900 to ₹1,100.

**⚖️ Selector** checks whether this new rule actually adds new value or just overlaps with something the system already catches.

---

### Step 7 — Three Safety Gates Before Anything Goes Live

Even if the new rule looks excellent in the lab, it must pass three independent checks before it can be deployed:

**Gate 1 — Regression Check:** The new rule is tested on 55 days of historical data. If it makes the overall system worse by more than 5%, it is rejected and sent back for revision. This protects existing performance.

**Gate 2 — Held-Out Validation:** The rule is run once — and only once — on a completely separate set of orders that were locked away from the very beginning. This is the final exam with no second chances. It proves the rule works on orders it has never seen.

**Gate 3 — Decoy Guard:** The rule is checked to make sure it is not accidentally using information that would only be available after the outcome (circular reasoning) or any fake test signals planted to catch cheating.

---

### Step 8 — The Champion Rule Goes Live. Instantly. No Downtime.

If the rule passes all three gates, it is promoted. The Frozen Serving Ensemble (Step 2) is updated atomically — like swapping one file for another — with the new rule now included.

The very next order that arrives is scored using the improved ruleset. No server restart. No redeployment. No data scientist needed.

Rahul's fraud pattern has been captured. Anyone who tries the same trick next time gets blocked automatically.

---

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
