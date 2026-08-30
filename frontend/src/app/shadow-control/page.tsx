'use client';

import React, { useState, useEffect } from 'react';
import { 
  Scale, 
  Info,
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
import { LifecycleBarChart } from '@/components/charts/LifecycleBarChart';
import { FinancialOutcomeMatrix } from '@/components/charts/FinancialOutcomeMatrix';
import { TrajectoryLineChart } from '@/components/charts/TrajectoryLineChart';

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

  return (
    <div className="space-y-10 animate-fade-in pb-12">
      {/* Top Header */}
      <div className="border-b border-slate-200 pb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-700 shadow-xs">
            <Scale className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
                Ablation Matrix & Evolutionary Trajectory
              </h1>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 font-mono font-bold">
                Section 4.7 & 4.8
              </span>
            </div>
            <p className="text-sm text-slate-600 mt-1 max-w-4xl leading-relaxed">
              Tracking normalized unit economics across the 3-stage evolutionary lifecycle (Genesis $\to$ Drift Collapse $\to$ Autonomous Evolved Recovery) and validating against industry GBDT baselines.
            </p>
          </div>
        </div>

        {/* Methodological Notice */}
        <div className="mt-4 p-4 rounded-2xl bg-slate-50 border border-slate-200 flex items-start gap-3 text-xs text-slate-700">
          <Info className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-slate-900">Single-Touch Held-Out Test Evaluation:</span>
            <p className="text-xs text-slate-600 leading-relaxed">
              All production metrics trace strictly to the single-touch benchmark run on the locked test split (<code className="text-slate-800 font-bold font-mono bg-white px-1.5 py-0.5 rounded border border-slate-200">held_out_test.csv, 2,641 orders</code>) at operating threshold <code className="text-slate-800 font-bold font-mono bg-white px-1.5 py-0.5 rounded border border-slate-200">T = 0.70</code>.
            </p>
          </div>
        </div>
      </div>

      {/* 1. 3-Stage Evolutionary Lifecycle Chart (Normalized ROI & Savings per 1k) */}
      <div>
        <div className="mb-4">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider font-mono">
            1. Evolutionary Lifecycle & Normalized Unit Economics
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Apples-to-apples performance progression across Genesis baseline, drift shock, and autonomous champion adaptation.
          </p>
        </div>

        <LifecycleBarChart />
      </div>

      {/* 2. Financial 3-Way Outcome Matrix */}
      <div>
        <div className="mb-4">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider font-mono">
            2. Production 3-Way Policy Routing & Financial Balance
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Cost-weighted outcome breakdown across Auto-Block (High Risk), Review Queue (Ambiguous), and Auto-Approve (Clean).
          </p>
        </div>

        <FinancialOutcomeMatrix />
      </div>

      {/* 3. Drift Shock & Recovery Trajectory Curve */}
      <div>
        <div className="mb-4">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider font-mono">
            3. Chronological Drift Shock & Autonomous Recovery Curve
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Visualizing the +246.16% recovery lift generated when the Residual Miner clustered unflagged drift patterns.
          </p>
        </div>

        <TrajectoryLineChart />
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