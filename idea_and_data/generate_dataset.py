"""Dataset generation script for Aegis-RTO.

Single source of truth for all three CSV splits.  Re-run this script whenever
the schema or decoy columns change to keep all data files consistent.

Decoy columns added (Section 5.4 circularity guard):
  - device_model_name : random smartphone model string, NO causal link to is_rto
  - app_theme_color   : random UI theme string,        NO causal link to is_rto

These are added to PERMISSIBLE_FEATURE_COLUMNS so the Generator can see and
potentially use them. A well-calibrated evolved system should NEVER assign
positive fitness to a rule that depends solely on decoy columns.

After running this script, re-run database ingestion:
    cd backend
    python -m app.db.ingest

Reproducibility: DECOY_SEED=42. All other data is unchanged from the original
pre-generated full_dataset_with_phase_labels.csv (the base distribution is
preserved exactly).
"""

import pathlib
import sys

import numpy as np
import pandas as pd
from scipy import stats

# ─── Paths ───────────────────────────────────────────────────────────────────
THIS_DIR = pathlib.Path(__file__).resolve().parent
FULL_CSV = THIS_DIR / "full_dataset_with_phase_labels.csv"
TRAIN_CSV = THIS_DIR / "train.csv"
VAL_CSV = THIS_DIR / "validation.csv"
TEST_CSV = THIS_DIR / "held_out_test.csv"

# ─── Decoy configuration ─────────────────────────────────────────────────────
DECOY_SEED = 42
DEVICE_MODELS = ["Samsung_A54", "Redmi_9", "OnePlus_Nord", "iPhone_13", "Vivo_Y20"]
THEME_COLORS = ["dark", "light", "auto"]

# ─── Split boundaries (day_index based, chronological) ───────────────────────
TRAIN_MAX_DAY = 55     # days 0–55  → train
VAL_MAX_DAY = 75       # days 56–75 → validation
# days 76–89 → held_out_test


def add_decoy_columns(df: pd.DataFrame, seed: int = DECOY_SEED) -> pd.DataFrame:
    """Appends two decoy columns to df with a fixed seed and NO causal link to is_rto.

    Values are assigned uniformly at random, independent of every other column.
    """
    rng = np.random.default_rng(seed)
    n = len(df)
    df = df.copy()
    df["device_model_name"] = rng.choice(DEVICE_MODELS, size=n)
    df["app_theme_color"] = rng.choice(THEME_COLORS, size=n)
    return df


def verify_decoy_independence(df: pd.DataFrame) -> None:
    """Chi-square test: confirms decoy columns have no statistical association with is_rto.

    Raises AssertionError if any decoy shows significant correlation (p < 0.01).
    """
    print("\n[Decoy Verification] Chi-square independence test vs is_rto:")
    for col in ["device_model_name", "app_theme_color"]:
        contingency = pd.crosstab(df[col], df["is_rto"])
        chi2, p, dof, expected = stats.chi2_contingency(contingency)
        status = "OK (independent)" if p > 0.01 else "FAIL (correlated!)"
        print(f"  {col:22s}  chi2={chi2:.3f}  p={p:.4f}  dof={dof}  [{status}]")
        if p <= 0.01:
            raise AssertionError(
                f"Decoy column '{col}' has unexpected correlation with is_rto (p={p:.4f}). "
                "Check DECOY_SEED or generation logic."
            )

    # Also eyeball RTO rate per category
    print("\n[Decoy Verification] RTO rate per decoy category (should be ~flat):")
    for col in ["device_model_name", "app_theme_color"]:
        rates = df.groupby(col)["is_rto"].mean().round(4)
        overall = df["is_rto"].mean()
        print(f"  {col}:")
        for cat, rate in rates.items():
            diff_pct = abs(rate - overall) * 100
            print(f"    {cat:20s} RTO={rate:.4f}  (d={diff_pct:.2f}pp from overall {overall:.4f})")


def regenerate_splits(full_df: pd.DataFrame) -> None:
    """Re-writes train.csv, validation.csv, held_out_test.csv from the full dataset."""
    train = full_df[full_df["day_index"] <= TRAIN_MAX_DAY].reset_index(drop=True)
    val = full_df[
        (full_df["day_index"] > TRAIN_MAX_DAY) & (full_df["day_index"] <= VAL_MAX_DAY)
    ].reset_index(drop=True)
    test = full_df[full_df["day_index"] > VAL_MAX_DAY].reset_index(drop=True)

    train.to_csv(TRAIN_CSV, index=False)
    val.to_csv(VAL_CSV, index=False)
    test.to_csv(TEST_CSV, index=False)
    full_df.to_csv(FULL_CSV, index=False)

    print(f"\n[Splits] Written:")
    print(f"  train.csv           {len(train):>6,} rows  (days 0–{TRAIN_MAX_DAY})")
    print(f"  validation.csv      {len(val):>6,} rows  (days {TRAIN_MAX_DAY+1}–{VAL_MAX_DAY})")
    print(f"  held_out_test.csv   {len(test):>6,} rows  (days {VAL_MAX_DAY+1}–89)")
    print(f"  full_dataset_...csv {len(full_df):>6,} rows  (all days)")


def main() -> None:
    print("=" * 60)
    print("Aegis-RTO Dataset Generator")
    print("=" * 60)

    # Safety check: confirm held_out_test guard hasn't fired yet (belt-and-suspenders)
    print("\n[Safety] Confirming held-out test single-touch guard has NOT fired...")
    try:
        sys.path.insert(0, str(THIS_DIR.parent / "backend"))
        from app.data.loader import _HELD_OUT_TEST_ACCESSED  # type: ignore
        if _HELD_OUT_TEST_ACCESSED:
            raise RuntimeError(
                "ABORT: evaluate_on_held_out_test() was already called in this runtime. "
                "Regeneration must happen in a fresh process before the guard fires."
            )
        print("  Guard has NOT fired. Safe to regenerate.")
    except ImportError:
        print("  Could not import loader (not in Python path). Proceeding — confirm manually.")

    # 1. Load existing full dataset (source of truth for real feature distributions)
    print(f"\n[Load] Reading {FULL_CSV.name}...")
    df_full = pd.read_csv(FULL_CSV)
    print(f"  Shape: {df_full.shape}  |  Columns: {df_full.columns.tolist()}")

    # 2. Drop decoy columns if already present (idempotent re-run)
    for col in ["device_model_name", "app_theme_color"]:
        if col in df_full.columns:
            df_full = df_full.drop(columns=[col])
            print(f"  Dropped existing decoy column: {col}")

    # 3. Add decoy columns with fixed seed
    print(f"\n[Decoys] Adding decoy columns (seed={DECOY_SEED})...")
    df_full = add_decoy_columns(df_full, seed=DECOY_SEED)
    print(f"  device_model_name categories: {sorted(df_full['device_model_name'].unique())}")
    print(f"  app_theme_color   categories: {sorted(df_full['app_theme_color'].unique())}")

    # 4. Verify decoy statistical independence from is_rto
    verify_decoy_independence(df_full)

    # 5. Re-write all CSVs with decoys included
    print("\n[Write] Regenerating split CSVs with decoy columns...")
    regenerate_splits(df_full)

    print("\n[Done] Dataset regenerated successfully.")
    print(
        "\nNEXT STEP: Re-ingest into PostgreSQL:\n"
        "  cd backend && python -m app.db.ingest\n"
        "  (also re-run: python -m app.db.session to verify table columns)"
    )


if __name__ == "__main__":
    main()
