"""Seed rich 5-round evolution runs and lineage DAG data into the database."""

from datetime import datetime, timezone
from app.db.session import get_engine, get_session_factory, Base
from app.db.models import EvolutionRun, Hypothesis, HypothesisLineage, EvaluationReportModel

def seed_rich_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    SessionFactory = get_session_factory()
    db = SessionFactory()
    
    try:
        # Clear existing data to ensure clean 5-round DAG
        db.query(EvaluationReportModel).delete()
        db.query(HypothesisLineage).delete()
        db.query(Hypothesis).delete()
        db.query(EvolutionRun).delete()
        db.commit()

        run_id = "run_20260824_5rounds_evolution"
        run = EvolutionRun(
            run_id=run_id,
            status="COMPLETED",
            total_rounds=5,
            hypotheses_tested=13,
            initial_best_net_savings_inr=13273.93,
            final_best_net_savings_inr=24312.15,
            net_savings_delta_inr=11038.22,
            champion_hypothesis_id="hyp_r3_3_f4b4",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        db.add(run)
        db.flush()

        # ==========================================
        # ROUND 1: SEED HYPOTHESES
        # ==========================================
        h_r1_1 = Hypothesis(
            hypothesis_id="hyp_r1_1_seed",
            run_id=run_id,
            name="Baseline High-Risk Regional COD Filter",
            generation_round=1,
            status="alive",
            target_signal="baseline_risk",
            description="Initial seed hypothesis targeting high regional pincode RTO rates and COD payment mode.",
            rationale="COD orders in regions with high RTO rates represent speculative buyer intent.",
            rule_code="def predict(df):\n    return ((df['payment_mode'] == 'COD') & (df['pincode_rolling_rto_rate'] > 0.35))",
        )
        h_r1_2 = Hypothesis(
            hypothesis_id="hyp_r1_2_promo_seed",
            run_id=run_id,
            name="Broad Promotional COD Shield",
            generation_round=1,
            status="pruned",
            target_signal="promo_drift",
            description="Blocks all promo code users choosing COD.",
            rationale="Overly broad rule that damaged conversion on genuine promo shoppers.",
            rule_code="def predict(df):\n    return ((df['payment_mode'] == 'COD') & (df['promo_code_used'] == True))",
        )
        h_r1_3 = Hypothesis(
            hypothesis_id="hyp_r1_3_newcust",
            run_id=run_id,
            name="New Customer COD Baseline",
            generation_round=1,
            status="alive",
            target_signal="new_account_risk",
            description="Targets first-time customers placing COD orders with zero purchase history.",
            rationale="Accounts without history carry higher default risk on delivery.",
            rule_code="def predict(df):\n    return ((df['payment_mode'] == 'COD') & (df['customer_prior_orders'] == 0))",
        )

        # ==========================================
        # ROUND 2: CATEGORY SPECIALIZATION & PRUNING
        # ==========================================
        h_r2_1 = Hypothesis(
            hypothesis_id="hyp_r2_3_bd99",
            run_id=run_id,
            name="Fashion Category Unverified COD",
            generation_round=2,
            status="champion",
            target_signal="category_risk",
            description="Fashion items suffer high buyer remorse in COD models. Combines zero purchase history with elevated regional RTO.",
            rationale="Fashion COD orders from new customers in high-risk zones have extreme return rates. Capping order value at Rs.900 limits false positive insult.",
            rule_code="def predict(df):\n    return ((df['payment_mode'] == 'COD') & (df['customer_prior_orders'] == 0) & (df['item_category'] == 'fashion') & (df['pincode_rolling_rto_rate'] > 0.25) & (df['order_value'] <= 900))",
        )
        h_r2_2 = Hypothesis(
            hypothesis_id="hyp_r2_2_highval_pruned",
            run_id=run_id,
            name="High Order Value Hard Ceiling",
            generation_round=2,
            status="pruned",
            target_signal="high_value_cod",
            description="Pruned rule: flagging high-value COD orders incurred extreme false-positive merchant insult penalties.",
            rationale="15% gross profit margin loss on Rs.3000+ orders overwhelmed avoided RTO savings.",
            rule_code="def predict(df):\n    return ((df['payment_mode'] == 'COD') & (df['order_value'] > 3000))",
        )
        h_r2_3 = Hypothesis(
            hypothesis_id="hyp_r2_3_device_burst",
            run_id=run_id,
            name="Multi-Device Rapid Order Burst",
            generation_round=2,
            status="alive",
            target_signal="device_velocity",
            description="Detects rapid successive orders from the same device within 24 hours.",
            rationale="High device frequency indicates bot testing or promo abuse.",
            rule_code="def predict(df):\n    return ((df['device_order_count_24h'] >= 2) & (df['customer_prior_orders'] == 0))",
        )

        # ==========================================
        # ROUND 3: RISK CEILINGS & DEFENSE GATES
        # ==========================================
        h_r3_1 = Hypothesis(
            hypothesis_id="hyp_r3_3_f4b4",
            run_id=run_id,
            name="Low-Value COD Impulse Test Order Defense",
            generation_round=3,
            status="champion",
            target_signal="low_value_impulse",
            description="Ultra low-value COD orders from zero-history accounts.",
            rationale="Ultra low-value COD orders (under Rs. 500) frequently represent fake/speculative tests with negligible false positive insult cost.",
            rule_code="def predict(df):\n    return ((df['payment_mode'] == 'COD') & (df['customer_prior_orders'] == 0) & (df['pincode_rolling_rto_rate'] > 0.28) & (df['order_value'] <= 500))",
        )
        h_r3_2 = Hypothesis(
            hypothesis_id="hyp_r3_2_tier2_pruned",
            run_id=run_id,
            name="Unbounded Regional Ban",
            generation_round=3,
            status="pruned",
            target_signal="regional_blanket",
            description="Pruned by Gate 3: Policy audit rejected unbounded blanket location ban without customer risk factor.",
            rationale="Violated Defense-Only safety policy by penalizing genuine buyers in developing postal codes.",
            rule_code="def predict(df):\n    return (df['pincode_rolling_rto_rate'] >= 0.40)",
        )
        h_r3_3 = Hypothesis(
            hypothesis_id="hyp_r3_3_night_burst",
            run_id=run_id,
            name="Late-Night High-Risk Location COD Defense",
            generation_round=3,
            status="alive",
            target_signal="temporal_risk",
            description="Late night orders (10PM - 5AM) in high risk postal codes.",
            rationale="Late night impulse orders exhibit elevated cancellation rates at courier dispatch.",
            rule_code="def predict(df):\n    return ((df['payment_mode'] == 'COD') & (df['pincode_rolling_rto_rate'] >= 0.30) & ((df['order_hour'] >= 22) | (df['order_hour'] <= 5)) & (df['order_value'] <= 1200))",
        )

        # ==========================================
        # ROUND 4: COMPOUND SIGNAL SYNTHESIS
        # ==========================================
        h_r4_1 = Hypothesis(
            hypothesis_id="hyp_r4_1_promo_burst_cod",
            run_id=run_id,
            name="New Account Promotional COD Burst Shield",
            generation_round=4,
            status="champion",
            target_signal="promo_drift",
            description="Blocks multi-device promo exploitation on COD orders from zero-history accounts.",
            rationale="Synthesizes promo code drift with device velocity and zero prior orders.",
            rule_code="def predict(df):\n    return ((df['payment_mode'] == 'COD') & (df['customer_prior_orders'] == 0) & (df['promo_code_used'] == True) & (df['device_order_count_24h'] >= 2))",
        )
        h_r4_2 = Hypothesis(
            hypothesis_id="hyp_r4_2_overfit_pruned",
            run_id=run_id,
            name="Decoy Feature Overfit Rule",
            generation_round=4,
            status="pruned",
            target_signal="circular_decoy",
            description="Pruned by Reflector: Attempted to branch on decoy non-causal feature.",
            rationale="Rejected by safety filter for attempting to split on non-causal app theme feature.",
            rule_code="def predict(df):\n    return ((df['payment_mode'] == 'COD') & (df['app_theme_color'] == 'dark'))",
        )

        # ==========================================
        # ROUND 5: FINAL CONVERGENCE & SELECTION
        # ==========================================
        h_r5_1 = Hypothesis(
            hypothesis_id="hyp_r5_1_converged_champion",
            run_id=run_id,
            name="Calibrated Compound COD Fraud Shield",
            generation_round=5,
            status="champion",
            target_signal="compound_synergy",
            description="Final converged champion ensemble combining low-value impulse defense, category remorse, and promo velocity.",
            rationale="Achieves peak net financial savings across pre-drift and validation distribution shifts.",
            rule_code="def predict(df):\n    return ((df['payment_mode'] == 'COD') & (df['customer_prior_orders'] == 0) & ((df['order_value'] <= 500) | (df['item_category'] == 'fashion')) & (df['pincode_rolling_rto_rate'] > 0.25))",
        )
        h_r5_2 = Hypothesis(
            hypothesis_id="hyp_r5_2_redundant_pruned",
            run_id=run_id,
            name="Redundant Fashion Subset",
            generation_round=5,
            status="pruned",
            target_signal="redundancy",
            description="Pruned during Forward Selection: Zero marginal financial gain over champion ensemble.",
            rationale="Subsumed completely by hyp_r5_1_converged_champion with higher false positive overlap.",
            rule_code="def predict(df):\n    return ((df['payment_mode'] == 'COD') & (df['item_category'] == 'fashion') & (df['order_value'] <= 400))",
        )

        db.add_all([
            h_r1_1, h_r1_2, h_r1_3,
            h_r2_1, h_r2_2, h_r2_3,
            h_r3_1, h_r3_2, h_r3_3,
            h_r4_1, h_r4_2,
            h_r5_1, h_r5_2,
        ])
        db.flush()

        # ==========================================
        # LINEAGE MUTATION EDGES
        # ==========================================
        edges = [
            HypothesisLineage(
                parent_hypothesis_id="hyp_r1_1_seed",
                child_hypothesis_id="hyp_r2_3_bd99",
                relationship_type="MUTATION",
                mutation_strategy="SPECIALIZE_FEATURE",
            ),
            HypothesisLineage(
                parent_hypothesis_id="hyp_r1_1_seed",
                child_hypothesis_id="hyp_r2_2_highval_pruned",
                relationship_type="MUTATION",
                mutation_strategy="EXPLORATORY_SPLIT",
            ),
            HypothesisLineage(
                parent_hypothesis_id="hyp_r1_3_newcust",
                child_hypothesis_id="hyp_r2_3_device_burst",
                relationship_type="MUTATION",
                mutation_strategy="ADD_VELOCITY_CONSTRAINT",
            ),
            HypothesisLineage(
                parent_hypothesis_id="hyp_r2_3_bd99",
                child_hypothesis_id="hyp_r3_3_f4b4",
                relationship_type="MUTATION",
                mutation_strategy="TIGHTEN_ORDER_VALUE_BOUND",
            ),
            HypothesisLineage(
                parent_hypothesis_id="hyp_r1_1_seed",
                child_hypothesis_id="hyp_r3_2_tier2_pruned",
                relationship_type="MUTATION",
                mutation_strategy="AGGRESSIVE_REGIONAL_FILTER",
            ),
            HypothesisLineage(
                parent_hypothesis_id="hyp_r1_1_seed",
                child_hypothesis_id="hyp_r3_3_night_burst",
                relationship_type="MUTATION",
                mutation_strategy="TEMPORAL_WINDOWING",
            ),
            HypothesisLineage(
                parent_hypothesis_id="hyp_r2_3_device_burst",
                child_hypothesis_id="hyp_r4_1_promo_burst_cod",
                relationship_type="MUTATION",
                mutation_strategy="CROSS_RULE_SYNTHESIS",
            ),
            HypothesisLineage(
                parent_hypothesis_id="hyp_r3_3_f4b4",
                child_hypothesis_id="hyp_r4_2_overfit_pruned",
                relationship_type="MUTATION",
                mutation_strategy="EXPLORATORY_SPLIT",
            ),
            HypothesisLineage(
                parent_hypothesis_id="hyp_r3_3_f4b4",
                child_hypothesis_id="hyp_r5_1_converged_champion",
                relationship_type="MUTATION",
                mutation_strategy="CONVERGENCE_UNION",
            ),
            HypothesisLineage(
                parent_hypothesis_id="hyp_r4_1_promo_burst_cod",
                child_hypothesis_id="hyp_r5_1_converged_champion",
                relationship_type="MUTATION",
                mutation_strategy="ENSEMBLE_MERGE",
            ),
            HypothesisLineage(
                parent_hypothesis_id="hyp_r2_3_bd99",
                child_hypothesis_id="hyp_r5_2_redundant_pruned",
                relationship_type="MUTATION",
                mutation_strategy="REDUNDANT_REFINEMENT",
            ),
        ]
        db.add_all(edges)

        # ==========================================
        # EVALUATION REPORTS
        # ==========================================
        reports = [
            EvaluationReportModel(
                hypothesis_id="hyp_r5_1_converged_champion",
                dataset_split="validation",
                precision=0.485,
                recall=0.098,
                f1_score=0.163,
                accuracy=0.782,
                flag_rate=0.045,
                total_orders=3885,
                true_positives=118,
                false_positives=125,
                true_negatives=2800,
                false_negatives=842,
                avoided_rto_loss_inr=29500.0,
                false_positive_insult_cost_inr=5187.85,
                net_financial_savings_inr=24312.15,
                cost_efficiency_ratio=5.69,
                gate_1_status="PASSED",
            ),
            EvaluationReportModel(
                hypothesis_id="hyp_r3_3_f4b4",
                dataset_split="train",
                precision=0.312,
                recall=0.068,
                f1_score=0.111,
                accuracy=0.765,
                flag_rate=0.042,
                total_orders=10807,
                true_positives=176,
                false_positives=388,
                true_negatives=8000,
                false_negatives=2243,
                avoided_rto_loss_inr=44000.0,
                false_positive_insult_cost_inr=24780.0,
                net_financial_savings_inr=19220.0,
                cost_efficiency_ratio=1.77,
                gate_1_status="PASSED",
            ),
            EvaluationReportModel(
                hypothesis_id="hyp_r2_3_bd99",
                dataset_split="train",
                precision=0.285,
                recall=0.045,
                f1_score=0.078,
                accuracy=0.761,
                flag_rate=0.038,
                total_orders=10807,
                true_positives=116,
                false_positives=291,
                true_negatives=8097,
                false_negatives=2303,
                avoided_rto_loss_inr=29000.0,
                false_positive_insult_cost_inr=15726.0,
                net_financial_savings_inr=13273.93,
                cost_efficiency_ratio=1.84,
                gate_1_status="PASSED",
            ),
            EvaluationReportModel(
                hypothesis_id="hyp_r2_2_highval_pruned",
                dataset_split="train",
                precision=0.142,
                recall=0.012,
                f1_score=0.022,
                accuracy=0.742,
                flag_rate=0.018,
                total_orders=10807,
                true_positives=31,
                false_positives=187,
                true_negatives=8100,
                false_negatives=2489,
                avoided_rto_loss_inr=7750.0,
                false_positive_insult_cost_inr=84150.0,
                net_financial_savings_inr=-76400.0,
                cost_efficiency_ratio=0.09,
                gate_1_status="REJECTED",
            ),
        ]
        db.add_all(reports)

        db.commit()
        print("Database successfully seeded with complete 5-round Knowledge Graph DAG.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_rich_db()
