'use client';

import React, { useState, useEffect } from 'react';
import { 
  Scale, 
  Lock,
  Layers,
  Info,
  HelpCircle,
  BarChart3,
  Cpu,
  FileCode,
  AlertCircle
} from 'lucide-react';
import { 
  fetchBenchmarkSummary, 
  fetchLightGBMComparison, 
  BenchmarkSummaryResponse, 
  LightGBMComparisonResponse 
} from '@/lib/api';

export default function ShadowControlPage() {
  const [summary, setSummary] = useState<BenchmarkSummaryResponse | null>(null);
  const [lgbComparison, setLgbComparison] = useState<LightGBMComparisonResponse | null>(null);

  useEffect(() => {
    fetchBenchmarkSummary()
      .then((data) => setSummary(data))
      .catch((err) => console.error('Failed to load benchmark summary:', err));

    fetchLightGBMComparison()
      .then((data) => setLgbComparison(data))
      .catch((err) => console.error('Failed to load LightGBM comparison:', err));
  }, []);

  const models = summary?.ablation_matrix?.models;
  const modelA = models?.model_a_frozen_v1;
  const modelC = models?.model_c_shadow_control;
  const modelB = models?.model_b_drift_champion;
  const bootstrap = summary?.ablation_matrix?.paired_bootstrap_b_vs_c_t070;

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Top Header */}
      <div className="border-b border-slate-200 pb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700">
            <Scale className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
                Rounds-Matched Shadow Control & Ablation
              </h1>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200 font-mono font-bold">
                Section 4.7 Matrix
              </span>
            </div>
            <p className="text-sm text-slate-600 mt-1 max-w-4xl leading-relaxed">
              Scientific ablation isolating drift-adaptation from mere additional optimization rounds (compute scaling). 
              Evaluated on the untouched <span className="text-slate-900 font-mono font-bold">held_out_test.csv (2,641 orders, Days 76–89)</span>.
            </p>
          </div>
        </div>

        {/* Methodological Notice */}
        <div className="mt-4 p-4 rounded-2xl bg-slate-50 border border-slate-200 flex items-start gap-3 text-xs text-slate-700">
          <Info className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-slate-900">Single-Touch Held-Out Test Evaluation:</span>
            <p className="text-xs text-slate-600 leading-relaxed">
              All metrics shown below trace strictly to the single-touch benchmark run on the final test split at operating threshold <code className="text-slate-800 font-bold font-mono bg-white px-1.5 py-0.5 rounded border border-slate-200">T = 0.70</code>.
            </p>
          </div>
        </div>
      </div>

      {/* 1. 3-Way Model Comparison Cards (Equal Neutral Framing) */}
      <div>
        <div className="mb-4">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider font-mono">
            1. Mechanism Ablation: 3-Way Model Architecture Comparison
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Parallel evaluation of initial pre-drift rules vs. compute scaling vs. error-guided drift adaptation.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Card 1: Model A -- Frozen Baseline */}
          <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-5 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200 flex items-center gap-1 font-semibold">
                  <Lock className="w-3 h-3 text-slate-500" />
                  N = 3 Rounds (Pre-Drift)
                </span>
                <span className="text-xs text-slate-500 font-bold font-mono">
                  Model A
                </span>
              </div>

              <h3 className="text-base font-bold text-slate-900">
                Model A -- Frozen Baseline
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Frozen after 3 rounds of exploration on Days 0–55 pre-drift data only. Zero drift exposure.
              </p>
            </div>

            <div className="space-y-2 pt-2 border-t border-slate-100 font-mono text-xs">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Auto-Blocked (T=0.70):</span>
                <span className="text-slate-900 font-bold">
                  {modelA ? `${modelA.t_070.auto_blocked_count} orders` : <span className="inline-block h-3.5 w-16 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">True / False Positives:</span>
                <span className="text-slate-900 font-bold">
                  {modelA ? `${modelA.t_070.true_positives} TP / ${modelA.t_070.false_positives} FP` : <span className="inline-block h-3.5 w-20 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Auto Precision:</span>
                <span className="text-slate-900 font-bold">
                  {modelA ? `${(modelA.t_070.precision * 100).toFixed(2)}%` : <span className="inline-block h-3.5 w-14 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Review Queue Volume:</span>
                <span className="text-slate-900 font-bold">
                  {modelA ? `${modelA.t_070.manual_review_count} (${modelA.t_070.manual_review_pct}%)` : <span className="inline-block h-3.5 w-20 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-2 bg-slate-50 border border-slate-200 px-3 rounded-xl text-slate-900 font-bold">
                <span>Auto Net Savings:</span>
                <span>
                  {modelA ? `₹${modelA.t_070.auto_decided_net_savings_inr.toLocaleString()}` : <span className="inline-block h-3.5 w-16 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600">
              <div className="font-bold text-slate-800 mb-1 flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5 text-slate-500" />
                Pre-Drift Benchmark:
              </div>
              Captures baseline risk in historical pincodes but lacks shields against promotional velocity or off-hours shift.
            </div>
          </div>

          {/* Card 2: Model C -- Shadow Control */}
          <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-5 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200 flex items-center gap-1 font-semibold">
                  <Layers className="w-3 h-3 text-slate-500" />
                  N+K = 5 Rounds (Pre-Drift Only)
                </span>
                <span className="text-xs text-slate-500 font-bold font-mono">
                  Model C
                </span>
              </div>

              <h3 className="text-base font-bold text-slate-900">
                Model C -- Shadow Control
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Given K=2 extra rounds searching pre-drift data only (0% drift exposure). Tests compute scaling in isolation.
              </p>
            </div>

            <div className="space-y-2 pt-2 border-t border-slate-100 font-mono text-xs">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Auto-Blocked (T=0.70):</span>
                <span className="text-slate-900 font-bold">
                  {modelC ? `${modelC.t_070.auto_blocked_count} orders` : <span className="inline-block h-3.5 w-16 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">True / False Positives:</span>
                <span className="text-slate-900 font-bold">
                  {modelC ? `${modelC.t_070.true_positives} TP / ${modelC.t_070.false_positives} FP` : <span className="inline-block h-3.5 w-20 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Auto Precision:</span>
                <span className="text-slate-900 font-bold">
                  {modelC ? `${(modelC.t_070.precision * 100).toFixed(2)}%` : <span className="inline-block h-3.5 w-14 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Review Queue Volume:</span>
                <span className="text-slate-900 font-bold">
                  {modelC ? `${modelC.t_070.manual_review_count} (${modelC.t_070.manual_review_pct}%)` : <span className="inline-block h-3.5 w-20 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-2 bg-slate-50 border border-slate-200 px-3 rounded-xl text-slate-900 font-bold">
                <span>Auto Net Savings:</span>
                <span>
                  {modelC ? `₹${modelC.t_070.auto_decided_net_savings_inr.toLocaleString()}` : <span className="inline-block h-3.5 w-16 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600">
              <div className="font-bold text-slate-800 mb-1 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-slate-500" />
                Compute Scaling Trade-Off:
              </div>
              Extra compute discovers broad category heuristics, capturing volume but expanding the review queue to 6.06% of traffic.
            </div>
          </div>

          {/* Card 3: Model B -- Drift-Adapted */}
          <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-5 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200 flex items-center gap-1 font-semibold">
                  <Layers className="w-3 h-3 text-slate-500" />
                  N+K = 5 Rounds (Drift-Exposed)
                </span>
                <span className="text-xs text-slate-500 font-bold font-mono">
                  Model B
                </span>
              </div>

              <h3 className="text-base font-bold text-slate-900">
                Model B -- Drift-Adapted
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Given K=2 extra rounds with error feedback from Days 56–75 drift distribution.
              </p>
            </div>

            <div className="space-y-2 pt-2 border-t border-slate-100 font-mono text-xs">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Auto-Blocked (T=0.70):</span>
                <span className="text-slate-900 font-bold">
                  {modelB ? `${modelB.t_070.auto_blocked_count} orders` : <span className="inline-block h-3.5 w-16 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">True / False Positives:</span>
                <span className="text-slate-900 font-bold">
                  {modelB ? `${modelB.t_070.true_positives} TP / ${modelB.t_070.false_positives} FP` : <span className="inline-block h-3.5 w-20 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Auto Precision:</span>
                <span className="text-slate-900 font-bold">
                  {modelB ? `${(modelB.t_070.precision * 100).toFixed(2)}%` : <span className="inline-block h-3.5 w-14 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Review Queue Volume:</span>
                <span className="text-slate-900 font-bold">
                  {modelB ? `${modelB.t_070.manual_review_count} (${modelB.t_070.manual_review_pct}%)` : <span className="inline-block h-3.5 w-20 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-2 bg-slate-50 border border-slate-200 px-3 rounded-xl text-slate-900 font-bold">
                <span>Auto Net Savings:</span>
                <span>
                  {modelB ? `₹${modelB.t_070.auto_decided_net_savings_inr.toLocaleString()}` : <span className="inline-block h-3.5 w-16 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600">
              <div className="font-bold text-slate-800 mb-1 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-slate-500" />
                Drift Adaptation Mechanism:
              </div>
              Synthesizes targeted promo velocity shields, maintaining minimal review friction (2.01% queue).
            </div>
          </div>
        </div>
      </div>

      {/* 2. Paired Bootstrap Significance Panel (Unmissable, Directly Beneath Cards) */}
      <div className="p-6 rounded-2xl border border-slate-300 bg-white shadow-xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-slate-700" />
              Paired Bootstrap Significance Analysis (Model B vs. Model C at T=0.70, B=2,000 Resamples)
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Statistical significance audit testing whether Model B (drift-adapted) and Model C (shadow control) are distinguishable on the held-out test split.
            </p>
          </div>
          <span className="text-xs font-mono font-bold px-3 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
            {bootstrap ? `p = ${bootstrap.net_savings.p_value.toFixed(4)}` : <span className="inline-block h-3.5 w-12 bg-slate-200 animate-pulse rounded" />}
          </span>
        </div>

        {/* 3 Metric Confidence Intervals */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
          {/* Net Savings Delta */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
            <span className="text-slate-500 block text-[11px]">Net Savings Delta (B - C):</span>
            <div className="text-lg font-bold text-slate-900">
              {bootstrap ? `₹${bootstrap.net_savings.point_delta_inr.toLocaleString()}` : <span className="inline-block h-5 w-24 bg-slate-200 animate-pulse rounded" />}
            </div>
            <div className="text-[11px] text-slate-600">
              {bootstrap ? `95% CI: [₹${bootstrap.net_savings.ci_95_lower_inr.toLocaleString()}, +₹${bootstrap.net_savings.ci_95_upper_inr.toLocaleString()}]` : <span className="inline-block h-3 w-36 bg-slate-100 animate-pulse rounded" />}
            </div>
            <span className="inline-block text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-200 text-slate-800 border border-slate-300 mt-1">
              Crosses Zero (p = 0.1510)
            </span>
          </div>

          {/* Precision Delta */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
            <span className="text-slate-500 block text-[11px]">Precision Delta (B - C):</span>
            <div className="text-lg font-bold text-slate-900">
              {bootstrap ? `${bootstrap.precision.point_delta_pct.toFixed(2)}%` : <span className="inline-block h-5 w-16 bg-slate-200 animate-pulse rounded" />}
            </div>
            <div className="text-[11px] text-slate-600">
              {bootstrap ? `95% CI: [${bootstrap.precision.ci_95_lower_pct.toFixed(2)}%, +${bootstrap.precision.ci_95_upper_pct.toFixed(2)}%]` : <span className="inline-block h-3 w-36 bg-slate-100 animate-pulse rounded" />}
            </div>
            <span className="inline-block text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-200 text-slate-800 border border-slate-300 mt-1">
              Crosses Zero (p = 0.4300)
            </span>
          </div>

          {/* Recall Delta */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
            <span className="text-slate-500 block text-[11px]">Recall Delta (B - C):</span>
            <div className="text-lg font-bold text-slate-900">
              {bootstrap ? `${bootstrap.recall.point_delta_pct.toFixed(2)}%` : <span className="inline-block h-5 w-16 bg-slate-200 animate-pulse rounded" />}
            </div>
            <div className="text-[11px] text-slate-600">
              {bootstrap ? `95% CI: [${bootstrap.recall.ci_95_lower_pct.toFixed(2)}%, +${bootstrap.recall.ci_95_upper_pct.toFixed(2)}%]` : <span className="inline-block h-3 w-36 bg-slate-100 animate-pulse rounded" />}
            </div>
            <span className="inline-block text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-200 text-slate-800 border border-slate-300 mt-1">
              Crosses Zero (p = 0.1170)
            </span>
          </div>
        </div>

        {/* Plain-Language Honesty Verdict */}
        <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 text-xs space-y-2 text-slate-800">
          <div className="font-bold text-slate-900 flex items-center gap-1.5">
            <HelpCircle className="w-4 h-4 text-slate-600" />
            Plain-Language Statistical Verdict:
          </div>
          <p className="leading-relaxed">
            <strong>Not statistically distinguishable at production threshold T=0.70:</strong> Point estimate is ₹-1,928.64 with 95% bootstrap confidence interval [₹-4,721.01, +₹622.37]. Because the confidence interval crosses zero (p = 0.1510), the data at T=0.70 cannot statistically resolve in favor of either drift adaptation or compute scaling alone.
          </p>
          <p className="text-[11px] text-slate-600 pt-1 border-t border-slate-200">
            <em>Secondary Observation (T=0.75, directional only -- not tested for statistical significance):</em> Under conservative thresholding (T=0.75), Model B achieves 70.00% precision vs 54.05% for Model C with reduced manual review overhead (3.56% vs 7.04%), indicating directional operational focus under tighter decision boundaries.
          </p>
        </div>
      </div>

      {/* 3. Section 4.8 LightGBM Baseline Comparison (Neutral Framing) */}
      <div className="space-y-5 pt-2">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider font-mono">
              2. Section 4.8 GBDT Baseline Comparison
            </h2>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200 font-mono">
              Interpretable AST Rules vs. GBDT
            </span>
          </div>
          <p className="text-xs text-slate-600 mt-1">
            <strong>Framing:</strong> Trade-off is interpretability and self-correction without retraining vs a raw-accuracy baseline.
          </p>
        </div>

        {/* Side-by-Side Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Card A: Evolved Rule Ensemble */}
          <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-5 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200 flex items-center gap-1 font-semibold">
                  <FileCode className="w-3.5 h-3.5 text-slate-600" />
                  Self-Evolving AST Ensemble
                </span>
                <span className="text-xs text-slate-500 font-bold font-mono">
                  Aegis Engine (T=0.70)
                </span>
              </div>

              <h3 className="text-base font-bold text-slate-900">
                Evolved Rule Ensemble
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Autonomous ensemble of verified Python AST Boolean rules synthesized via Generator-Reflector loops.
              </p>
            </div>

            <div className="space-y-2 pt-2 border-t border-slate-100 font-mono text-xs">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Evaluation Split:</span>
                <span className="text-slate-900 font-bold">Held-Out Test (2,641 Orders)</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Auto-Blocked (T=0.70):</span>
                <span className="text-slate-900 font-bold">
                  {lgbComparison ? `${lgbComparison.evolved_rule_ensemble.true_positives + lgbComparison.evolved_rule_ensemble.false_positives} (19 TP / 32 FP)` : <span className="inline-block h-3.5 w-24 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Auto Precision:</span>
                <span className="text-slate-900 font-bold">
                  {lgbComparison ? `${(lgbComparison.evolved_rule_ensemble.precision * 100).toFixed(2)}%` : <span className="inline-block h-3.5 w-14 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Auto Recall:</span>
                <span className="text-slate-900 font-bold">
                  {lgbComparison ? `${(lgbComparison.evolved_rule_ensemble.recall * 100).toFixed(2)}%` : <span className="inline-block h-3.5 w-14 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Auto-Decision Rate:</span>
                <span className="text-slate-900 font-bold">
                  {lgbComparison ? `${lgbComparison.evolved_rule_ensemble.auto_decision_rate_pct.toFixed(2)}%` : <span className="inline-block h-3.5 w-14 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-2 bg-slate-50 border border-slate-200 px-3 rounded-xl text-slate-900 font-bold">
                <span>Net Financial Savings:</span>
                <span>
                  {lgbComparison ? `+₹${lgbComparison.evolved_rule_ensemble.net_financial_savings_inr.toLocaleString()}` : <span className="inline-block h-3.5 w-20 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 space-y-1">
              <div className="font-bold text-slate-800 flex items-center gap-1.5">
                <FileCode className="w-3.5 h-3.5 text-slate-600" />
                Operational Characteristic:
              </div>
              <p>100% transparent logic. Conservative execution avoids false-positive margin penalties under drift (+₹2,458.91).</p>
            </div>
          </div>

          {/* Card B: LightGBM Baseline */}
          <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-5 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200 flex items-center gap-1 font-semibold">
                  <Cpu className="w-3.5 h-3.5 text-slate-600" />
                  Standard GBDT Classifier
                </span>
                <span className="text-xs text-slate-500 font-bold font-mono">
                  Section 4.8 GBDT
                </span>
              </div>

              <h3 className="text-base font-bold text-slate-900">
                LightGBM Baseline
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Gradient boosted decision tree (200 estimators) trained once on pre-drift data (Days 0–55) with cost-tuned threshold.
              </p>
            </div>

            <div className="space-y-2 pt-2 border-t border-slate-100 font-mono text-xs">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Evaluation Split:</span>
                <span className="text-slate-900 font-bold">Held-Out Test (2,641 Orders)</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Auto-Blocked (Tuned T=0.65):</span>
                <span className="text-slate-900 font-bold">
                  {lgbComparison ? `${lgbComparison.lightgbm_baseline.true_positives + lgbComparison.lightgbm_baseline.false_positives} (118 TP / 113 FP)` : <span className="inline-block h-3.5 w-24 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Precision (Higher Raw Stat):</span>
                <span className="text-slate-900 font-bold">
                  {lgbComparison ? `${(lgbComparison.lightgbm_baseline.precision * 100).toFixed(2)}%` : <span className="inline-block h-3.5 w-14 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Recall (Higher Raw Stat):</span>
                <span className="text-slate-900 font-bold">
                  {lgbComparison ? `${(lgbComparison.lightgbm_baseline.recall * 100).toFixed(2)}%` : <span className="inline-block h-3.5 w-14 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Training Split:</span>
                <span className="text-slate-900 font-bold">orders_train (Trained Once)</span>
              </div>
              <div className="flex justify-between py-2 bg-slate-50 border border-slate-200 px-3 rounded-xl text-slate-900 font-bold">
                <span>Net Financial Savings:</span>
                <span>
                  {lgbComparison ? `-₹${Math.abs(lgbComparison.lightgbm_baseline.net_financial_savings_inr).toLocaleString()}` : <span className="inline-block h-3.5 w-20 bg-slate-200 animate-pulse rounded" />}
                </span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 space-y-1">
              <div className="font-bold text-slate-800 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-slate-600" />
                Operational Characteristic:
              </div>
              <p>High statistical representation capacity across 13 raw features. Higher raw precision/recall, but opaque 200-tree model.</p>
            </div>
          </div>
        </div>

        {/* Mechanism Analysis Explanatory Card */}
        <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-xs">
            <AlertCircle className="w-4 h-4 text-slate-600" />
            <span>Why GBDT's Higher Raw Coverage Does Not Translate to Positive Net Savings Under Drift</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-600">
            <div className="p-3.5 rounded-xl bg-white border border-slate-200 space-y-1">
              <span className="font-bold text-slate-900 block">1. Pre-Drift Threshold Calibration Breakdown</span>
              <p className="leading-relaxed">
                GBDT's threshold was tuned on pre-drift data where high precision (76.11%) justified high flag volume. Under post-drift shift, its static decision boundary flags 113 false positives on high-ticket shifted orders (averaging ₹1,970/order), generating ₹33,441.66 in margin penalties that exceed its ₹29,500 logistics savings.
              </p>
            </div>
            <div className="p-3.5 rounded-xl bg-white border border-slate-200 space-y-1">
              <span className="font-bold text-slate-900 block">2. Precision Break-Even Calibration</span>
              <p className="leading-relaxed">
                Blocking an RTO saves ₹250. Wrongly blocking a customer costs 15% of order value. At mean FP order value ₹477.31 (₹71.60 cost), break-even precision is 22.26% (at catalog gross AOV ₹841, break-even is 33.53%). Aegis's conservative 37.25% precision at T=0.70 exceeds both hurdles.
              </p>
            </div>
            <div className="p-3.5 rounded-xl bg-white border border-slate-200 space-y-1">
              <span className="font-bold text-slate-900 block">3. Interpretability & Autonomous Maintenance</span>
              <p className="leading-relaxed">
                LightGBM provides higher raw statistical coverage as an unconstrained ML model. Aegis trades off peak unconstrained recall for 100% auditable AST rules that self-correct via residual mining without continuous full-model retraining pipelines.
              </p>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}