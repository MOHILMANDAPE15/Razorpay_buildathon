"""Ingestion utility to populate PostgreSQL isolated tables from canonical CSV files."""

import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import text

from app.core.config import data_paths
from app.db.session import Base, get_engine
from app.db.models import OrderTrain, OrderValidation, OrderHeldOutTest


def init_db(engine=None):
    """Creates all database tables defined in SQLAlchemy models."""
    db_engine = engine or get_engine()
    print("[DB] Initializing database tables...")
    Base.metadata.create_all(bind=db_engine)
    print("[DB] Tables created successfully.")


def ingest_split_csv(csv_path: Path, table_name: str, default_phase: str, default_drift_weight: float, engine=None) -> int:
    """Loads a single split CSV into its corresponding PostgreSQL table."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found at {csv_path}")

    db_engine = engine or get_engine()
    df = pd.read_csv(csv_path)

    # Ensure phase and drift_weight columns exist for narrative tracking
    if "phase" not in df.columns:
        df["phase"] = default_phase
    if "drift_weight" not in df.columns:
        df["drift_weight"] = default_drift_weight

    # Convert timestamps and boolean types
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.date
    df["order_datetime"] = pd.to_datetime(df["order_datetime"])
    df["is_first_time_customer"] = df["is_first_time_customer"].astype(bool)
    df["promo_code_used"] = df["promo_code_used"].astype(bool)
    df["is_rto"] = df["is_rto"].astype(int)

    # Load in chunks into database
    with db_engine.begin() as conn:
        conn.execute(text(f"DELETE FROM {table_name};"))
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi",
        )

    print(f"[DB] Ingested {len(df):,} rows into '{table_name}' from {csv_path.name}")
    return len(df)


def ingest_all_datasets(engine=None):
    """Ingests train.csv, validation.csv, and held_out_test.csv into their respective isolated tables."""
    db_engine = engine or get_engine()
    init_db(db_engine)

    print("\n[DB Ingestion] Starting dataset population into isolated tables...")
    train_count = ingest_split_csv(
        csv_path=data_paths.train_path,
        table_name="orders_train",
        default_phase="pre_drift",
        default_drift_weight=0.0,
        engine=db_engine,
    )
    val_count = ingest_split_csv(
        csv_path=data_paths.validation_path,
        table_name="orders_validation",
        default_phase="transition",
        default_drift_weight=0.5,
        engine=db_engine,
    )
    test_count = ingest_split_csv(
        csv_path=data_paths.held_out_test_path,
        table_name="orders_held_out_test",
        default_phase="post_drift",
        default_drift_weight=1.0,
        engine=db_engine,
    )

    total = train_count + val_count + test_count
    print(f"\n[DB Ingestion] Complete! Total orders stored: {total:,} across 3 isolated tables.")
    return {
        "orders_train": train_count,
        "orders_validation": val_count,
        "orders_held_out_test": test_count,
        "total": total,
    }


if __name__ == "__main__":
    try:
        ingest_all_datasets()
    except Exception as e:
        print(f"[DB Ingestion Error] {e}")
        sys.exit(1)
