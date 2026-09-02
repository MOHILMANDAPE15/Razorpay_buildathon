export interface GlossaryEntry {
  term: string;
  category: 'pipeline' | 'agent' | 'gate' | 'trigger' | 'routing' | 'security';
  shortDesc: string;
  fullDesc: string;
  simpleExplanation: string;
  whyItMatters: string;
  inputsAndOutputs: {
    inputs: string;
    outputs: string;
  };
  metricOrFormula?: string;
  realWorldExample?: string;
}

export const GLOSSARY: Record<string, GlossaryEntry> = {
  new_order: {
    term: '1. New Order Stream',
    category: 'pipeline',
    shortDesc: 'Live incoming transaction telemetry entering the scoring pipeline.',
    simpleExplanation: 'When a customer places an e-commerce order (especially Cash-on-Delivery), raw checkout information is sent to the scoring engine in real time.',
    fullDesc: 'Raw checkout payload containing 17 order features (COD vs Prepaid, order value in INR, customer prior order history, pincode rolling RTO rate, device velocity, item category) evaluated in real-time under a strict <10ms SLA.',
    whyItMatters: 'Capturing fresh behavioral signals at the checkout moment is the first line of defense before physical package dispatch.',
    inputsAndOutputs: {
      inputs: 'Raw customer checkout payload (17 features, payment mode, pincode, device ID).',
      outputs: 'Sanitized feature dataframe delivered to the scoring ensemble.',
    },
    metricOrFormula: 'Scoring Latency < 10ms | 100% Deterministic Feature Ingestion',
    realWorldExample: 'A COD order of ₹1,499 from a newly created account in a high-risk pincode entering the live stream at 11:30 PM.',
  },

  frozen_ensemble: {
    term: '2. Frozen Serving Ensemble',
    category: 'pipeline',
    shortDesc: 'Production AST rule ensemble currently scoring live traffic.',
    simpleExplanation: 'The current active rulebook running in production. It is completely locked and frozen so live scoring is 100% predictable, lightning fast, and never hallucinating.',
    fullDesc: 'A locked snapshot of validated Python AST boolean rules and calibrated weights. It is never altered dynamically during scoring; it is only updated via atomic version promotion after candidate rules pass all 3 safety verification gates.',
    whyItMatters: 'Guarantees zero online LLM runtime dependency, millisecond execution, and total auditability for compliance and merchant SLAs.',
    inputsAndOutputs: {
      inputs: 'Sanitized order feature vector.',
      outputs: 'Composite risk score (0.0 to 1.0) and boolean match flags for each rule.',
    },
    metricOrFormula: 'Composite Risk Score = Baseline Risk + Σ Rule_Weights',
    realWorldExample: 'Serving snapshot `ensemble_v1` evaluating 3,885 validation orders with sub-millisecond Python AST execution.',
  },

  three_way_router: {
    term: '3. 3-Way Decision Router',
    category: 'routing',
    shortDesc: 'Splits traffic into Auto-Approve, Auto-Block, and Analyst Review.',
    simpleExplanation: 'Instead of forcing a binary Yes/No decision on uncertain orders, it sends clear orders through automatically and routes tricky borderline orders to human investigation.',
    fullDesc: 'Routes high-confidence fraud (Risk ≥ 0.70) to instant automated block, clear genuine buyers (Risk < 0.35) to frictionless auto-approve, and borderline risk (0.35 ≤ Risk < 0.70) to the human review queue without cherry-picking.',
    whyItMatters: 'Prevents false-positive customer insults (which destroy 15% merchant gross margin) while maintaining a 97%+ automated decision rate.',
    inputsAndOutputs: {
      inputs: 'Composite risk score from Frozen Ensemble.',
      outputs: 'Routing decision: AUTO_APPROVE, MANUAL_REVIEW, or AUTO_BLOCK.',
    },
    metricOrFormula: 'Auto-Block: Risk ≥ 0.70 | Review Queue: 0.35 ≤ Risk < 0.70 | Auto-Approve: Risk < 0.35',
    realWorldExample: 'An order scoring 0.42 is sent to the human review queue (where RTO concentration is 47.17%), while a 0.85 order is blocked automatically.',
  },

  outcome_logged: {
    term: '4. Outcome Logged & Maturation',
    category: 'pipeline',
    shortDesc: 'Delivery and courier outcome capture after physical fulfillment.',
    simpleExplanation: 'After physical shipping, couriers take 5 to 7 days to deliver packages. Once the true outcome (Delivered vs RTO Refusal) is confirmed, it becomes ground truth for continuous learning.',
    fullDesc: 'Orders mature over a 5-day settlement window as couriers report final physical status (successful delivery vs buyer return/refusal). Mature outcomes form the verified ground truth dataset for residual mining and telemetry auditing.',
    whyItMatters: 'Fraud defense requires real delivery ground truth. Prematurely scanning un-matured orders creates false feedback loops.',
    inputsAndOutputs: {
      inputs: '3PL courier webhook updates (DELIVERED or RTO_REFUSED).',
      outputs: 'Labeled database records with finalized `is_rto` ground truth.',
    },
    metricOrFormula: 'Maturation Window = 5 Days Post-Order Fulfillment',
    realWorldExample: 'Courier confirms an order was refused at the doorstep after 5 days, locking `is_rto = 1` for residual analysis.',
  },

  triggers: {
    term: '5. Autonomous Adaptation Triggers',
    category: 'trigger',
    shortDesc: 'Three continuous sentinels that detect anomalies and initiate evolution.',
    simpleExplanation: 'Three vigilant background watchdogs that constantly look for sudden spikes, gradual drift, and hidden clusters of missed fraud.',
    fullDesc: 'Unified monitoring layer comprising the Real-Time Spike Monitor (immediate volume anomalies), Concept Drift Detector (feature distribution shifts), and Residual Miner (mature false negatives).',
    whyItMatters: 'Ensures the system wakes up autonomously when attack dynamics shift, without waiting for human analysts to notice decay.',
    inputsAndOutputs: {
      inputs: 'Live scoring stream and matured ground truth records.',
      outputs: 'Autonomous evolution trigger alerts and targeted candidate briefs.',
    },
    metricOrFormula: 'Multi-Sentinel Alert Bus: Spike (Z > 2.5σ) OR Drift (PSI > 0.25) OR Residual Miner (p < 0.01)',
  },

  spike_monitor: {
    term: 'Spike Monitor Sentinel',
    category: 'trigger',
    shortDesc: 'Zero-label lag sliding-window Z-score and CUSUM change-point detector.',
    simpleExplanation: 'Tracks the flag rate over a 40-order sliding window. If fraud suddenly surges, it detects the statistical anomaly immediately without needing labels.',
    fullDesc: 'Monitors the live flag rate over a 40-order sliding window. Triggers alerts when burst traffic exceeds Z > 2.50σ or CUSUM accumulates persistent rate deviations above baseline (8.0%).',
    whyItMatters: 'Catches bot attacks, credential stuffing, and sudden promo abuse campaigns within minutes of onset.',
    inputsAndOutputs: {
      inputs: 'Live boolean flags from the scoring stream.',
      outputs: 'Real-time Z-score, CUSUM accumulator, and CRITICAL_SPIKE alerts.',
    },
    metricOrFormula: 'Z = (k - n·p0) / sqrt(n·p0·(1-p0)) | Trigger Hurdle: Z ≥ 2.50σ',
    realWorldExample: 'Fraud flag rate surges from 8.0% to 45.0% during a flash sale; Z-score reaches 3.82σ and fires a spike alert.',
  },

  drift_detector: {
    term: 'Concept Drift Sentinel',
    category: 'trigger',
    shortDesc: 'Statistical distribution shift detector tracking population drift.',
    simpleExplanation: 'Compares current buyer characteristics against historical baselines to detect subtle shifts in buyer behavior and fraud syndicates.',
    fullDesc: 'Evaluates Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) tests across key order features against the baseline training distribution to detect adversarial behavior changes.',
    whyItMatters: 'Detects stealthy fraud migration where total volume looks normal but the underlying behavior (e.g. account age or pincode mix) has shifted.',
    inputsAndOutputs: {
      inputs: 'Current 14-day feature distributions vs Day 0–55 baseline.',
      outputs: 'Per-feature PSI scores and distribution drift severity status.',
    },
    metricOrFormula: 'PSI = Σ (Actual% - Expected%) × ln(Actual% / Expected%) | Threshold: PSI > 0.25',
    realWorldExample: 'A shift where throwaway accounts (<2 days old) suddenly represent 40% of high-value COD mobile purchases.',
  },

  residual_miner: {
    term: 'Residual Mining Sentinel',
    category: 'trigger',
    shortDesc: 'Scans mature delivery logs to discover unflagged false-negative clusters.',
    simpleExplanation: 'The core innovation of Aegis-RTO: it inspects every order that slipped past our rules and resulted in RTO, clustering them into distinct attack signatures.',
    fullDesc: 'Analyzes matured orders where the frozen ensemble scored low risk but the order was actually returned (false negatives). Runs HDBSCAN/agglomerative clustering and Fisher’s exact tests to formulate structured defense agendas.',
    whyItMatters: 'Transforms painful fraud losses into structured machine-readable agendas for autonomous rule synthesis.',
    inputsAndOutputs: {
      inputs: 'Matured false-negative orders (`is_rto = 1` and `decision = AUTO_APPROVE`).',
      outputs: 'Discovered high-risk cluster cohorts with bounding feature signatures.',
    },
    metricOrFormula: 'Cohort Isolation: Fisher Exact p < 0.01 | Minimum Cohort Size: 30 orders',
    realWorldExample: 'Isolating an unflagged cluster of ₹400–₹900 COD fashion orders with 0 prior orders in high-risk pincodes.',
  },

  mature_orders: {
    term: '1. Mature Orders Ingestion',
    category: 'pipeline',
    shortDesc: 'Ingests orders with finalized 5-day delivery or RTO ground truth.',
    simpleExplanation: 'Only orders that have finished the 5-day courier delivery window are used for learning, guaranteeing 100% verified labels.',
    fullDesc: 'Filters out in-transit transactions to ensure the residual miner only analyzes verified delivery successes and confirmed RTO rejections.',
    whyItMatters: 'Eliminates label noise and prevents the evolution engine from penalizing orders that are still in delivery vans.',
    inputsAndOutputs: {
      inputs: 'Order telemetry table joined with 3PL delivery confirmation logs.',
      outputs: 'Matured ground-truth dataset filtered to order age ≥ 5 days.',
    },
    metricOrFormula: 'Order Age ≥ 5 Days Post-Dispatch',
    realWorldExample: 'Selecting only orders from Days 56–70 during a Day 75 adaptation run.',
  },

  miss_clustering: {
    term: '2. False-Negative Miss Clustering',
    category: 'pipeline',
    shortDesc: 'Hierarchical agglomerative clustering isolating unflagged RTO patterns.',
    simpleExplanation: 'Groups similar unflagged fraud orders together so we can understand the pattern rather than treating every loss as random.',
    fullDesc: 'Uses unsupervised hierarchical agglomerative clustering and HDBSCAN across behavioral dimensions (payment mode, account age, pincode risk, velocity) to group unflagged misses into tight cohorts.',
    whyItMatters: 'Identifies the exact multi-dimensional boundary where fraud syndicates are bypassing existing heuristics.',
    inputsAndOutputs: {
      inputs: 'Normalized feature vectors of all unflagged RTO misses.',
      outputs: 'Discrete candidate cluster groups with centroid signatures.',
    },
    metricOrFormula: 'HDBSCAN / Agglomerative Ward Linkage across 6 core risk features',
    realWorldExample: 'Cluster #3: COD + account age < 3 days + pincode RTO rate > 28% + order value ≤ ₹500.',
  },

  significance_guard: {
    term: '3. Statistical Significance Guard',
    category: 'gate',
    shortDesc: 'Fisher’s Exact / Chi-Square hypothesis test validating cluster density.',
    simpleExplanation: 'A strict statistical check ensuring a discovered fraud cluster is genuinely abnormal, not just a random coincidence.',
    fullDesc: 'Calculates contingency tables and runs Fisher’s Exact Test or Chi-Square tests against the background population to ensure cluster RTO concentration is statistically significant at p < 0.01.',
    whyItMatters: 'Prevents the engine from overreacting to tiny random courier delays and creating overfit rules.',
    inputsAndOutputs: {
      inputs: 'Cluster cohort RTO rate vs ambient population RTO rate.',
      outputs: 'P-value and statistical acceptance boolean flag.',
    },
    metricOrFormula: 'Fisher’s Exact Test p < 0.01 | Minimum 30 orders in cohort',
    realWorldExample: 'Cluster with 78% RTO density vs 28% baseline yields p = 0.00004 (< 0.01), passing the guard.',
  },

  cooldown_check: {
    term: '4. Cluster Cooldown Guard',
    category: 'gate',
    shortDesc: 'Suppresses duplicate synthesis for recently addressed fraud clusters.',
    simpleExplanation: 'Remembers what fraud patterns we already addressed in the last 3 rounds so we do not waste time creating duplicate rules.',
    fullDesc: 'Enforces a 3-round cooldown window per cluster signature to avoid redundant LLM synthesis and ensemble rule bloat.',
    whyItMatters: 'Keeps the rule ensemble clean, compact, and non-redundant while conserving LLM token budgets.',
    inputsAndOutputs: {
      inputs: 'Cluster signature hash and recent evolution round history.',
      outputs: 'Cooldown status: ELIGIBLE or SUPPRESSED.',
    },
    metricOrFormula: 'Cooldown Window = 3 Evolution Rounds',
    realWorldExample: 'Suppressing synthesis for a low-value COD cluster that was already addressed in Round 4.',
  },

  defense_agenda: {
    term: '5. Targeted Defense Agenda',
    category: 'trigger',
    shortDesc: 'Synthesizes targeted hypothesis briefs for the Core Evolution Loop.',
    simpleExplanation: 'Packages the discovered fraud pattern into a structured mission brief that tells our Generator Agent exactly what kind of rule to build.',
    fullDesc: 'Packages cluster feature bounds, error attributions, and economic ROI targets into a structured prompt passed directly to the Generator Agent.',
    whyItMatters: 'Gives the LLM explicit, grounded constraints so it synthesizes precise rules instead of guessing blind.',
    inputsAndOutputs: {
      inputs: 'Validated cluster feature boundaries and economic loss metrics.',
      outputs: 'Structured JSON/Markdown defense agenda brief for Generator.',
    },
    metricOrFormula: 'Target Agenda: Feature bounds, target precision ≥ 65%, minimum net INR savings',
    realWorldExample: 'Agenda: "Create a rule targeting COD orders under ₹500 from new accounts in pincodes with >28% RTO rate."',
  },

  core_evolution_loop: {
    term: '6. Core Multi-Agent Evolution Loop',
    category: 'pipeline',
    shortDesc: 'The central multi-agent synthesis, mutation, and verification engine.',
    simpleExplanation: 'An automated pair-programming team of AI agents that write, test, critique, and select new fraud defense rules in Python AST code.',
    fullDesc: 'An autonomous pair-programming loop where Generator synthesizes rules, Evaluator computes cost-weighted fitness, Reflector diagnoses false positives, Selector prunes overfit candidates, and 3 safety gates verify production readiness.',
    whyItMatters: 'Replaces weeks of manual SQL/Python rule engineering with verifiable, auditable autonomous evolution in under 2 minutes.',
    inputsAndOutputs: {
      inputs: 'Defense agenda from Residual Miner or Drift Sentinels.',
      outputs: 'Fully validated candidate rule ensemble ready for shadow promotion.',
    },
    metricOrFormula: 'Multi-Agent Iteration: Generator → Evaluator → Reflector → Selector → 3 Safety Gates',
  },

  generator: {
    term: '1. Generator Agent',
    category: 'agent',
    shortDesc: 'Synthesizes and mutates candidate Python AST fraud rules.',
    simpleExplanation: 'The AI rule creator. It writes clean, sandboxed Python code that evaluates transaction features to catch the target fraud.',
    fullDesc: 'Uses structured LLM prompts conditioned on historical error reflections, discovered residual clusters, and existing ensemble rules to generate syntactically safe boolean expressions.',
    whyItMatters: 'Produces human-readable, auditable code that executes natively inside Python with zero latency overhead.',
    inputsAndOutputs: {
      inputs: 'Target agenda brief, error diagnoses, and existing ensemble rules.',
      outputs: 'Candidate Python boolean functions (e.g. `def predict(df): ...`).',
    },
    metricOrFormula: 'Safe AST Grammar · Zero eval() · Memory & CPU Capped Sandbox',
    realWorldExample: 'Synthesizing `def predict(df): return (df["payment_mode"] == "COD") & (df["order_value"] <= 500) & (df["customer_prior_orders"] == 0)`.',
  },

  evaluator: {
    term: '2. Evaluator Agent',
    category: 'agent',
    shortDesc: 'Executes candidate AST rules in a security sandbox on validation data.',
    simpleExplanation: 'The mathematical referee. It runs the generated code across thousands of real transactions and calculates exact INR profit and loss.',
    fullDesc: 'Executes candidate AST rules in a memory-capped Python sandbox on validation data. Computes precision, recall, flag rate, and net financial savings enforcing ₹250 RTO savings vs 15% false-positive customer insult penalties.',
    whyItMatters: 'Ensures rules are judged by real merchant unit economics, not vanity machine learning accuracy scores.',
    inputsAndOutputs: {
      inputs: 'Candidate AST rule code and validation transaction dataset.',
      outputs: 'Precision, recall, flag rate, and Net Financial Savings in INR.',
    },
    metricOrFormula: 'Net Savings = (True Positives × ₹250) - Σ (False Positives × Order_Value × 0.15)',
    realWorldExample: 'Catching 42 RTOs (+₹10,500) while causing only 4 false positives (-₹600), delivering +₹9,900 net savings.',
  },

  reflector: {
    term: '3. Reflector Agent',
    category: 'agent',
    shortDesc: 'Diagnoses rule failures and directly synthesizes a mutated child rule via its own LLM call.',
    simpleExplanation: 'The diagnostic mutator. When a candidate rule causes false alarms or fails execution, the Reflector diagnoses exactly why — then synthesizes a corrected mutated child rule itself using its own LLM call. The child is immediately sent back to the Evaluator for re-scoring.',
    fullDesc: 'Performs causal error attribution on misclassified orders, then calls its own LLM to produce an evolved child hypothesis with tighter boundaries. The parent rule failure diagnosis is also persisted to the Notepad, where it informs the Generator in the next evolution round.',
    whyItMatters: 'Turns failed rule attempts into iterative stepping stones, evolving high-precision rules through guided self-mutation — without needing a full extra Generator round.',
    inputsAndOutputs: {
      inputs: 'False positive order feature details, rule misclassification logs, and parent rule code.',
      outputs: 'Mutated child RuleHypothesis (sent to Evaluator for re-scoring) + failure diagnosis stored in Notepad.',
    },
    metricOrFormula: 'Causal Attribution: Feature importance differential on false positive cohorts | Child re-evaluated by Evaluator in same round',
    realWorldExample: 'Diagnosing that legitimate prepaid buyers were caught by a loose threshold; Reflector directly writes and returns a tightened child rule adding `df["payment_mode"] == "COD"` constraint.',
  },

  selector: {
    term: '4. Selector & Ensemble Pruner',
    category: 'agent',
    shortDesc: 'Assembles complementary rule ensembles and prunes redundant rules.',
    simpleExplanation: 'The team builder. It picks the best combination of rules that work together without overlap or bloat.',
    fullDesc: 'Selects the top-performing non-collinear rules using greedy forward selection to maximize collective net savings without inflating collective flag rate.',
    whyItMatters: 'Prevents rule sprawl and ensures the final ensemble is compact, fast, and covers multiple independent attack vectors.',
    inputsAndOutputs: {
      inputs: 'Pool of evaluated candidate rules and baseline ensemble.',
      outputs: 'Pareto-optimal candidate ensemble with individual rule weights.',
    },
    metricOrFormula: 'Greedy Forward Selection maximizing Marginal Net INR Gain',
    realWorldExample: 'Selecting 2 complementary rules that together boost net savings by ₹16,167 while pruning 4 redundant variants.',
  },

  regression_gate: {
    term: '5. Gate 1: Pre-Drift Regression Gate',
    category: 'gate',
    shortDesc: 'Verifies that new rules do not destroy baseline performance.',
    simpleExplanation: 'The historical safeguard. Tests candidate rules against our original pre-drift data to make sure they do not break existing clean performance.',
    fullDesc: 'Tests candidate ensembles against historical pre-drift training data (Days 0–55). Enforces that net savings do not drop by >5% compared to the existing serving ensemble.',
    whyItMatters: 'Guarantees that adapting to new fraud attacks never compromises defense against classic established fraud patterns.',
    inputsAndOutputs: {
      inputs: 'Candidate ensemble and pre-drift baseline dataset (Days 0–55).',
      outputs: 'Regression delta percentage and Gate 1 PASS/FAIL verdict.',
    },
    metricOrFormula: 'Regression Delta = (Candidate_Savings - Baseline_Savings) / Baseline_Savings ≥ -5.0%',
    realWorldExample: 'Candidate ensemble achieves -0.8% delta on pre-drift data (well within the -5.0% threshold) and passes Gate 1.',
  },

  held_out_gate: {
    term: '6. Gate 2: Held-Out Verification Gate',
    category: 'gate',
    shortDesc: 'Single-touch validation on strictly isolated test data.',
    simpleExplanation: 'The blind exam. Evaluates the candidate ensemble once on an isolated test split to prove it did not cheat or memorize validation data.',
    fullDesc: 'Evaluates the final candidate ensemble once on the physically separated validation split (Days 56–75). Guards against validation overfitting and cherry-picking.',
    whyItMatters: 'Provides uncompromising scientific proof of out-of-sample generalization before real money is at risk.',
    inputsAndOutputs: {
      inputs: 'Candidate ensemble and isolated validation split table.',
      outputs: 'Validation precision, break-even hurdle clearance, and Gate 2 PASS/FAIL.',
    },
    metricOrFormula: 'Precision ≥ Break-Even Precision (22.26%) | Net INR Savings > 0',
    realWorldExample: 'Achieving 37.25% precision (exceeding 22.26% break-even hurdle) with +₹2,458 net savings, passing Gate 2.',
  },

  decoy_guard: {
    term: '7. Decoy Guard & AST Security Audit',
    category: 'security',
    shortDesc: 'Adversarial perturbation testing and synthetic honeypot validation.',
    simpleExplanation: 'The security audit. Verifies that rules are safe Python AST code with zero illegal imports, memory caps, and zero reliance on noisy decoy features.',
    fullDesc: 'Ensures candidate rules exhibit 0% false alerts on clean decoy traffic, never reference unauthorized decoy columns (device_model_name, app_theme_color), and execute in a sandboxed AST runtime.',
    whyItMatters: 'Guarantees zero remote code execution vulnerabilities, prevents overfit to decoy features, and ensures complete enterprise security compliance.',
    inputsAndOutputs: {
      inputs: 'Candidate rule AST syntax tree and decoy perturbation test vectors.',
      outputs: 'Security audit certificate and Decoy Guard PASS/FAIL.',
    },
    metricOrFormula: 'Decoy Correlation == 0.00 | Disallowed AST Nodes == 0',
    realWorldExample: 'AST inspection confirms only boolean operators on 17 approved schema columns with zero system imports.',
  },

  promoted_ensemble: {
    term: '8. Promoted Champion Rule',
    category: 'pipeline',
    shortDesc: 'Verified rule promoted to production serving snapshot.',
    simpleExplanation: 'The champion finish line! The rule has passed every test, shadow deployment, and security audit, and is atomically promoted into the live serving ensemble.',
    fullDesc: 'Atomic promotion to live serving registry after passing Gate 1, Gate 2, and Decoy Guard. Updates production serving weights, closing the loop and protecting all future transactions.',
    whyItMatters: 'Closes the full autonomous loop: moving from detected loss to live deployed defense without human bottleneck.',
    inputsAndOutputs: {
      inputs: 'Triple-verified candidate rule ensemble.',
      outputs: 'Updated production snapshot in `frozen_rule_snapshot.py` and serving registry.',
    },
    metricOrFormula: 'Shadow Deployment → Canary Testing → Atomic Production Snapshot Bump',
    realWorldExample: 'Promoting `hyp_r3_3_f4b4` into serving ensemble, increasing overall validation recovery to ₹22,734.77.',
  },

  feedback_loop_retry: {
    term: 'Failure Reflection Loop-Back',
    category: 'pipeline',
    shortDesc: 'Rejected hypotheses feed diagnoses back into Generator.',
    simpleExplanation: 'When a candidate rule fails any test, it is not thrown away — its failure notes are sent straight back to the Generator to write a better version.',
    fullDesc: 'Instead of disappearing, failed candidates are annotated with Reflector diagnoses and re-queued into the Generator to evolve stronger child hypotheses in the next iteration.',
    whyItMatters: 'Enables continuous learning and evolutionary convergence rather than random trial and error.',
    inputsAndOutputs: {
      inputs: 'Failed rule code and failure attribution diagnostics.',
      outputs: 'Re-queued mutation seed for next evolution cycle.',
    },
  },

  loop_syntax_fail: {
    term: 'Evaluator Fast-Fail Drop Loop',
    category: 'gate',
    shortDesc: 'Syntax/runtime failures cause the candidate to be dropped; Generator synthesizes fresh candidates in the next round.',
    simpleExplanation: 'If the Evaluator receives a candidate with a syntax error or runtime exception (is_valid=False), it does NOT call the Reflector — the candidate is simply dropped from the population. The Generator handles its own syntax repair internally via repair_rule_code during generation, and fresh candidates are proposed in the next round.',
    fullDesc: 'The Reflector only runs on candidates where is_valid=True. A candidate that fails sandboxed execution is marked invalid and removed. The Generator uses an internal repair_rule_code fallback to fix syntax errors at generation time before a candidate is ever sent to the Evaluator.',
    whyItMatters: 'Ensures 100% syntactically valid executable code before any computationally heavy evaluation or gate testing begins.',
    inputsAndOutputs: {
      inputs: 'Python syntax / execution traceback from Evaluator sandbox.',
      outputs: 'Candidate dropped from population; Generator proposes fresh candidates next round.',
    },
    metricOrFormula: 'Immediate AST Error Intercept (< 50ms) | Reflector NOT invoked on is_valid=False',
  },

  loop_regression_fail: {
    term: 'Regression Gate Pruning Loop',
    category: 'gate',
    shortDesc: 'Gate 1 failures are pruned from the population; failure digest feeds the next-round Generator via Notepad.',
    simpleExplanation: 'If a candidate rule performs well on new fraud but hurts old clean traffic by more than 5%, Gate 1 rejects it and marks it as pruned. Critically, it does NOT immediately re-run the Generator in the same round — the failure reason is instead stored in the Notepad and informs the Generator\'s next evolution round.',
    fullDesc: 'When a candidate ensemble regresses on pre-drift data by more than 5%, the candidate is marked as pruned and removed from the active top-K population. The regression failure reason is persisted via the Notepad history summary, which is fed as context into the Generator at the start of the next evolution round — enabling iterative boundary tightening across rounds.',
    whyItMatters: 'Guarantees the system never degrades pre-existing merchant margins while chasing new fraud — and uses failure signals as structured learning for future generation rounds.',
    inputsAndOutputs: {
      inputs: 'Pre-drift regression logs (> 5% drop in net savings).',
      outputs: 'Candidate marked pruned; failure digest written to Notepad for next-round Generator context.',
    },
    metricOrFormula: 'Trigger: Regression Delta < -5.0% | Feedback: via Notepad history summary in next round',
  },

  loop_promotion: {
    term: 'Main Closed-Loop Production Feedback',
    category: 'pipeline',
    shortDesc: 'The primary closing loop of the entire Aegis-RTO architecture.',
    simpleExplanation: 'The crowning loop of the entire self-evolving system: promoted rules travel all the way back to the top of the architecture, updating the Frozen Serving Ensemble (Node 2) so live orders are protected from that second on.',
    fullDesc: 'The recursive backbone of autonomous defense: once a rule passes all 3 safety verification gates, it updates the production serving weights snapshot in Node 2, completing the closed loop from detection to production defense.',
    whyItMatters: 'Eliminates the traditional 2-to-4 week manual data science and deployment lag, cutting adaptation turnaround to under 2 minutes.',
    inputsAndOutputs: {
      inputs: 'Champion ensemble promoted from Gate 3.',
      outputs: 'Updated production serving weights snapshot for Node 2.',
    },
    metricOrFormula: 'Closed-Loop Lifecycle: Detection → Synthesis → Verification → Serving Snapshot',
  },
};
