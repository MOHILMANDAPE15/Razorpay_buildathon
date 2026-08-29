export interface GlossaryEntry {
  term: string;
  category: 'pipeline' | 'agent' | 'gate' | 'trigger' | 'routing' | 'security';
  shortDesc: string;
  fullDesc: string;
  metricOrFormula?: string;
}

export const GLOSSARY: Record<string, GlossaryEntry> = {
  new_order: {
    term: 'New Order Stream',
    category: 'pipeline',
    shortDesc: 'Live incoming transaction telemetry entering the scoring pipeline.',
    fullDesc: 'Raw checkout payload containing 17 order features (COD/Prepaid, order value, customer history, pincode risk, device velocity, item category) evaluated in real-time (<10ms).',
  },
  frozen_ensemble: {
    term: 'Frozen Serving Ensemble',
    category: 'pipeline',
    shortDesc: 'Production AST rule ensemble currently scoring live traffic.',
    fullDesc: 'A locked snapshot of validated Python AST boolean rules. Never altered dynamically during scoring; only updated via atomic version promotion after passing all safety gates.',
    metricOrFormula: 'Composite Risk = Baseline Risk + Σ Rule_Weights',
  },
  three_way_router: {
    term: '3-Way Decision Router',
    category: 'routing',
    shortDesc: 'Splits traffic into Auto-Approve, Auto-Block, and Analyst Review.',
    fullDesc: 'Routes high-confidence fraud (T >= 0.70) to instant automated block, clear genuine orders to auto-approve, and borderline scores (0.35 <= T < 0.70) to the human review queue without cherry-picking.',
    metricOrFormula: 'Auto-Block: Score ≥ 0.70 | Review Queue: 0.35 ≤ Score < 0.70',
  },
  outcome_logged: {
    term: 'Outcome Logged & Maturation',
    category: 'pipeline',
    shortDesc: 'Delivery and courier outcome capture after physical fulfillment.',
    fullDesc: 'Orders mature over 5 to 7 days as couriers report final delivery or RTO (Return to Origin). Mature outcomes form the ground truth dataset for residual mining and telemetry auditing.',
  },
  triggers: {
    term: 'Autonomous Adaptation Triggers',
    category: 'trigger',
    shortDesc: 'Three specialized sentinels that detect anomalies and initiate evolution.',
    fullDesc: 'Unified monitoring layer comprising the Real-Time Spike Monitor (immediate volume anomalies), Concept Drift Detector (feature distribution shifts), and Residual Miner (mature false negatives).',
  },
  spike_monitor: {
    term: 'Spike Monitor Sentinel',
    category: 'trigger',
    shortDesc: 'Zero-label lag sliding-window Z-score and CUSUM change-point detector.',
    fullDesc: 'Monitors the live flag rate over a 50-order sliding window. Triggers alerts and cooldown checks when burst traffic exceeds Z > 3.0σ or CUSUM accumulates persistent rate deviations.',
    metricOrFormula: 'Z = (k - n·p0) / sqrt(n·p0·(1-p0)) | Threshold: Z > 3.0σ',
  },
  drift_detector: {
    term: 'Concept Drift Sentinel',
    category: 'trigger',
    shortDesc: 'Statistical distribution shift detector tracking population drift.',
    fullDesc: 'Evaluates Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) tests across key order features against the baseline training distribution to detect adversarial behavior changes.',
    metricOrFormula: 'PSI > 0.25 indicates significant distribution drift',
  },
  residual_miner: {
    term: 'Residual Mining Sentinel',
    category: 'trigger',
    shortDesc: 'Scans mature delivery logs to discover unflagged false-negative clusters.',
    fullDesc: 'Analyzes 5-day mature orders where the frozen ensemble failed to catch genuine RTOs. Runs Chi-Square tests (p < 0.05, min 30 orders) to formulate structured mutation agendas for the core evolution loop.',
    metricOrFormula: 'Chi-Square p < 0.05 with 3-round cluster cooldown',
  },
  core_evolution_loop: {
    term: 'Core Evolution Loop',
    category: 'pipeline',
    shortDesc: 'The central multi-agent synthesis, mutation, and verification engine.',
    fullDesc: 'An autonomous pair-programming loop where Generator synthesizes rules, Evaluator computes cost-weighted fitness, Reflector diagnoses false positives, and Selector prunes overfit candidates.',
  },
  generator: {
    term: 'Generator Agent',
    category: 'agent',
    shortDesc: 'Synthesizes and mutates candidate Python AST fraud rules.',
    fullDesc: 'Uses structured LLM prompts conditioned on historical error reflections, discovered residual clusters, and existing ensemble rules to generate syntactically safe boolean expressions.',
  },
  evaluator: {
    term: 'Evaluator Agent',
    category: 'agent',
    shortDesc: 'Executes candidate AST rules in a security sandbox on validation data.',
    fullDesc: 'Computes precision, recall, flag rate, and net financial savings in INR. Enforces the ₹250 RTO savings vs 15% false-positive customer insult penalty.',
    metricOrFormula: 'Net Savings = TP × ₹250 - Σ (FP × Order_Value × 0.15)',
  },
  reflector: {
    term: 'Reflector Agent',
    category: 'agent',
    shortDesc: 'Analyzes false positives and diagnoses specific feature failure modes.',
    fullDesc: 'Performs causal error attribution on misclassified orders, recommending targeted tightening (e.g. adding account age constraints or category filters) instead of discarding promising rules.',
  },
  selector: {
    term: 'Selector & Ensemble Pruner',
    category: 'agent',
    shortDesc: 'Assembles complementary rule ensembles and prunes redundant rules.',
    fullDesc: 'Selects the top-performing non-collinear rules using greedy forward selection to maximize collective net savings without inflating collective flag rate.',
  },
  regression_gate: {
    term: 'Gate 1: Pre-Drift Regression Gate',
    category: 'gate',
    shortDesc: 'Verifies that new rules do not destroy baseline performance.',
    fullDesc: 'Tests candidate ensembles against historical pre-drift training data (Days 0–55). Enforces that net savings do not drop by >5% compared to the existing serving ensemble.',
    metricOrFormula: 'Regression Delta < -5.0% = Immediate Rejection',
  },
  held_out_gate: {
    term: 'Gate 2: Locked Held-Out Verification Gate',
    category: 'gate',
    shortDesc: 'Single-touch validation on strictly isolated test data.',
    fullDesc: 'Evaluates the final candidate ensemble once on the physically separated held-out test table (Days 76–89). Guards against validation overfitting and cherry-picking.',
  },
  defense_audit: {
    term: 'Defense & Decoy Audit',
    category: 'security',
    shortDesc: 'Validates AST security and confirms zero circularity on decoy features.',
    fullDesc: 'Ensures generated rules never reference decoy columns (device_model_name, app_theme_color), use no unauthorized imports, and remain strictly auditable boolean logic.',
  },
  promoted_ensemble: {
    term: 'Promoted Champion Rule',
    category: 'pipeline',
    shortDesc: 'Verified rule promoted to production serving snapshot.',
    fullDesc: 'Atomic promotion to live serving registry after passing Gate 1, Gate 2, and Defense Audit, closing the feedback loop with updated serving weights.',
  },
  feedback_loop_retry: {
    term: 'Failure Reflection Loop-Back',
    category: 'pipeline',
    shortDesc: 'Rejected hypotheses feed diagnoses back into Generator.',
    fullDesc: 'Instead of disappearing, failed candidates are annotated with Reflector diagnoses and re-queued into the Generator to evolve stronger child hypotheses in the next iteration.',
  },
};
