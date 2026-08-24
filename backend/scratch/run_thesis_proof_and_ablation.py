"""Executes Section 4.7 Live Frozen Rule Ensemble Thesis Proof and Section 5.4 Blinded Ablation.

Produces hard experimental artifacts:
1. v1_frozen_rules_snapshot.json (real evolved pre-drift baseline)
2. thesis_proof_and_ablation_results.json (complete comparison matrix)
"""

import json
import os
import sys
from pathlib import Path

# Ensure backend root is on sys.path
THIS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = THIS_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import numpy as np
import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm import get_llm_client
from app.core.sandbox import execute_rule_sandboxed
from app.data.loader import load_train_data, load_validation_data
from app.data.schema import (
    BLINDED_COLUMN_MAP,
    BLINDED_COLUMN_REVERSE_MAP,
    get_blinded_dataframe,
    sanitize_features,
)
from app.engine.baseline import StaticV1Baseline
from app.engine.evaluator import CostWeightedEvaluator
from app.engine.frozen_rule_snapshot import (
    FrozenRuleEnsemble,
    LIVE_SNAPSHOT_PATH,
    generate_frozen_rule_snapshot,
)
from app.engine.notepad import Notepad
from app.engine.selector import CostWeightedSelector
from app.engine.types import RuleHypothesis
from app.agents.prompts import BLINDED_SCHEMA_DOCUMENTATION


def run_section_4_7_live_proof():
    """Generates the real frozen v1 ensemble on train, then measures its degradation on val."""
    print("\n" + "=" * 70)
    print("STEP 1: Generating Live Section 4.7 Frozen Ensemble on Train (Days 0-55)")
    print("=" * 70)

    # 1. Generate live frozen snapshot via LLM evolution on train
    snapshot = generate_frozen_rule_snapshot(live=True, n_rounds=2)

    # 2. Load frozen ensemble and evaluate on validation (drift exposure)
    print("\n" + "=" * 70)
    print("STEP 2: Evaluating Frozen Ensemble on Validation (Days 56-75, Drift Ramp-in)")
    print("=" * 70)

    df_train = load_train_data()
    df_val = load_validation_data()

    frozen_ensemble = FrozenRuleEnsemble(LIVE_SNAPSHOT_PATH).load()
    train_report = frozen_ensemble.evaluate(df_train, split_name="train")
    val_report = frozen_ensemble.evaluate(df_val, split_name="validation")

    print("\n[Section 4.7 Live Results] Frozen Ensemble Drift Impact:")
    print(f"  Train Net Savings (Pre-Drift):  Rs. {train_report.cost_metrics.net_financial_savings_inr:,.2f}  "
          f"(Precision: {train_report.standard_metrics.precision*100:.1f}%, Recall: {train_report.standard_metrics.recall*100:.1f}%)")
    print(f"  Val Net Savings (Post-Drift):   Rs. {val_report.cost_metrics.net_financial_savings_inr:,.2f}  "
          f"(Precision: {val_report.standard_metrics.precision*100:.1f}%, Recall: {val_report.standard_metrics.recall*100:.1f}%)")
    delta_val = val_report.cost_metrics.net_financial_savings_inr - train_report.cost_metrics.net_financial_savings_inr
    print(f"  Degradation Delta:             Rs. {delta_val:,.2f}")

    return {
        "train": {
            "precision": train_report.standard_metrics.precision,
            "recall": train_report.standard_metrics.recall,
            "f1": train_report.standard_metrics.f1,
            "net_savings_inr": train_report.cost_metrics.net_financial_savings_inr,
        },
        "validation_drift": {
            "precision": val_report.standard_metrics.precision,
            "recall": val_report.standard_metrics.recall,
            "f1": val_report.standard_metrics.f1,
            "net_savings_inr": val_report.cost_metrics.net_financial_savings_inr,
        },
        "degradation_delta_inr": round(delta_val, 2),
    }


def run_section_5_4_blinded_ablation():
    """Runs a live Generator round with blinded column names (col_01..col_19)."""
    print("\n" + "=" * 70)
    print("STEP 3: Running Section 5.4 Blinded-Naming Ablation Experiment")
    print("=" * 70)

    blinded_system_prompt = f"""You are the Lead Fraud Detection Rule Engineer for Aegis-RTO.
Your task is to analyze an e-commerce order dataset with blinded column names and propose high-precision vectorized fraud detection rules.

{BLINDED_SCHEMA_DOCUMENTATION}

CRITICAL RULES:
1. Define a vectorized function `predict(df: pd.DataFrame)` returning boolean Series or 0/1 array.
2. Use ONLY column names from the schema (`col_01` to `col_19`). Do NOT guess or use real names.
3. Respond in valid JSON adhering to:
{{
    "name": "Title of Rule",
    "target_columns": ["col_09", "col_13"],
    "description": "Description of the pattern",
    "rationale": "Reasoning based on the column distributions and semantics",
    "code": "def predict(df):\\n    return (df['col_09'] == 'COD') & (df['col_13'] > 0.3)"
}}
"""

    blinded_user_prompt = """Generation Round: 1 (Blinded Ablation Run)

TASK:
Propose 2 diverse fraud detection rules using ONLY the available blinded columns (`col_01` through `col_19`).
Look for column combinations that separate high-risk orders from normal orders (e.g. payment mode col_09, location risk col_13, promo abuse col_14, device velocity col_16).
Do not assume column importance — reason directly from the column types and value distributions.

Respond with a JSON array containing 2 rule objects.
"""

    llm = get_llm_client(temperature=0.7)
    messages = [
        SystemMessage(content=blinded_system_prompt),
        HumanMessage(content=blinded_user_prompt),
    ]

    print("[Blinded Ablation] Prompting LLM with blinded column schema...")
    response = llm.invoke(messages)
    content = response.content.strip()
    if content.startswith("```json"):
        content = content.split("```json", 1)[1].split("```", 1)[0].strip()
    elif content.startswith("```"):
        content = content.split("```", 1)[1].split("```", 1)[0].strip()

    raw_rules = json.loads(content)
    if isinstance(raw_rules, dict):
        raw_rules = [raw_rules]

    df_val = load_validation_data()
    df_blinded = get_blinded_dataframe(df_val)
    evaluator = CostWeightedEvaluator()

    blinded_results = []
    print(f"\n[Blinded Ablation] Evaluated {len(raw_rules)} blinded rules:")

    for r in raw_rules:
        name = r.get("name", "Blinded Rule")
        code = r.get("code", "")
        desc = r.get("description", "")
        rationale = r.get("rationale", "")

        # Execute rule directly on blinded dataframe (it uses col_XX names)
        hyp = RuleHypothesis(
            id=f"blinded_{len(blinded_results)+1}",
            name=name,
            code=code,
            description=desc,
            rationale=rationale,
        )

        try:
            flags = execute_rule_sandboxed(code, sanitize_features(df_blinded))
            report = evaluator.evaluate_flags(flags, df_val, hyp.id, hyp.name)
            
            # Map blinded column names back to real names to see what was discovered
            used_cols = [col for col in BLINDED_COLUMN_MAP.values() if col in code]
            mapped_real_cols = [BLINDED_COLUMN_REVERSE_MAP.get(c, c) for c in used_cols]
            decoy_used = any(c in ["col_18", "col_19"] for c in used_cols)

            result_entry = {
                "name": name,
                "code": code,
                "blinded_columns_used": used_cols,
                "mapped_real_columns": mapped_real_cols,
                "decoy_column_used": decoy_used,
                "precision": report.standard_metrics.precision,
                "recall": report.standard_metrics.recall,
                "f1": report.standard_metrics.f1,
                "net_savings_inr": report.cost_metrics.net_financial_savings_inr,
            }
            blinded_results.append(result_entry)

            safe_name = name.encode('ascii', 'replace').decode('ascii')
            print(f"\n  Rule: '{safe_name}'")
            print(f"    Blinded cols used: {used_cols} -> Real: {mapped_real_cols}")
            print(f"    Decoy used: {decoy_used}")
            print(f"    Precision: {report.standard_metrics.precision*100:.1f}%  |  Recall: {report.standard_metrics.recall*100:.1f}%")
            print(f"    Net Savings: Rs. {report.cost_metrics.net_financial_savings_inr:,.2f}")
        except Exception as e:
            safe_name = name.encode('ascii', 'replace').decode('ascii')
            print(f"  Error evaluating '{safe_name}': {str(e).encode('ascii', 'replace').decode('ascii')}")

    return blinded_results


def main():
    print("=" * 70)
    print("AEGIS-RTO: Section 4.7 Thesis Proof & Section 5.4 Ablation Live Run")
    print("=" * 70)

    # 1. Section 4.7 Live Thesis Proof
    sec_4_7_data = run_section_4_7_live_proof()

    # 2. Section 5.4 Blinded Ablation
    sec_5_4_data = run_section_5_4_blinded_ablation()

    # 3. Save comprehensive results
    output_path = BACKEND_DIR.parent / "thesis_proof_and_ablation_results.json"
    full_output = {
        "experiment_title": "Section 4.7 Frozen Rule Drift Proof and Section 5.4 Blinded Ablation",
        "timestamp": "2026-08-24",
        "section_4_7_frozen_rule_proof": sec_4_7_data,
        "section_5_4_blinded_ablation": sec_5_4_data,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(full_output, f, indent=2)

    print("\n" + "=" * 70)
    print(f"[SUCCESS] All experimental results saved to: {output_path.name}")
    print("=" * 70)


if __name__ == "__main__":
    main()
