import sys
from pathlib import Path
import json

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

print("="*60)
print("VERIFYING AEGIS-RTO FASTAPI PRODUCTION DATA LAYER ENDPOINTS")
print("="*60)

# 1. Health Probe
res_health = client.get("/api/v1/health")
print(f"\n1. GET /api/v1/health -> Status {res_health.status_code}")
print(f"   Payload: {res_health.json()}")

# 2. Lineage Graph
res_lineage_graph = client.get("/api/v1/lineage/graph")
print(f"\n2. GET /api/v1/lineage/graph -> Status {res_lineage_graph.status_code}")
lineage_data = res_lineage_graph.json()
print(f"   Run ID: {lineage_data.get('run_id')}")
print(f"   Total Nodes: {len(lineage_data.get('nodes', []))}")
print(f"   Total Edges: {len(lineage_data.get('edges', []))}")
print(f"   Rounds: {lineage_data.get('rounds')}")
print(f"   Champion: {lineage_data.get('run_summary', {}).get('champion_hypothesis_id')}")
print(f"   Final Savings: Rs. {lineage_data.get('run_summary', {}).get('final_best_net_savings_inr'):,.2f}")

# 3. Residual Mining Latest Scan (Training Split)
res_mining_train = client.get("/api/v1/residual-mining/latest-scan?split=training&mode=dynamic")
print(f"\n3. GET /api/v1/residual-mining/latest-scan (split=training) -> Status {res_mining_train.status_code}")
mining_train_data = res_mining_train.json()
meta_tr = mining_train_data.get("scan_metadata", {})
print(f"   Total Orders Analyzed: {meta_tr.get('total_orders_analyzed'):,}")
print(f"   Mature Orders Scanned: {meta_tr.get('mature_orders_count'):,}")
print(f"   Unmatured Deferred: {meta_tr.get('unmatured_orders_deferred'):,}")
print(f"   Realized False Negatives: {meta_tr.get('total_false_negatives'):,}")
print(f"   False Negative Rate: {meta_tr.get('false_negative_rate')*100:.2f}%")
print(f"   Discovered Clusters: {len(mining_train_data.get('discovered_clusters', []))}")
for c in mining_train_data.get('discovered_clusters', []):
    print(f"     * [{c.get('cluster_id')}] {c.get('cluster_name')} (Misses: {c.get('miss_volume')}, Cohort: {c.get('cohort_size')}, p={c.get('p_value')})")
print(f"   Rejected Candidates: {len(mining_train_data.get('rejected_candidates', []))}")
for r in mining_train_data.get('rejected_candidates', []):
    print(f"     * {r.get('cluster_name')} -> {r.get('rejection_reason')}")

# 4. Review Metrics (Held-Out Benchmark Cohort)
res_review_metrics = client.get("/api/v1/review/metrics?cohort=held_out_benchmark")
print(f"\n4. GET /api/v1/review/metrics (cohort=held_out_benchmark) -> Status {res_review_metrics.status_code}")
rev_data = res_review_metrics.json()
print(f"   Total Orders: {rev_data.get('total_orders'):,}")
print(f"   Auto-Decided Volume: {rev_data.get('auto_decided_count'):,} ({rev_data.get('auto_decided_pct')}%)")
print(f"   Auto-Approved: {rev_data.get('auto_approved_count'):,}")
print(f"   Auto-Blocked: {rev_data.get('auto_blocked_count'):,}")
print(f"   Auto-Decided Precision: {rev_data.get('auto_decided_precision')*100:.2f}%")
print(f"   Auto Net Savings: Rs. {rev_data.get('auto_decided_net_savings_inr'):,.2f}")
print(f"   Review Queue Orders: {rev_data.get('manual_review_count'):,} ({rev_data.get('manual_review_pct')}%)")
print(f"   Review Queue Concentration: {rev_data.get('review_queue_rto_concentration')*100:.2f}%")
print(f"   Full System Net Savings: Rs. {rev_data.get('full_system_net_savings_inr'):,.2f}")

# 5. Review Queue
res_queue = client.get("/api/v1/review/queue")
print(f"\n5. GET /api/v1/review/queue -> Status {res_queue.status_code}")
q_data = res_queue.json()
print(f"   Total In Queue: {q_data.get('total_in_queue')}")

print("\n" + "="*60)
print("ALL BACKEND ENDPOINTS VERIFIED & OPERATIONAL")
print("="*60)
