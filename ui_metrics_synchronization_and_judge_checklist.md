# UI Metrics Synchronization & Judge-Ready Checklist

> **Technical Audit: Why Some UI Metrics Are Static vs. Dynamic & Judge Implementation Plan**  
> **Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager**

---

## 🔍 1. Direct Explanation: Why Aren't All UI Numbers Automatically Populated?

In our current codebase, there is a split between **dynamic real-time endpoints** and **static presentation templates**:

### ✅ What is Already 100% Dynamic via Backend APIs:
1. **Knowledge Graph (`/lineage`)**:
   - Queries `GET /api/v1/evolution/runs` and `GET /api/v1/lineage/{run_id}` directly from PostgreSQL database tables (`evolution_runs`, `rule_hypotheses`, `rule_edges`).
   - Node scorecards, code blocks, and DAG edges update live with every evolution run.
2. **Real-Time Spike Monitor (`/monitor`)**:
   - Polled every 3 seconds via `GET /api/v1/monitor/status` and `GET /api/v1/monitor/history`.
   - Real-time Z-scores, CUSUM meters, and SVG chart bars update dynamically as synthetic traffic is injected.
3. **Human Review Queue (`/review`)**:
   - Fetches live triage cases via `GET /api/v1/review/queue` and dynamically submits analyst decisions via `POST /api/v1/review/decision`.

### ⚠️ What Was Hardcoded in Static JSX (The Gap):
1. **Homepage Hero Footer (`/`)**:
   - The 4 KPI badges (`2,641 Orders`, `+₹8,072.21`, `47.17%`, `97.99%`) in `frontend/src/app/page.tsx` were hardcoded in JSX markup as presentation defaults before the latest benchmark runs completed.
2. **Ablation Matrix Page (`/shadow-control`)**:
   - The 3-way comparison cards in `frontend/src/app/shadow-control/page.tsx` contain hardcoded metric values (`₹24,312.15`, `₹34,441.85`, `₹35,428.00`) instead of calling a dedicated backend API endpoint.

---

## 🛠️ 2. What Needs to Be Implemented for Buildathon Judges

To ensure the UI is 100% automatically synchronized with the exact latest benchmark artifacts without manual hardcoding, we need **3 simple, high-impact fixes**:

### Fix 1: Add a Unified Benchmark Summary API Endpoint in FastAPI Backend
Create `GET /api/v1/benchmark/summary` in [`backend/app/api/routes.py`](file:///c:/Users/Dell/Razorpay_buildathon/backend/app/api/routes.py) that reads:
- `backend/scratch/final_held_out_test_results.json` (Held-Out Test Headline Metrics)
- `backend/scratch/shadow_control_results.json` (Section 4.7 Ablation Matrix)
- Section 6.2 Review Queue Breakdown
- Serves them as a single JSON response to the frontend.

### Fix 2: Dynamic Hooking on Homepage Hero (`frontend/src/app/page.tsx`)
Replace static numbers with `useEffect` calling `fetchBenchmarkSummary()`, dynamically populating:
- Test Dataset Volume (2,641 orders)
- Champion Auto-Decided Net Savings (`+₹2,458.91` / `+₹8,072.21`)
- Review Queue Risk Density (`47.17% / 1.52x`)
- Automated Routing Rate (`97.99%`)

### Fix 3: Dynamic Hooking on Ablation Matrix (`frontend/src/app/shadow-control/page.tsx`)
Update `ShadowControlPage` to fetch from `GET /api/v1/benchmark/summary` or `GET /api/v1/ablation/matrix`, rendering all 3 model cards dynamically from real JSON artifacts.

---

## 🎯 3. Judge Presentation Impact

| Area | Before Fix (Current) | After Fix (Judge-Ready) |
|---|---|---|
| **Data Integrity** | High in backend / reports; static in some UI cards | **100% end-to-end synchronized** from Python backend to React UI |
| **Auditability** | Judges must read markdown reports to see latest sweep | Judges see exact, auditable live metrics on every UI dashboard |
| **Demo Robustness** | Works well, but numbers require manual sync if data changes | **Zero-touch automatic updates** whenever new benchmarks are evaluated |

---

## 🚀 4. Ready to Execute?
I can immediately implement the `GET /api/v1/benchmark/summary` endpoint in the backend and update the frontend React components to make all metrics 100% dynamic and live.
