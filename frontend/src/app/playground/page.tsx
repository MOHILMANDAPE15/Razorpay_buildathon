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
  Code2,
  RefreshCw,
  Zap,
  Sliders,
  Layers,
  History,
  Check,
  ArrowRight,
  TrendingUp,
  RotateCcw,
} from 'lucide-react';
import clsx from 'clsx';
import {
  fetchPlaygroundTestCase,
  explainPlaygroundDecision,
  OrderTestCaseResponse,
} from '@/lib/api';

export default function PlaygroundPage() {
  const [currentTestCase, setCurrentTestCase] = useState<OrderTestCaseResponse | null>(null);
  const [historyList, setHistoryList] = useState<OrderTestCaseResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [explaining, setExplaining] = useState<boolean>(false);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [explanationMeta, setExplanationMeta] = useState<{ model: string; source: string } | null>(null);

  const handleGenerateTestCase = async () => {
    setLoading(true);
    try {
      const data = await fetchPlaygroundTestCase();
      setCurrentTestCase(data);
      setHistoryList((prev) => [data, ...prev.slice(0, 19)]); // Keep last 20 cases
      setExplanation(data.explanation || null);
      setExplanationMeta({ model: 'gemini-3.6-flash', source: 'live' });
    } catch (err) {
      console.error('Failed to generate validation test case:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectHistoryItem = (item: OrderTestCaseResponse) => {
    setCurrentTestCase(item);
    setExplanation(item.explanation || null);
    setExplanationMeta({ model: 'gemini-3.6-flash', source: 'cached' });
  };

  const handleClearHistory = () => {
    if (currentTestCase) {
      setHistoryList([currentTestCase]);
    } else {
      setHistoryList([]);
    }
  };

  const handleRegenerateExplanation = async () => {
    if (!currentTestCase) return;
    setExplaining(true);
    try {
      const res = await explainPlaygroundDecision({
        order_id: currentTestCase.order_id,
        classification: currentTestCase.classification,
        classification_reason: currentTestCase.classification_reason,
        order_features: currentTestCase.order_features,
        routing_decision: currentTestCase.routing_decision,
        risk_score: currentTestCase.risk_score,
        matched_rules: currentTestCase.matched_rules,
        ground_truth: currentTestCase.ground_truth,
        outcome_classification: currentTestCase.outcome_classification,
        tier: currentTestCase.tier,
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
    handleGenerateTestCase();
  }, []);

  // Compute live session stats
  const totalDrawn = historyList.length;
  const clearPatternCount = historyList.filter((c) => c.classification === 'Clear pattern').length;
  const borderlineCount = historyList.filter((c) => c.classification === 'Borderline').length;
  const adaptationGapCount = historyList.filter((c) => c.classification === 'Adaptation gap').length;

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
              Live Random Validation Draw
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Draw genuinely random transaction payloads from the full validation split to observe honest empirical distribution, 3-way routing, and post-hoc classification.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleGenerateTestCase}
            disabled={loading}
            className="px-5 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-700 active:scale-95 text-white font-bold text-sm shadow-md shadow-indigo-200 flex items-center gap-2.5 transition disabled:opacity-50 cursor-pointer"
          >
            <RefreshCw className={clsx('w-4 h-4', loading && 'animate-spin')} />
            <span>Generate Test Case</span>
          </button>
        </div>
      </div>

      {/* Split-Provenance Guarantee Banner */}
      <div className="p-4 rounded-2xl bg-slate-900 text-slate-200 border border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs shadow-xs">
        <div className="flex items-center gap-2.5">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>
            <strong className="text-white">Validation Split Provenance:</strong> Sampling uniformly from 3,885 orders in Days 56–75. Zero leakage to held-out test split (Days 76–90). No pre-bucketed pools.
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800">
            Split: Validation (Non-Held-Out)
          </span>
          <span className="text-[10px] font-mono text-slate-400">
            Pool Size: 3,885 orders
          </span>
        </div>
      </div>

      {/* Primary Action Hero & Session Distribution Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Hero Generator Card */}
        <div className="lg:col-span-7 p-6 rounded-3xl bg-gradient-to-br from-indigo-50/80 via-white to-purple-50/50 border border-indigo-100 shadow-xs flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-indigo-700 font-bold text-xs uppercase tracking-wider font-mono">
              <Zap className="w-3.5 h-3.5" />
              Empirical Validation Pool Sampler
            </div>
            <h2 className="text-xl font-black text-slate-900">
              Uniform Random Validation Sampling
            </h2>
            <p className="text-xs text-slate-600 leading-relaxed">
              Click to pull an authentic transaction from the validation split. The production frozen ensemble executes 3-way routing, and the system explains the result <strong>post-hoc</strong> based on actual risk score cutoffs, threshold distances, and ground truth.
            </p>
          </div>

          <div className="pt-3 flex flex-wrap items-center gap-3">
            <button
              onClick={handleGenerateTestCase}
              disabled={loading}
              className="px-6 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-700 active:scale-95 text-white font-bold text-sm shadow-md shadow-indigo-200 flex items-center gap-2 transition disabled:opacity-50 cursor-pointer"
            >
              <RefreshCw className={clsx('w-4 h-4', loading && 'animate-spin')} />
              <span>{loading ? 'Sampling Validation Pool...' : 'Draw Random Order'}</span>
            </button>

            <span className="text-xs text-slate-500 flex items-center gap-1 font-medium">
              <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
              Post-hoc classified into Clear, Borderline, or Gap
            </span>
          </div>
        </div>

        {/* Live Session Distribution History Card */}
        <div className="lg:col-span-5 p-6 rounded-3xl bg-white border border-slate-200 shadow-xs flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-700 font-bold text-xs uppercase tracking-wider font-mono">
              <TrendingUp className="w-3.5 h-3.5 text-indigo-600" />
              Session Empirical Distribution
            </div>
            {totalDrawn > 1 && (
              <button
                onClick={handleClearHistory}
                className="text-[11px] text-slate-400 hover:text-slate-600 flex items-center gap-1 cursor-pointer transition"
                title="Reset session history counter"
              >
                <RotateCcw className="w-3 h-3" />
                Reset Tally
              </button>
            )}
          </div>

          <div className="space-y-2.5">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
              <span>{totalDrawn} Drawn in Session:</span>
              <span className="font-mono text-slate-500">
                {totalDrawn > 0
                  ? `${clearPatternCount} clear · ${borderlineCount} review · ${adaptationGapCount} gap`
                  : 'Awaiting first draw'}
              </span>
            </div>

            {/* Distribution Stacked Bar */}
            <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden flex border border-slate-200">
              {totalDrawn > 0 ? (
                <>
                  <div
                    className="h-full bg-emerald-500 transition-all duration-300"
                    style={{ width: `${(clearPatternCount / totalDrawn) * 100}%` }}
                    title={`Clear Pattern: ${clearPatternCount} (${((clearPatternCount / totalDrawn) * 100).toFixed(0)}%)`}
                  />
                  <div
                    className="h-full bg-amber-500 transition-all duration-300"
                    style={{ width: `${(borderlineCount / totalDrawn) * 100}%` }}
                    title={`Borderline: ${borderlineCount} (${((borderlineCount / totalDrawn) * 100).toFixed(0)}%)`}
                  />
                  <div
                    className="h-full bg-purple-500 transition-all duration-300"
                    style={{ width: `${(adaptationGapCount / totalDrawn) * 100}%` }}
                    title={`Adaptation Gap: ${adaptationGapCount} (${((adaptationGapCount / totalDrawn) * 100).toFixed(0)}%)`}
                  />
                </>
              ) : (
                <div className="h-full w-full bg-slate-200" />
              )}
            </div>

            {/* Breakdown Badges */}
            <div className="grid grid-cols-3 gap-2 pt-1">
              <div className="p-2 rounded-xl bg-emerald-50 border border-emerald-200 text-center">
                <span className="text-[10px] text-emerald-700 font-bold block uppercase">Clear Pattern</span>
                <span className="text-xs font-mono font-black text-emerald-900">
                  {clearPatternCount} ({totalDrawn ? ((clearPatternCount / totalDrawn) * 100).toFixed(0) : 0}%)
                </span>
              </div>

              <div className="p-2 rounded-xl bg-amber-50 border border-amber-200 text-center">
                <span className="text-[10px] text-amber-700 font-bold block uppercase">Borderline</span>
                <span className="text-xs font-mono font-black text-amber-900">
                  {borderlineCount} ({totalDrawn ? ((borderlineCount / totalDrawn) * 100).toFixed(0) : 0}%)
                </span>
              </div>

              <div className="p-2 rounded-xl bg-purple-50 border border-purple-200 text-center">
                <span className="text-[10px] text-purple-700 font-bold block uppercase">Adaptation Gap</span>
                <span className="text-xs font-mono font-black text-purple-900">
                  {adaptationGapCount} ({totalDrawn ? ((adaptationGapCount / totalDrawn) * 100).toFixed(0) : 0}%)
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Session History Trail Pill List */}
      {historyList.length > 1 && (
        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between text-xs font-bold text-slate-700">
            <span className="flex items-center gap-1.5 font-mono">
              <History className="w-3.5 h-3.5 text-indigo-600" />
              Recent Draws in Session (Click to inspect):
            </span>
            <span className="text-[11px] font-normal text-slate-400">
              Showing last {historyList.length} random draws
            </span>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-1 pt-1">
            {historyList.map((item, idx) => {
              const isSelected = currentTestCase?.order_id === item.order_id;
              return (
                <button
                  key={`${item.order_id}-${idx}`}
                  onClick={() => handleSelectHistoryItem(item)}
                  className={clsx(
                    'px-3 py-1.5 rounded-xl border text-xs font-mono shrink-0 flex items-center gap-2 transition cursor-pointer',
                    isSelected
                      ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
                      : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                  )}
                >
                  <span className="font-bold">#{item.order_id.slice(-4)}</span>
                  <span
                    className={clsx(
                      'text-[9px] px-1.5 py-0.2 rounded-md font-sans font-bold',
                      item.classification === 'Clear pattern'
                        ? 'bg-emerald-100 text-emerald-800'
                        : item.classification === 'Borderline'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-purple-100 text-purple-800'
                    )}
                  >
                    {item.classification}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    r={item.risk_score.toFixed(2)}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Main Order Inspection Panel */}
      {loading ? (
        <div className="py-20 rounded-3xl bg-white border border-slate-200 flex flex-col items-center justify-center gap-3 text-slate-400 shadow-xs">
          <RefreshCw className="w-8 h-8 animate-spin text-indigo-600" />
          <p className="text-sm font-medium">Drawing random validation order & executing AST evaluation...</p>
        </div>
      ) : currentTestCase ? (
        <div className="space-y-6">
          {/* Post-Hoc Classification Header Banner */}
          <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-700 shrink-0 font-bold font-mono">
                  #{currentTestCase.order_id.slice(-4)}
                </div>
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <h2 className="text-lg font-bold text-slate-900 font-mono">
                      {currentTestCase.order_id}
                    </h2>
                    <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                      Validation Split
                    </span>

                    {/* Prominent Post-Hoc Classification Badge */}
                    <span
                      className={clsx(
                        'text-xs font-black px-3 py-1 rounded-full border flex items-center gap-1.5 uppercase font-mono tracking-wide',
                        currentTestCase.classification === 'Clear pattern' &&
                          'bg-emerald-50 text-emerald-800 border-emerald-300 ring-2 ring-emerald-100',
                        currentTestCase.classification === 'Borderline' &&
                          'bg-amber-50 text-amber-800 border-amber-300 ring-2 ring-amber-100',
                        currentTestCase.classification === 'Adaptation gap' &&
                          'bg-purple-50 text-purple-800 border-purple-300 ring-2 ring-purple-100'
                      )}
                    >
                      {currentTestCase.classification === 'Clear pattern' && <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />}
                      {currentTestCase.classification === 'Borderline' && <Sliders className="w-3.5 h-3.5 text-amber-600" />}
                      {currentTestCase.classification === 'Adaptation gap' && <ShieldAlert className="w-3.5 h-3.5 text-purple-600" />}
                      {currentTestCase.classification}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Sampled from the non-held-out validation pool and classified post-hoc based on score cutoffs and ground truth.
                  </p>
                </div>
              </div>

              {/* Verdict Badge */}
              <div className="flex items-center gap-3">
                <div
                  className={clsx(
                    'px-4 py-2 rounded-xl border flex items-center gap-2 font-bold text-xs font-mono',
                    currentTestCase.is_correct === true
                      ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                      : currentTestCase.is_correct === false
                      ? 'bg-rose-50 text-rose-800 border-rose-200'
                      : 'bg-amber-50 text-amber-800 border-amber-200'
                  )}
                >
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

            {/* Post-Hoc Classification Reasoning Callout */}
            <div
              className={clsx(
                'p-4 rounded-2xl border text-xs leading-relaxed flex items-start gap-3',
                currentTestCase.classification === 'Clear pattern' && 'bg-emerald-50/60 border-emerald-200 text-emerald-950',
                currentTestCase.classification === 'Borderline' && 'bg-amber-50/60 border-amber-200 text-amber-950',
                currentTestCase.classification === 'Adaptation gap' && 'bg-purple-50/60 border-purple-200 text-purple-950'
              )}
            >
              <Sparkles
                className={clsx(
                  'w-4 h-4 shrink-0 mt-0.5',
                  currentTestCase.classification === 'Clear pattern' && 'text-emerald-600',
                  currentTestCase.classification === 'Borderline' && 'text-amber-600',
                  currentTestCase.classification === 'Adaptation gap' && 'text-purple-600'
                )}
              />
              <div>
                <strong className="block text-xs font-bold mb-0.5">
                  Post-Hoc Classification Rationale:
                </strong>
                <span>{currentTestCase.classification_reason}</span>
              </div>
            </div>
          </div>

          {/* Core Grid: Routing Decision & Order Features */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Column 1: 3-Way Routing Decision Card */}
            <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-5 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
                    Routing Engine Decision
                  </span>
                  <Sliders className="w-4 h-4 text-slate-400" />
                </div>

                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                  <div className="text-xs text-slate-500 font-medium">Assigned Routing Policy</div>
                  <div className="flex items-center gap-2">
                    <span
                      className={clsx(
                        'text-sm font-black font-mono px-3 py-1 rounded-lg border',
                        currentTestCase.routing_decision === 'AUTO_BLOCK'
                          ? 'bg-rose-100 text-rose-800 border-rose-300'
                          : currentTestCase.routing_decision === 'AUTO_APPROVE'
                          ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                          : 'bg-amber-100 text-amber-800 border-amber-300'
                      )}
                    >
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
                  <div className="text-xs text-slate-500 font-medium">Transaction Ground Truth</div>
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-slate-900">
                      {currentTestCase.ground_truth.actual_outcome}
                    </span>
                    <span
                      className={clsx(
                        'text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border',
                        currentTestCase.ground_truth.is_rto === 1
                          ? 'bg-rose-100 text-rose-800 border-rose-200'
                          : 'bg-emerald-100 text-emerald-800 border-emerald-200'
                      )}
                    >
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
                    <span className="text-amber-400 font-bold">Routed to Human Review (Zero Auto Insult)</span>
                  )}
                </div>
              </div>
            </div>

            {/* Column 2: Order Features Attributes */}
            <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
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
                  <strong
                    className={clsx(
                      'text-sm font-bold',
                      currentTestCase.order_features.payment_mode === 'COD' ? 'text-amber-700' : 'text-emerald-700'
                    )}
                  >
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
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
                    Triggered & Evaluated Rules
                  </span>
                  <Code2 className="w-4 h-4 text-slate-400" />
                </div>

                {/* If rules matched, show matched rules */}
                {currentTestCase.matched_rules && currentTestCase.matched_rules.length > 0 ? (
                  <div className="space-y-3">
                    {currentTestCase.matched_rules.map((r, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-2xl bg-slate-900 text-slate-200 text-xs font-mono space-y-2 border border-slate-800"
                      >
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
                  /* If no rules matched, display evaluated active ensemble rules */
                  <div className="space-y-3">
                    <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-600">
                      <strong>0 Rules Triggered:</strong> Evaluated against active ensemble (all conditions false):
                    </div>
                    {currentTestCase.evaluated_rules.slice(0, 2).map((r, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-2xl bg-slate-900 text-slate-200 text-xs font-mono space-y-2 border border-slate-800 opacity-90"
                      >
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

              <div className="text-[11px] text-slate-400 italic font-sans">
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
                    Grounded strictly in order features, post-hoc classification, and cost model arithmetic
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleRegenerateExplanation}
                  disabled={explaining}
                  className="px-3.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white text-xs font-semibold flex items-center gap-1.5 transition active:scale-95 disabled:opacity-50 cursor-pointer"
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
                <span>Source: {explanationMeta.source === 'llm' ? 'Live Gemini LLM Generation' : 'Grounded Decision Engine'}</span>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
