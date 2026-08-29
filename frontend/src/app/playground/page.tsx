'use client';

import { useState, useEffect } from 'react';
import {
  FlaskConical,
  Sparkles,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Code2,
  RefreshCw,
  Zap,
  Info,
  ChevronRight,
  Sliders,
  DollarSign,
  UserCheck,
  Building,
  Clock,
  Layers,
  Send,
  Play,
  Check,
} from 'lucide-react';
import clsx from 'clsx';
import {
  fetchPlaygroundTestCase,
  explainPlaygroundDecision,
  OrderTestCaseResponse,
  ExplainResponse,
} from '@/lib/api';

export default function PlaygroundPage() {
  const [selectedTier, setSelectedTier] = useState<'easy' | 'medium' | 'hard'>('easy');
  const [currentTestCase, setCurrentTestCase] = useState<OrderTestCaseResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [isEvaluated, setIsEvaluated] = useState<boolean>(true);
  const [explaining, setExplaining] = useState<boolean>(false);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [explanationMeta, setExplanationMeta] = useState<{ model: string; source: string } | null>(null);

  const loadTestCase = async (tier: 'easy' | 'medium' | 'hard', autoEvaluate = true) => {
    setSelectedTier(tier);
    setLoading(true);
    setIsEvaluated(autoEvaluate);
    try {
      const data = await fetchPlaygroundTestCase(tier);
      setCurrentTestCase(data);
      setExplanation(data.explanation || null);
      setExplanationMeta({ model: 'gemini-3.6-flash', source: 'live' });
    } catch (err) {
      console.error('Failed to load transaction simulation:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunEvaluation = () => {
    setIsEvaluated(true);
  };

  const handleRegenerateExplanation = async () => {
    if (!currentTestCase) return;
    setExplaining(true);
    try {
      const res = await explainPlaygroundDecision({
        order_id: currentTestCase.order_id,
        tier: currentTestCase.tier,
        order_features: currentTestCase.order_features,
        routing_decision: currentTestCase.routing_decision,
        risk_score: currentTestCase.risk_score,
        matched_rules: currentTestCase.matched_rules,
        ground_truth: currentTestCase.ground_truth,
        outcome_classification: currentTestCase.outcome_classification,
      });
      setExplanation(res.explanation);
      setExplanationMeta({ model: res.model_used, source: res.source });
    } catch (err) {
      console.error('Failed to explain decision:', err);
    } finally {
      setExplaining(false);
    }
  };

  useEffect(() => {
    loadTestCase('easy', true);
  }, []);

  const tiers = [
    {
      id: 'easy' as const,
      name: 'Easy Tier',
      subtitle: 'Clear Fraud or Verified Buyer',
      badge: 'High Confidence',
      badgeClass: 'bg-emerald-100 text-emerald-800 border-emerald-200',
      borderHover: 'hover:border-emerald-300',
      activeBorder: 'border-emerald-500 ring-2 ring-emerald-100',
      desc: 'Simulates standard transactions: unambiguous high-confidence fraud attempts or clean verified buyers.',
    },
    {
      id: 'medium' as const,
      name: 'Medium Tier',
      subtitle: 'Borderline & Threshold Boundaries',
      badge: 'Marginal Risk',
      badgeClass: 'bg-amber-100 text-amber-800 border-amber-200',
      borderHover: 'hover:border-amber-300',
      activeBorder: 'border-amber-500 ring-2 ring-amber-100',
      desc: 'Simulates borderline checkout scenarios: intermediate risk signals scoring near threshold boundaries (0.35–0.70).',
    },
    {
      id: 'hard' as const,
      name: 'Hard Tier',
      subtitle: 'Deceptive Misses & FP Risks',
      badge: 'Adaptation Gap',
      badgeClass: 'bg-purple-100 text-purple-800 border-purple-200',
      borderHover: 'hover:border-purple-300',
      activeBorder: 'border-purple-500 ring-2 ring-purple-100',
      desc: 'Simulates sophisticated deceptive orders: subtle edge cases, newly emerging fraud variants, and false-positive margin risk scenarios.',
    },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">
              Interactive Defense Playground
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-100 text-indigo-700 border border-indigo-200 flex items-center gap-1 font-mono">
              <FlaskConical className="w-3.5 h-3.5" />
              Live Simulation
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Generate dynamic transaction simulations across risk difficulty tiers and evaluate real-time 3-way routing, rule execution, and AI explanations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => loadTestCase(selectedTier, true)}
            disabled={loading}
            className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs shadow-xs flex items-center gap-2 transition active:scale-95 disabled:opacity-50"
          >
            <RefreshCw className={clsx('w-3.5 h-3.5', loading && 'animate-spin')} />
            Generate New {selectedTier.toUpperCase()} Transaction
          </button>
        </div>
      </div>

      {/* Real-Time Simulation Engine Banner */}
      <div className="p-3.5 rounded-2xl bg-indigo-50/70 border border-indigo-200 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 text-indigo-900 font-medium">
          <Zap className="w-4 h-4 text-indigo-600 shrink-0" />
          <span>
            <strong>Simulation Engine:</strong> Dynamically generates realistic transaction payloads across buyer profiles to test live ensemble defense.
          </span>
        </div>
        <span className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-indigo-100 text-indigo-800 border border-indigo-200">
          Synthetic Transaction Generator
        </span>
      </div>

      {/* Difficulty Tier Selector Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {tiers.map((t) => {
          const isSelected = selectedTier === t.id;
          return (
            <div
              key={t.id}
              onClick={() => loadTestCase(t.id, true)}
              className={clsx(
                'p-6 rounded-2xl bg-white border transition-all duration-200 cursor-pointer relative shadow-xs flex flex-col justify-between group',
                t.borderHover,
                isSelected ? t.activeBorder : 'border-slate-200'
              )}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
                    Tier {t.id === 'easy' ? 'I' : t.id === 'medium' ? 'II' : 'III'}
                  </span>
                  <span className={clsx('text-[10px] font-bold px-2 py-0.5 rounded-full border', t.badgeClass)}>
                    {t.badge}
                  </span>
                </div>

                <div>
                  <h3 className="text-base font-bold text-slate-900 group-hover:text-indigo-600 transition">
                    {t.name}
                  </h3>
                  <p className="text-xs text-slate-500 font-medium mt-0.5">
                    {t.subtitle}
                  </p>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed">
                  {t.desc}
                </p>
              </div>

              <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs font-semibold text-indigo-600 group-hover:underline flex items-center gap-1">
                  Generate Scenario
                  <ChevronRight className="w-3.5 h-3.5" />
                </span>
                {isSelected && (
                  <span className="w-2 h-2 rounded-full bg-indigo-600 ring-4 ring-indigo-100" />
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Order Inspection Panel */}
      {loading ? (
        <div className="py-20 rounded-3xl bg-white border border-slate-200 flex flex-col items-center justify-center gap-3 text-slate-400 shadow-xs">
          <RefreshCw className="w-8 h-8 animate-spin text-indigo-600" />
          <p className="text-sm font-medium">Generating transaction payload & running AST evaluation...</p>
        </div>
      ) : currentTestCase ? (
        <div className="space-y-6">
          {/* Order Header Summary Banner */}
          <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-700 shrink-0 font-bold font-mono">
                #{currentTestCase.order_id.slice(-4)}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-lg font-bold text-slate-900 font-mono">
                    {currentTestCase.order_id}
                  </h2>
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                    Live Payload
                  </span>
                  <span className={clsx(
                    'text-[11px] font-bold px-2.5 py-0.5 rounded-full border',
                    currentTestCase.tier === 'easy' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                    currentTestCase.tier === 'medium' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                    'bg-purple-50 text-purple-700 border-purple-200'
                  )}>
                    {currentTestCase.tier_label}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  Simulated transaction evaluated against live ensemble under 3-way routing policy.
                </p>
              </div>
            </div>

            {/* Verdict Badge */}
            <div className="flex items-center gap-3">
              <div className={clsx(
                'px-4 py-2 rounded-xl border flex items-center gap-2 font-bold text-xs font-mono',
                currentTestCase.is_correct === true
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  : currentTestCase.is_correct === false
                  ? 'bg-rose-50 text-rose-800 border-rose-200'
                  : 'bg-amber-50 text-amber-800 border-amber-200'
              )}>
                {currentTestCase.is_correct === true ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                ) : currentTestCase.is_correct === false ? (
                  <XCircle className="w-4 h-4 text-rose-600" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                )}
                <span>{currentTestCase.verdict_badge}</span>
              </div>
            </div>
          </div>

          {/* Core Grid: Routing Decision & Order Features */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Column 1: 3-Way Routing Decision Card */}
            <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-5 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Routing Engine Decision
                  </span>
                  <Sliders className="w-4 h-4 text-slate-400" />
                </div>

                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                  <div className="text-xs text-slate-500">Assigned Routing Policy</div>
                  <div className="flex items-center gap-2">
                    <span className={clsx(
                      'text-sm font-black font-mono px-3 py-1 rounded-lg border',
                      currentTestCase.routing_decision === 'AUTO_BLOCK'
                        ? 'bg-rose-100 text-rose-800 border-rose-300'
                        : currentTestCase.routing_decision === 'AUTO_APPROVE'
                        ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                        : 'bg-amber-100 text-amber-800 border-amber-300'
                    )}>
                      {currentTestCase.routing_decision}
                    </span>
                  </div>
                </div>

                {/* Risk Score Gauge */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-500 font-medium">Composite Risk Score</span>
                    <strong className="font-mono font-bold text-slate-900">
                      {currentTestCase.risk_score.toFixed(4)}
                    </strong>
                  </div>
                  <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden relative border border-slate-200">
                    <div
                      className={clsx(
                        'h-full transition-all duration-500 rounded-full',
                        currentTestCase.risk_score >= 0.70
                          ? 'bg-rose-600'
                          : currentTestCase.risk_score >= 0.35
                          ? 'bg-amber-500'
                          : 'bg-emerald-500'
                      )}
                      style={{ width: `${Math.min(100, Math.max(5, currentTestCase.risk_score * 100))}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                    <span>0.0 (Auto-Approve)</span>
                    <span>0.35 (Review Cutoff)</span>
                    <span>0.70 (Auto-Block)</span>
                    <span>1.0</span>
                  </div>
                </div>

                {/* Ground Truth vs System */}
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                  <div className="text-xs text-slate-500">Transaction Ground Truth</div>
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-slate-900">
                      {currentTestCase.ground_truth.actual_outcome}
                    </span>
                    <span className={clsx(
                      'text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border',
                      currentTestCase.ground_truth.is_rto === 1
                        ? 'bg-rose-100 text-rose-800 border-rose-200'
                        : 'bg-emerald-100 text-emerald-800 border-emerald-200'
                    )}>
                      is_rto = {currentTestCase.ground_truth.is_rto}
                    </span>
                  </div>
                </div>
              </div>

              {/* Economic Impact Pill */}
              <div className="p-3.5 rounded-xl bg-slate-900 text-white text-xs space-y-1">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">
                  Unit Economic Impact
                </div>
                <div className="font-mono text-xs">
                  {currentTestCase.outcome_classification === 'CORRECT_BLOCK' && (
                    <span className="text-emerald-400 font-bold">+₹250.00 Avoided 3PL Logistics Loss</span>
                  )}
                  {currentTestCase.outcome_classification === 'CORRECT_APPROVE' && (
                    <span className="text-emerald-400 font-bold">₹0 Friction Loss (Seamless Checkout)</span>
                  )}
                  {currentTestCase.outcome_classification === 'FALSE_NEGATIVE_MISS' && (
                    <span className="text-rose-400 font-bold">-₹250.00 Realized RTO Logistics Loss</span>
                  )}
                  {currentTestCase.outcome_classification === 'FALSE_POSITIVE_INSULT' && (
                    <span className="text-rose-400 font-bold">
                      -₹{((currentTestCase.order_features.order_value || 1000) * 0.15).toFixed(2)} Lost Merchant Margin (15%)
                    </span>
                  )}
                  {currentTestCase.outcome_classification === 'BORDERLINE_REVIEW' && (
                    <span className="text-amber-400 font-bold">Routed to Human Queue (47.17% RTO Density)</span>
                  )}
                </div>
              </div>
            </div>

            {/* Column 2: Order Features Attributes */}
            <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Extracted Order Signals
                </span>
                <Layers className="w-4 h-4 text-slate-400" />
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 block font-sans">Order Value</span>
                  <strong className="text-slate-900 text-sm font-bold">
                    ₹{Number(currentTestCase.order_features.order_value || 0).toLocaleString()}
                  </strong>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 block font-sans">Payment Mode</span>
                  <strong className={clsx(
                    'text-sm font-bold',
                    currentTestCase.order_features.payment_mode === 'COD' ? 'text-amber-700' : 'text-emerald-700'
                  )}>
                    {currentTestCase.order_features.payment_mode || 'COD'}
                  </strong>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 block font-sans">Account Age</span>
                  <strong className="text-slate-900">
                    {currentTestCase.order_features.customer_account_age_days} days
                  </strong>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 block font-sans">Prior Orders</span>
                  <strong className="text-slate-900">
                    {currentTestCase.order_features.customer_prior_orders} orders
                  </strong>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 block font-sans">Pincode RTO Rate</span>
                  <strong className="text-slate-900">
                    {(Number(currentTestCase.order_features.pincode_rolling_rto_rate || 0.20) * 100).toFixed(1)}%
                  </strong>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 block font-sans">Promo Code Used</span>
                  <strong className="text-slate-900">
                    {currentTestCase.order_features.promo_code_used ? 'YES' : 'NO'}
                  </strong>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 block font-sans">Device Velocity (24h)</span>
                  <strong className="text-slate-900">
                    {currentTestCase.order_features.device_order_count_24h || 0} orders
                  </strong>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 block font-sans">Item Category</span>
                  <strong className="text-slate-900 truncate block">
                    {currentTestCase.order_features.item_category || 'general'}
                  </strong>
                </div>
              </div>
            </div>

            {/* Column 3: Matched & Evaluated Rules AST Code */}
            <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-4 flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Triggered & Evaluated Rules
                  </span>
                  <Code2 className="w-4 h-4 text-slate-400" />
                </div>

                {/* If rules matched, show matched rules */}
                {currentTestCase.matched_rules && currentTestCase.matched_rules.length > 0 ? (
                  <div className="space-y-3">
                    {currentTestCase.matched_rules.map((r, idx) => (
                      <div key={idx} className="p-3.5 rounded-2xl bg-slate-900 text-slate-200 text-xs font-mono space-y-2 border border-slate-800">
                        <div className="flex items-center justify-between text-[11px] text-indigo-400 font-bold border-b border-slate-800 pb-1.5">
                          <span>{r.rule_name || r.rule_id}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-950 text-rose-400 border border-rose-800/60 font-bold">
                            TRIGGERED · MATCHED
                          </span>
                        </div>
                        <pre className="text-[11px] text-emerald-300/90 whitespace-pre-wrap leading-relaxed overflow-x-auto">
                          {r.rule_code}
                        </pre>
                      </div>
                    ))}
                  </div>
                ) : currentTestCase.evaluated_rules && currentTestCase.evaluated_rules.length > 0 ? (
                  /* If no rules matched, display the active evaluated ensemble rules so it's never blank! */
                  <div className="space-y-3">
                    <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-600">
                      <strong>0 Rules Triggered:</strong> Active ensemble rules evaluated against payload (all conditions false):
                    </div>
                    {currentTestCase.evaluated_rules.slice(0, 2).map((r, idx) => (
                      <div key={idx} className="p-3 rounded-2xl bg-slate-900 text-slate-200 text-xs font-mono space-y-2 border border-slate-800 opacity-90">
                        <div className="flex items-center justify-between text-[11px] text-slate-300 font-bold border-b border-slate-800 pb-1.5">
                          <span>{r.rule_name || r.rule_id}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700 font-medium">
                            EVALUATED · NOT TRIGGERED
                          </span>
                        </div>
                        <pre className="text-[11px] text-slate-400 whitespace-pre-wrap leading-relaxed overflow-x-auto">
                          {r.rule_code}
                        </pre>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-6 rounded-2xl bg-slate-50 border border-slate-100 flex flex-col items-center justify-center text-center text-slate-400 space-y-2">
                    <CheckCircle2 className="w-6 h-6 text-emerald-500" />
                    <p className="text-xs font-medium text-slate-700">No fraud heuristic triggered.</p>
                    <span className="text-[11px] text-slate-500">
                      Evaluated under ambient baseline risk (<code className="font-mono">risk &lt; 0.35</code>).
                    </span>
                  </div>
                )}
              </div>

              <div className="text-[11px] text-slate-400 italic">
                * All rules execute inside a memory-capped, sandboxed Python AST runtime with zero eval() vulnerabilities.
              </div>
            </div>
          </div>

          {/* AI Explanation Agent Card */}
          <div className="p-6 rounded-3xl bg-gradient-to-br from-indigo-900 via-slate-900 to-indigo-950 text-white shadow-lg space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-indigo-600/30 border border-indigo-400/40 flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-indigo-300" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    Aegis Explanation Agent
                  </h3>
                  <span className="text-[10px] text-indigo-300 font-mono">
                    Grounded strictly in order features, matched rules, and cost model arithmetic
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleRegenerateExplanation}
                  disabled={explaining}
                  className="px-3.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white text-xs font-semibold flex items-center gap-1.5 transition active:scale-95 disabled:opacity-50"
                >
                  <RefreshCw className={clsx('w-3.5 h-3.5', explaining && 'animate-spin')} />
                  Regenerate Explanation
                </button>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-white/5 border border-white/10 text-sm leading-relaxed text-indigo-100">
              {explaining ? (
                <div className="py-4 flex items-center gap-3 text-indigo-300">
                  <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
                  <span className="text-xs">Generating grounded natural language explanation via Gemini LLM...</span>
                </div>
              ) : (
                <p className="font-medium">{explanation}</p>
              )}
            </div>

            {explanationMeta && (
              <div className="flex items-center justify-between text-[10px] text-indigo-400/80 font-mono">
                <span>Model: {explanationMeta.model}</span>
                <span>Source: {explanationMeta.source === 'llm' ? 'Live LLM Generation' : 'Grounded Decision Engine'}</span>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
