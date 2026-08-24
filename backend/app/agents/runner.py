"""Autonomous Evolution Runner coordinating the multi-round self-evolving fraud engine."""

import time
from typing import Dict, List, Optional
import pandas as pd
from pydantic import BaseModel, Field

from app.agents.generator import HypothesisGenerator
from app.agents.reflector import HypothesisReflector
from app.data.loader import load_validation_data
from app.data.schema import sanitize_features
from app.engine.evaluator import CostWeightedEvaluator
from app.engine.notepad import Notepad
from app.engine.regression import RegressionHarness
from app.engine.types import EvaluationReport, RegressionReport, RuleHypothesis


class RoundLog(BaseModel):
    """Execution log for a single evolutionary round."""
    round_number: int
    hypotheses_proposed: int
    hypotheses_evaluated: int
    mutations_generated: int
    gate_1_passed_count: int
    best_rule_name: str
    best_rule_net_savings_inr: float
    best_rule_precision: float
    best_rule_recall: float


class EvolutionSummary(BaseModel):
    """End-to-end report of the multi-round evolution experiment."""
    total_rounds: int
    total_hypotheses_tested: int
    total_active_hypotheses: int
    total_execution_time_sec: float
    initial_best_net_savings_inr: float
    final_best_net_savings_inr: float
    net_savings_delta_inr: float
    round_logs: List[RoundLog] = Field(default_factory=list)
    top_rules: List[Dict] = Field(default_factory=list)


class EvolutionRunner:
    """Orchestrates the autonomous evolutionary cycle across multiple rounds:
    Generator -> Evaluator -> Reflector -> Gate 1 Regression Suite -> Selector -> Notepad.
    """

    def __init__(
        self,
        generator: Optional[HypothesisGenerator] = None,
        reflector: Optional[HypothesisReflector] = None,
        evaluator: Optional[CostWeightedEvaluator] = None,
        regression_harness: Optional[RegressionHarness] = None,
        notepad: Optional[Notepad] = None,
    ):
        self.generator = generator or HypothesisGenerator()
        self.reflector = reflector or HypothesisReflector()
        self.evaluator = evaluator or CostWeightedEvaluator()
        self.regression_harness = regression_harness or RegressionHarness(evaluator=self.evaluator)
        self.notepad = notepad or Notepad()

    def run_evolution(
        self,
        rounds: int = 2,
        hypotheses_per_round: int = 2,
        df_validation: Optional[pd.DataFrame] = None,
        top_k_keep: int = 4,
    ) -> EvolutionSummary:
        """Executes multi-round self-evolution.
        
        Args:
            rounds: Number of evolutionary generations to execute.
            hypotheses_per_round: Number of new proposals per generator round.
            df_validation: Optional validation DataFrame (defaults to canonical validation.csv).
            top_k_keep: Maximum number of active alive rules to preserve.
            
        Returns:
            EvolutionSummary: Full evolutionary trajectory and final champion rules.
        """
        start_time = time.perf_counter()
        df_val = df_validation if df_validation is not None else load_validation_data()
        df_sample = sanitize_features(df_val.head(20))

        initial_best_net = 0.0
        active_baseline_report: Optional[EvaluationReport] = None
        round_logs: List[RoundLog] = []

        print(f"\n[EvolutionRunner] Starting {rounds}-Round Self-Evolution Loop on {len(df_val)} validation orders...")

        for r in range(1, rounds + 1):
            print(f"\n{'='*25} ROUND {r} / {rounds} {'='*25}")
            
            # Step 1: Generator proposes candidate rules
            history_summary = self.notepad.get_history_summary_for_generator()
            print(f"[Generator] Proposing {hypotheses_per_round} candidate hypotheses...")
            candidates = self.generator.generate_hypotheses(
                n_hypotheses=hypotheses_per_round,
                notepad_summary=history_summary,
                generation_round=r,
                df_sample=df_sample,
            )
            print(f"[Generator] Generated {len(candidates)} valid candidate rules.")

            # Register candidates in Notepad
            for c in candidates:
                self.notepad.add_hypothesis(c)

            # Step 2: Evaluator scores all candidate rules
            mutations: List[RuleHypothesis] = []
            gate_1_passed = 0

            for cand in candidates:
                print(f"[Evaluator] Scoring candidate [{cand.id}] '{cand.name}'...")
                report = self.evaluator.evaluate_hypothesis(cand, df_val)
                self.notepad.record_evaluation(report)

                if report.is_valid and report.cost_metrics and report.standard_metrics:
                    cm = report.cost_metrics
                    sm = report.standard_metrics
                    print(
                        f"  -> Precision: {sm.precision*100:.1f}% | Recall: {sm.recall*100:.1f}% | "
                        f"Net Value: Rs. {cm.net_financial_savings_inr:,.2f}"
                    )

                    # Gate 1 check against active baseline
                    passed, reg_report, _ = self.regression_harness.evaluate_candidate(
                        candidate_hypothesis=cand,
                        df_validation=df_val,
                        baseline_report=active_baseline_report,
                    )
                    if passed:
                        gate_1_passed += 1
                        cand.status = "alive"
                    else:
                        print(f"  [Gate 1] Regressed: {'; '.join(reg_report.reasons)}")

                    # Step 3: Reflector diagnoses failures & mutates rule
                    print(f"[Reflector] Diagnosing errors for [{cand.id}] and mutating rule...")
                    mutated = self.reflector.reflect_and_mutate(
                        parent_hypothesis=cand,
                        eval_report=report,
                        generation_round=r,
                        df_sample=df_sample,
                    )
                    if mutated:
                        print(f"[Reflector] Synthesized mutated rule: '{mutated.name}'")
                        mutations.append(mutated)
                        self.notepad.add_hypothesis(mutated)

            # Step 4: Evaluate mutated rules
            for mut in mutations:
                print(f"[Evaluator] Scoring mutated rule [{mut.id}] '{mut.name}'...")
                mut_report = self.evaluator.evaluate_hypothesis(mut, df_val)
                self.notepad.record_evaluation(mut_report)

                if mut_report.is_valid and mut_report.cost_metrics and mut_report.standard_metrics:
                    cm = mut_report.cost_metrics
                    sm = mut_report.standard_metrics
                    print(
                        f"  [Mutated Result] Precision: {sm.precision*100:.1f}% | Recall: {sm.recall*100:.1f}% | "
                        f"Net Value: Rs. {cm.net_financial_savings_inr:,.2f}"
                    )

                    passed, reg_report, _ = self.regression_harness.evaluate_candidate(
                        candidate_hypothesis=mut,
                        df_validation=df_val,
                        baseline_report=active_baseline_report,
                    )
                    if passed:
                        gate_1_passed += 1
                        mut.status = "alive"

            # Step 5: Selector maintains top-K population
            top_ranked = self.notepad.get_top_hypotheses(top_k=top_k_keep)
            active_ids = [hyp.id for hyp, rep in top_ranked]
            self.notepad.prune_unselected(active_ids)

            if top_ranked:
                best_hyp, best_rep = top_ranked[0]
                active_baseline_report = best_rep
                if r == 1:
                    initial_best_net = best_rep.cost_metrics.net_financial_savings_inr

                round_logs.append(
                    RoundLog(
                        round_number=r,
                        hypotheses_proposed=len(candidates),
                        hypotheses_evaluated=len(candidates) + len(mutations),
                        mutations_generated=len(mutations),
                        gate_1_passed_count=gate_1_passed,
                        best_rule_name=best_hyp.name,
                        best_rule_net_savings_inr=best_rep.cost_metrics.net_financial_savings_inr,
                        best_rule_precision=best_rep.standard_metrics.precision,
                        best_rule_recall=best_rep.standard_metrics.recall,
                    )
                )
                print(
                    f"\n[Round {r} Champion] '{best_hyp.name}' -> Net Rs. {best_rep.cost_metrics.net_financial_savings_inr:,.2f} "
                    f"(Precision: {best_rep.standard_metrics.precision*100:.1f}%, Recall: {best_rep.standard_metrics.recall*100:.1f}%)"
                )

        total_exec_sec = time.perf_counter() - start_time
        final_top = self.notepad.get_top_hypotheses(top_k=top_k_keep)
        final_best_net = final_top[0][1].cost_metrics.net_financial_savings_inr if final_top else 0.0

        top_rules_summary = [
            {
                "id": h.id,
                "name": h.name,
                "status": h.status,
                "parent_ids": h.parent_ids,
                "net_financial_savings_inr": rep.cost_metrics.net_financial_savings_inr,
                "precision": rep.standard_metrics.precision,
                "recall": rep.standard_metrics.recall,
                "f1": rep.standard_metrics.f1,
                "code": h.code,
            }
            for h, rep in final_top
        ]

        return EvolutionSummary(
            total_rounds=rounds,
            total_hypotheses_tested=len(self.notepad.registry),
            total_active_hypotheses=len(final_top),
            total_execution_time_sec=round(total_exec_sec, 2),
            initial_best_net_savings_inr=round(initial_best_net, 2),
            final_best_net_savings_inr=round(final_best_net, 2),
            net_savings_delta_inr=round(final_best_net - initial_best_net, 2),
            round_logs=round_logs,
            top_rules=top_rules_summary,
        )
