import sys
from pathlib import Path
import os
import pandas as pd

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Read train.csv directly to get true ground truth numbers
train_csv_path = Path(__file__).resolve().parent.parent.parent / "idea_and_data" / "train.csv"
df_train = pd.read_csv(train_csv_path)

print(f"=== Direct CSV Inspection ===")
print(f"Total train orders: {len(df_train)}")
max_day = df_train['day_index'].max()
print(f"Max day index in train: {max_day}")
mature_df = df_train[df_train['day_index'] <= (max_day - 5)]
print(f"Mature orders count (day <= {max_day-5}): {len(mature_df)}")
print(f"Unmatured deferred: {len(df_train) - len(mature_df)}")

from app.engine.frozen_rule_snapshot import load_frozen_v1_rules
from app.engine.selector import EnsembleRule
rules = load_frozen_v1_rules()
ens = EnsembleRule(rules)
from app.data.schema import sanitize_features
sanitized = sanitize_features(mature_df)
flags = ens.predict(sanitized)
y_true = mature_df['is_rto'].to_numpy().astype(int)
fn_mask = (y_true == 1) & (flags == 0)
total_fn = int(fn_mask.sum())
fn_rate = total_fn / len(mature_df)
print(f"True mature False Negatives (FN): {total_fn}")
print(f"True mature False Negative Rate: {fn_rate:.4f} ({fn_rate*100:.2f}%)")

from app.engine.residual_miner import ResidualMiner
miner = ResidualMiner(maturity_window_days=5)
report = miner.run_residual_analysis(df_train, ens, current_day_index=max_day, current_round=3)
print(f"Report total FN: {report.total_false_negatives}")
print(f"Report FN rate: {report.false_negative_rate:.4f} ({report.false_negative_rate*100:.2f}%)")
print(f"Report discovered clusters: {len(report.clusters_identified)}")
for c in report.clusters_identified:
    print(f"  - {c.cluster_id}: {c.cluster_name} (misses={c.miss_count}, cohort={c.total_mature_orders_in_cohort}, p={c.p_value})")
print(f"Report rejected candidates: {len(report.rejected_insignificant_clusters)}")
for r in report.rejected_insignificant_clusters:
    print(f"  - {r.cluster_name} (reason: {r.rejection_reason})")
