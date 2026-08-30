/** API client for Aegis-RTO FastAPI backend */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

export interface EvolutionRunSummary {
  run_id: string;
  status: string;
  total_rounds: number;
  hypotheses_tested: number;
  initial_best_net_savings_inr: number;
  final_best_net_savings_inr: number;
  net_savings_delta_inr: number;
  champion_hypothesis_id: string | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface NodeMetrics {
  precision: number;
  recall: number;
  f1_score: number;
  flag_rate: number;
  net_financial_savings_inr: number;
  dataset_split: string;
}

export interface LineageNode {
  id: string;
  name: string;
  generation_round: number;
  status: 'champion' | 'candidate' | 'alive' | 'pruned';
  discovery_type?: 'hand_coded' | 'mutated' | 'autonomous_discovery';
  target_signal: string;
  description: string;
  rationale: string;
  rule_code: string;
  is_champion: boolean;
  parent_ids: string[];
  child_ids: string[];
  created_at: string | null;
  metrics: NodeMetrics | null;
}


export interface LineageEdge {
  id: string;
  source: string;
  target: string;
  relationship_type: string;
  mutation_strategy: string;
  created_at: string | null;
}

export interface LineageGraphResponse {
  run_id: string;
  run_summary: {
    run_id: string;
    status: string;
    champion_hypothesis_id: string | null;
    final_best_net_savings_inr: number;
    total_nodes: number;
    total_edges: number;
    total_rounds: number;
    total_champions: number;
  };
  rounds: number[];
  nodes: LineageNode[];
  edges: LineageEdge[];
}

export interface SplitEvaluationReport {
  report_id: number;
  dataset_split: string;
  precision: number;
  recall: number;
  f1_score: number;
  flag_rate: number;
  total_orders: number;
  true_positives: number;
  false_positives: number;
  avoided_rto_loss_inr: number;
  false_positive_insult_cost_inr: number;
  net_financial_savings_inr: number;
  gate_1_status: string;
}

export interface HypothesisDetails {
  hypothesis_id: string;
  run_id: string | null;
  name: string;
  generation_round: number;
  status: string;
  target_signal: string | null;
  description: string | null;
  rationale: string | null;
  rule_code: string;
  created_at: string | null;
  parents: Array<{
    hypothesis_id: string;
    name: string;
    relationship_type: string;
    mutation_strategy: string | null;
  }>;
  children: Array<{
    hypothesis_id: string;
    name: string;
    relationship_type: string;
    mutation_strategy: string | null;
  }>;
  evaluation_reports: SplitEvaluationReport[];
}

export interface AlertPayload {
  alert_id: string;
  timestamp: string;
  severity: string;
  metric: string;
  current_value: number;
  threshold_value: number;
  baseline_value: number;
  message: string;
  recommended_action: string;
}

export interface MonitorSnapshot {
  status: string;
  total_orders_processed: number;
  window_size: number;
  current_flag_rate: number;
  baseline_expected_rate: number;
  z_score: number;
  cusum_positive: number;
  cusum_threshold: number;
  active_alerts: AlertPayload[];
  timestamp: string;
}

export interface TimeSeriesPoint {
  step: number;
  timestamp: string;
  flag_rate: number;
  baseline: number;
  upper_bound: number;
  z_score: number;
  status: string;
}

export async function fetchEvolutionRuns(): Promise<EvolutionRunSummary[]> {
  const res = await fetch(`${API_BASE}/lineage/runs`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch evolution runs: ${res.statusText}`);
  return res.json();
}

export async function fetchLineageGraph(runId?: string): Promise<LineageGraphResponse> {
  const url = runId
    ? `${API_BASE}/lineage/graph?run_id=${encodeURIComponent(runId)}`
    : `${API_BASE}/lineage/graph`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch lineage DAG: ${res.statusText}`);
  return res.json();
}


export interface Section62Metrics {
  total_orders: number;
  auto_decided_count: number;
  auto_decided_pct: number;
  auto_blocked_count: number;
  auto_approved_count: number;
  manual_review_count: number;
  manual_review_pct: number;
  auto_decided_precision: number;
  auto_decided_recall: number;
  auto_decided_net_savings_inr: number;
  review_queue_rto_concentration: number;
  review_queue_total_value_inr: number;
  full_system_net_savings_inr: number;
  methodological_notice: string;
}

export interface ReviewQueueResponse {
  status: string;
  total_in_queue: number;
  queue: Array<{
    review_id: number;
    order_id: string;
    risk_score: number;
    triggered_signals: Record<string, any>;
    status: string;
    created_at?: string;
  }>;
}

export async function fetchReviewMetrics(cohort?: string): Promise<Section62Metrics> {
  const url = cohort ? `${API_BASE}/review/metrics?cohort=${encodeURIComponent(cohort)}` : `${API_BASE}/review/metrics`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch review metrics: ${res.statusText}`);
  return res.json();
}

export async function fetchReviewQueue(): Promise<ReviewQueueResponse> {
  const res = await fetch(`${API_BASE}/review/queue`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch review queue: ${res.statusText}`);
  return res.json();
}

export async function fetchHypothesisDetails(hypothesisId: string): Promise<HypothesisDetails> {
  const res = await fetch(`${API_BASE}/lineage/hypothesis/${encodeURIComponent(hypothesisId)}`, {
    cache: 'no-store',
  });
  if (!res.ok) throw new Error(`Failed to fetch hypothesis details: ${res.statusText}`);
  return res.json();
}

export async function fetchMonitorStatus(): Promise<MonitorSnapshot> {
  const res = await fetch(`${API_BASE}/monitor/status`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch monitor status: ${res.statusText}`);
  return res.json();
}

export async function fetchMonitorHistory(limit = 60): Promise<TimeSeriesPoint[]> {
  const res = await fetch(`${API_BASE}/monitor/history?limit=${limit}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch monitor history: ${res.statusText}`);
  return res.json();
}

export interface BenchmarkSummaryResponse {
  status: string;
  production_headline_metrics: {
    dataset_name: string;
    operating_threshold: number;
    total_test_orders: number;
    auto_decided_net_savings_inr: number;
    auto_decided_pct: number;
    auto_blocked_count: number;
    auto_approved_count: number;
    manual_review_count: number;
    manual_review_pct: number;
    review_queue_rto_concentration: number;
    review_queue_risk_multiplier: number;
    auto_decided_precision: number;
    auto_decided_recall: number;
    full_system_net_savings_inr: number;
    methodological_notice: string;
  };
  ablation_matrix: {
    title?: string;
    total_test_orders?: number;
    models?: Record<string, any>;
    paired_bootstrap_b_vs_c_t070?: {
      resamples_b: number;
      net_savings: {
        point_delta_inr: number;
        ci_95_lower_inr: number;
        ci_95_upper_inr: number;
        p_value: number;
        statistically_significant: boolean;
        crosses_zero: boolean;
      };
      precision: {
        point_delta_pct: number;
        ci_95_lower_pct: number;
        ci_95_upper_pct: number;
        p_value: number;
        statistically_significant: boolean;
        crosses_zero: boolean;
      };
      recall: {
        point_delta_pct: number;
        ci_95_lower_pct: number;
        ci_95_upper_pct: number;
        p_value: number;
        statistically_significant: boolean;
        crosses_zero: boolean;
      };
      scientific_verdict: string;
    };
  };
  paired_bootstrap?: any;
}

export async function fetchBenchmarkSummary(): Promise<BenchmarkSummaryResponse> {
  const res = await fetch(`${API_BASE}/benchmark/summary`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch benchmark summary: ${res.statusText}`);
  return res.json();
}

export async function triggerTrafficSimulation(
  totalEvents = 30,
  spikeRate = 0.45,
  orderValueMean = 1250.0
): Promise<any> {
  const res = await fetch(`${API_BASE}/monitor/simulate-traffic`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      total_events: totalEvents,
      spike_rate: spikeRate,
      order_value_mean: orderValueMean,
    }),
  });
  if (!res.ok) throw new Error(`Traffic simulation failed: ${res.statusText}`);
  return res.json();
}

export interface DiscoveredCluster {
  cluster_id: string;
  cluster_name: string;
  signature_patterns: Record<string, any>;
  miss_volume: number;
  cohort_size: number;
  miss_percentage_of_cohort: number;
  statistical_lift: number;
  p_value: number;
  conjunction_depth: number;
  status: 'significant' | 'on_cooldown' | 'bypassed_surge';
  is_autonomous_discovery: boolean;
  generator_agenda: string;
  resulting_hypothesis?: {
    hypothesis_id: string;
    name: string;
    rule_code: string;
    gate_verdict: string;
    net_financial_delta_inr: number;
    precision: number;
    recall: number;
    true_positives: number;
    false_positives: number;
  } | null;
  cooldown_info: {
    cooldown_until_round: number;
    last_miss_count: number;
    surge_bypass_active: boolean;
  };
  representative_samples?: Array<Record<string, any>>;
}

export interface RejectedCandidate {
  cluster_name: string;
  signature_patterns: Record<string, any>;
  cohort_size: number;
  miss_count: number;
  lift: number;
  p_value: number;
  rejection_reason: string;
}

export interface ResidualMiningScanResponse {
  status: string;
  scan_metadata: {
    split_scanned: string;
    miner_mode: string;
    total_orders_analyzed: number;
    mature_orders_count: number;
    unmatured_orders_deferred: number;
    total_false_negatives: number;
    false_negative_rate: number;
    current_round: number;
    current_day_index: number;
    maturity_window_days: number;
    significance_alpha: number;
    timestamp: string;
  };
  discovered_clusters: DiscoveredCluster[];
  suppressed_clusters: any[];
  rejected_candidates: RejectedCandidate[];
}

export interface ClusterTimelineEvent {
  round: number;
  event: string;
  description: string;
  timestamp: string;
  status: string;
}

export interface ClusterHistoryResponse {
  cluster_id: string;
  cluster_name: string;
  discovery_type: string;
  first_discovered_round: number;
  current_status: string;
  total_scans_detected: number;
  peak_miss_volume: number;
  timeline: ClusterTimelineEvent[];
}

export async function fetchResidualMiningScan(
  split = 'training',
  mode = 'dynamic'
): Promise<ResidualMiningScanResponse> {
  const res = await fetch(
    `${API_BASE}/residual-mining/latest-scan?split=${split}&mode=${mode}`,
    { cache: 'no-store' }
  );
  if (!res.ok) throw new Error(`Failed to fetch residual mining scan: ${res.statusText}`);
  return res.json();
}

export async function fetchClusterHistory(clusterId: string): Promise<ClusterHistoryResponse> {
  const res = await fetch(
    `${API_BASE}/residual-mining/cluster-history/${encodeURIComponent(clusterId)}`,
    { cache: 'no-store' }
  );
  if (!res.ok) throw new Error(`Failed to fetch cluster history: ${res.statusText}`);
  return res.json();
}

export interface MatchedRuleDetail {
  rule_id: string;
  rule_name: string;
  rule_code: string;
}

export interface RuleEvaluationDetail {
  rule_id: string;
  rule_name: string;
  rule_code: string;
  is_matched: boolean;
}

export interface OrderTestCaseResponse {
  order_id: string;
  tier: 'easy' | 'medium' | 'hard';
  tier_label: string;
  tier_description: string;
  order_features: Record<string, any>;
  routing_decision: 'AUTO_APPROVE' | 'AUTO_BLOCK' | 'MANUAL_REVIEW';
  risk_score: number;
  is_flagged: boolean;
  matched_rules: MatchedRuleDetail[];
  evaluated_rules?: RuleEvaluationDetail[];
  ground_truth: {
    is_rto: number;
    actual_outcome: string;
  };
  outcome_classification: string;
  is_correct: boolean | null;
  verdict_badge: string;
  explanation?: string;
}


export interface ExplainRequest {
  order_id: string;
  tier: string;
  order_features: Record<string, any>;
  routing_decision: string;
  risk_score: number;
  matched_rules: Array<{ rule_id: string; rule_name: string; rule_code?: string }>;
  ground_truth: Record<string, any>;
  outcome_classification: string;
}

export interface ExplainResponse {
  order_id: string;
  explanation: string;
  model_used: string;
  source: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatbotAskRequest {
  message: string;
  session_id?: string;
  history?: ChatMessage[];
}

export interface ChatbotAskResponse {
  reply: string;
  is_refusal: boolean;
  model_used: string;
  tokens_estimated: number;
  source: string;
}

export async function fetchPlaygroundTestCase(tier = 'easy'): Promise<OrderTestCaseResponse> {
  const res = await fetch(`${API_BASE}/playground/generate?tier=${tier}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to generate playground test case: ${res.statusText}`);
  return res.json();
}

export async function explainPlaygroundDecision(payload: ExplainRequest): Promise<ExplainResponse> {
  const res = await fetch(`${API_BASE}/playground/explain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Failed to generate explanation: ${res.statusText}`);
  return res.json();
}

export async function askJudgeChatbot(payload: ChatbotAskRequest): Promise<ChatbotAskResponse> {
  const res = await fetch(`${API_BASE}/chatbot/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Failed to query judge chatbot: ${res.statusText}`);
  return res.json();
}

export async function streamJudgeChatbot(
  payload: ChatbotAskRequest,
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (err: any) => void
): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/chatbot/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      // Fall back to regular endpoint if stream endpoint encounters error
      const fallback = await askJudgeChatbot(payload);
      onToken(fallback.reply);
      onDone();
      return;
    }

    if (!res.body) {
      throw new Error('Response body is null');
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith('data:')) continue;

        const dataStr = trimmed.slice(5).trim();
        if (dataStr === '[DONE]') {
          onDone();
          return;
        }

        try {
          const parsed = JSON.parse(dataStr);
          if (parsed.token) {
            onToken(parsed.token);
          }
        } catch {
          // ignore non-json SSE lines
        }
      }
    }
    onDone();
  } catch (err) {
    onError(err);
  }
}

export interface LightGBMComparisonResponse {
  status: string;
  dataset_name: string;
  framing: string;
  evolved_rule_ensemble: {
    name: string;
    operating_threshold: number;
    precision: number;
    recall: number;
    true_positives: number;
    false_positives: number;
    net_financial_savings_inr: number;
    auto_decision_rate_pct: number;
    review_queue_rto_concentration: number;
    break_even_fp_aov_inr: number;
    break_even_precision_pct: number;
    catalog_gross_aov_inr: number;
    interpretability: string;
    adaptation_mode: string;
  };
  lightgbm_baseline: {
    name: string;
    operating_threshold: number;
    precision: number;
    recall: number;
    true_positives: number;
    false_positives: number;
    net_financial_savings_inr: number;
    training_split: string;
    interpretability: string;
    adaptation_mode: string;
  };
  mechanism_analysis: {
    title: string;
    points: string[];
  };
}

export async function fetchLightGBMComparison(): Promise<LightGBMComparisonResponse> {
  const res = await fetch(`${API_BASE}/benchmark/lightgbm-comparison`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch LightGBM comparison: ${res.statusText}`);
  return res.json();
}