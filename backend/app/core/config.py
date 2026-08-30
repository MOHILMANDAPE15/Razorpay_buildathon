"""Configuration settings and cost model parameters for Aegis-RTO."""

import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def _resolve_data_dir() -> Path:
    """Dynamically resolves canonical dataset directory across local, Docker, and production paths."""
    env_dir = os.getenv("DATA_DIR")
    if env_dir and Path(env_dir).exists():
        return Path(env_dir)

    # 1. Workspace repo root: <repo>/idea_and_data
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    if (repo_root / "idea_and_data").exists():
        return repo_root / "idea_and_data"

    # 2. Backend root or Docker /app/idea_and_data: <backend>/idea_and_data
    backend_root = Path(__file__).resolve().parent.parent.parent
    if (backend_root / "idea_and_data").exists():
        return backend_root / "idea_and_data"

    # 3. Current working directory
    cwd = Path.cwd()
    if (cwd / "idea_and_data").exists():
        return cwd / "idea_and_data"
    if (cwd.parent / "idea_and_data").exists():
        return cwd.parent / "idea_and_data"

    return repo_root / "idea_and_data"


DATA_DIR = _resolve_data_dir()


class CostModelConfig(BaseModel):
    """Cost parameters calibrated against e-commerce COD/RTO benchmarks."""
    
    # Avoided loss per correctly-flagged RTO order (Rs. 150 - 300)
    avoided_rto_cost_inr: float = Field(
        default=float(os.getenv("AVOIDED_RTO_COST_INR", "250.0")),
        description="True Positive value: logistics, return shipping & restocking loss avoided (₹)"
    )
    
    # False Positive insult cost modeled per-order as order_value * margin
    fp_margin_loss_rate: float = Field(
        default=float(os.getenv("FP_MARGIN_LOSS_RATE", "0.15")),
        description="Assumed merchant gross profit margin lost on genuine order false blocks (e.g. 15%)"
    )
    
    # Execution timeout for sandboxed rule evaluation
    rule_timeout_sec: float = Field(
        default=float(os.getenv("RULE_TIMEOUT_SEC", "3.0")),
        description="Maximum seconds permitted for executing a single rule across a dataset"
    )


class DataPaths(BaseModel):
    """Paths to canonical split datasets."""
    train_path: Path = DATA_DIR / "train.csv"
    validation_path: Path = DATA_DIR / "validation.csv"
    held_out_test_path: Path = DATA_DIR / "held_out_test.csv"
    full_dataset_path: Path = DATA_DIR / "full_dataset_with_phase_labels.csv"


cost_config = CostModelConfig()
data_paths = DataPaths()
