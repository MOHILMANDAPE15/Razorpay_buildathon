# Aegis-RTO: Self-Evolving RTO & COD Fraud Detection Engine

> **Razorpay Buildathon — Track 2 (Return-Risk Scorer / Adaptive Defense)**

An autonomous, self-evolving fraud defense system that discovers, validates, and refines executable fraud detection rules in response to shifting adversarial patterns and Return-to-Origin (RTO) / Cash-on-Delivery (COD) abuse.

---

## 🚀 Key Highlights & Architectural Overview

Traditional machine learning classifiers decay when fraudsters adapt their tactics (e.g., transitioning from simple first-time COD abuse to distributed promo-code stacking and device-pool cycling). **Aegis-RTO** closes this loop through an offline evolutionary discovery engine coupled with online, sub-millisecond sandboxed rule execution.

```
                    ┌──────────────────────────────────────────────┐
                    │               OFFLINE EVOLUTION               │
                    │                                              │
                    │   ┌─────────────┐       ┌───────────────┐    │
                    │   │  Generator  │ ───>  │   Evaluator   │    │
                    │   │   (LLM)     │       │(Cost-Weighted)│    │
                    │   └─────────────┘       └───────┬───────┘    │
                    │          ▲                      │            │
                    │          │                      ▼            │
                    │   ┌─────────────┐       ┌───────────────┐    │
                    │   │  Reflector  │ <───  │   Selector    │    │
                    │   │ (Diagnosis) │       │(Prune/Top-K)  │    │
                    │   └─────────────┘       └───────┬───────┘    │
                    │                                 │            │
                    │                                 ▼            │
                    │                     ┌───────────────────────┐│
                    │                     │ Knowledge Graph Linker││
                    │                     │  (PostgreSQL Edge DB) ││
                    │                     └───────────┬───────────┘│
                    └─────────────────────────────────┼────────────┘
                                                      │ Promotion Gate
                                                      ▼
                    ┌──────────────────────────────────────────────┐
                    │               ONLINE INFERENCE               │
                    │                                              │
                    │  Order Inflow ──> [FastAPI Rule Sandbox]     │
                    │                           │                  │
                    │            ┌──────────────┴──────────────┐   │
                    │            ▼                             ▼   │
                    │      High / Low Risk              Marginal   │
                    │     (Auto-Decided)             (Human Review)│
                    │            │                             │   │
                    │            └──────────────┬──────────────┘   │
                    │                           ▼                  │
                    │                   PostgreSQL Logs            │
                    │                           │                  │
                    │                           ▼                  │
                    │                Drift & Spike Monitors        │
                    │                           │                  │
                    │       (Triggers Evolution Re-Entry) ─────────┘
                    └──────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology | Role / Purpose |
|---|---|---|
| **Frontend UI & Dashboard** | **Next.js (App Router, React, TailwindCSS, Lucide, Recharts)** | High-fidelity interactive merchant dashboard, hypothesis lineage graph, live traffic stream, drift analytics, and human review portal (replaces Streamlit). |
| **Database & Knowledge Store** | **PostgreSQL** | Relational state, hypothesis persistence, mutation graph edges, live scoring logs, and audit trails (replaces SQLite). |
| **Online Scoring Service** | **FastAPI (Python)** | High-throughput online evaluation engine, low-confidence routing, and live logging. |
| **Hypothesis & Mutation Engine** | **LLM APIs (Claude / OpenAI / Gemini)** | Code generation for executable feature/rule logic, automated error diagnosis, and mutation reasoning. |
| **Data & Baseline Benchmarks** | **pandas, scikit-learn, LightGBM** | Synthetic data handling, cost-weighted fitness calculation, and side-by-side static ML baseline benchmark. |
| **Execution Sandbox** | **Restricted Python Runtime** | Safe execution of generated Python rule ASTs without file or network access. |

---

## 📊 Dataset & Injected Drift Scenario

Located in [`idea_and_data/`](./idea_and_data/):
- **`train.csv` (Days 0–55)**: 10,807 orders — Baseline fraud pattern (high COD, first-time customers, known high-risk pincodes, large order values).
- **`validation.csv` (Days 56–75)**: 3,885 orders — Drift ramp-in (promo code stacking, device pool reuse, late-night ordering).
- **`held_out_test.csv` (Days 76–89)**: 2,641 orders — Post-drift evaluation (**frozen test split touched strictly once for final metrics**).
- **`full_dataset_with_phase_labels.csv`**: Master historical dataset for analysis.

For complete column schemas and causal rolling rate guarantees, refer to [`idea_and_data/data_card.md`](./idea_and_data/data_card.md).

---

## 🛡️ Production Guardrails & Honesty Guarantees

1. **Defense-Only Audit Gate**: Two-stage safety check (heuristic regex filter + secondary LLM evaluator) ensuring generated hypothesis rationales describe detection signals and never provide evasion tactics.
2. **Cost-Weighted Evaluator**: Penalizes False Positives (customer insult cost: $AOV \times \text{margin}$) more heavily than raw $F_1$, preventing over-blocking.
3. **Low-Confidence Human Review Routing**: Marginal risk scores are routed to an analyst queue rather than forced into auto-rejection.
4. **Honest Metrics Reporting**: Human review cases are explicitly tracked as a 3rd outcome class rather than pruned to artificially inflate precision/recall numbers.

---

## 📁 Repository Structure

```
├── backend/                  # FastAPI service, rule engine, & evolution runner
├── database/                 # PostgreSQL schemas, migrations, & connection pools
├── idea_and_data/            # Synthetic RTO/COD datasets & design specifications
│   ├── RTO_Fraud_SelfEvolving_Engine_Design (3).pdf
│   ├── data_card.md
│   ├── full_dataset_with_phase_labels.csv
│   ├── held_out_test.csv
│   ├── train.csv
│   └── validation.csv
├── .gitignore                # Environment, Python, and Node ignore rules
└── README.md                 # Project documentation & architecture overview
```

---

## 👤 Author
- **Name**: Mohil Mandape
- **GitHub**: [@MOHILMANDAPE15](https://github.com/MOHILMANDAPE15)
- **Email**: mohilmandpe33@gmail.com
