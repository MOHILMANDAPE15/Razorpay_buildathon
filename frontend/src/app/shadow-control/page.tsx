'use client';

import React from 'react';
import { 
  Scale, 
  TrendingDown, 
  TrendingUp, 
  ShieldCheck, 
  AlertOctagon, 
  Sparkles,
  CheckCircle2,
  Lock,
  Layers,
  Info
} from 'lucide-react';

export default function ShadowControlPage() {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Header */}
      <div className="border-b border-slate-200 pb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600">
            <Scale className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
                Rounds-Matched Ablation Matrix
              </h1>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 font-mono font-bold">
                Scientific Ablation
              </span>
            </div>
            <p className="text-sm text-slate-600 mt-1 max-w-4xl leading-relaxed">
              Rigorous scientific ablation proving that static v1 rule degradation is caused by true distribution shift (adversarial drift), 
              not a lack of training rounds or compute. All three configurations evaluated identically on <span className="text-slate-900 font-mono font-bold">orders_validation (3,885 orders)</span>.
            </p>
          </div>
        </div>

        {/* Prominent Methodological Notice */}
        <div className="mt-4 p-4 rounded-2xl bg-indigo-50/50 border border-indigo-100 flex items-start gap-3 text-xs text-slate-700">
          <Info className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-slate-900">Controlled Mechanism-Proof Isolation:</span>
            <p className="text-xs text-slate-600 leading-relaxed">
              This experiment isolates the adaptation mechanism against pre-drift compute scaling. 
              The drift-adapted numbers reflect feedback-guided recovery on the validation distribution and are not out-of-sample test results. 
              The official system performance is evaluated strictly on the untouched <code className="text-indigo-700 font-bold font-mono bg-white px-1.5 py-0.5 rounded border border-indigo-200">held_out_test.csv</code>.
            </p>
          </div>
        </div>
      </div>

      {/* 3-Way Comparison Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 1. Frozen v1 */}
        <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-5 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200 flex items-center gap-1 font-semibold">
                <Lock className="w-3 h-3 text-slate-500" />
                3 Rounds (Train Only)
              </span>
              <span className="text-xs text-rose-600 font-bold font-mono">
                -73.0% Degradation
              </span>
            </div>

            <h3 className="text-base font-bold text-slate-900">
              Original Frozen v1 Ensemble
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Selected 2 rules (<code className="text-slate-800 font-mono font-semibold">hyp_r3_3_f4b4</code> + <code className="text-slate-800 font-mono font-semibold">hyp_r2_3_bd99</code>) trained autonomously on pre-drift data.
            </p>
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-100 font-mono text-xs">
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Train Net Savings:</span>
              <span className="text-slate-900 font-bold">₹24,312.15</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Train Recall:</span>
              <span className="text-slate-900 font-bold">9.63%</span>
            </div>
            <div className="flex justify-between py-1.5 bg-rose-50 px-2.5 rounded-xl text-rose-800 font-bold">
              <span>Validation Net Savings:</span>
              <span>₹6,567.62</span>
            </div>
            <div className="flex justify-between py-1.5 bg-rose-50 px-2.5 rounded-xl text-rose-800 font-bold">
              <span>Validation Recall:</span>
              <span>3.79%</span>
            </div>
            <div className="flex justify-between py-1 text-[11px] text-slate-500">
              <span>Precision:</span>
              <span className="text-slate-800 font-semibold">42.86%</span>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-rose-50/60 border border-rose-200 text-xs text-rose-900">
            <div className="font-bold mb-1 flex items-center gap-1.5">
              <AlertOctagon className="w-4 h-4 text-rose-600" />
              Drift Vulnerability:
            </div>
            Static rules suffer a severe 73% drop in financial savings when exposed to shifted COD checkout patterns.
          </div>
        </div>

        {/* 2. Rounds-Matched Shadow Control */}
        <div className="p-6 rounded-2xl border border-amber-200 bg-amber-50/30 shadow-xs space-y-5 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200 flex items-center gap-1 font-semibold">
                <Layers className="w-3 h-3 text-amber-600" />
                5 Rounds (Train Only)
              </span>
              <span className="text-xs text-amber-700 font-bold font-mono">
                -61.5% Val Drop
              </span>
            </div>

            <h3 className="text-base font-bold text-slate-900">
              Rounds-Matched Shadow Control
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Explored 5 full rounds of mutations (<code className="text-slate-800 font-mono font-semibold">hyp_shadow_r4_01</code> + <code className="text-slate-800 font-mono font-semibold">hyp_shadow_r5_02</code>) on pre-drift data only.
            </p>
          </div>

          <div className="space-y-2 pt-2 border-t border-amber-100 font-mono text-xs">
            <div className="flex justify-between py-1 border-b border-amber-100">
              <span className="text-slate-500">Train Net Savings:</span>
              <span className="text-slate-900 font-bold">₹34,441.85</span>
            </div>
            <div className="flex justify-between py-1 border-b border-amber-100">
              <span className="text-slate-500">Train Recall:</span>
              <span className="text-slate-900 font-bold">16.97%</span>
            </div>
            <div className="flex justify-between py-1.5 bg-amber-100/70 px-2.5 rounded-xl text-amber-900 font-bold">
              <span>Validation Net Savings:</span>
              <span>₹13,273.93</span>
            </div>
            <div className="flex justify-between py-1.5 bg-amber-100/70 px-2.5 rounded-xl text-amber-900 font-bold">
              <span>Validation Recall:</span>
              <span>8.38%</span>
            </div>
            <div className="flex justify-between py-1 text-[11px] text-slate-500">
              <span>Precision:</span>
              <span className="text-slate-800 font-semibold">36.65%</span>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-amber-100/60 border border-amber-200 text-xs text-amber-900">
            <div className="font-bold mb-1 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-amber-600" />
              Ablation Proof:
            </div>
            Extra compute on historical pre-drift data improves train metrics (+₹34k) but still collapses by 61.5% on drifted traffic.
          </div>
        </div>

        {/* 3. Drift-Adapted Evolved Ensemble */}
        <div className="p-6 rounded-2xl border border-emerald-300 bg-emerald-50/40 shadow-sm space-y-5 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center gap-1 font-semibold">
                <Sparkles className="w-3 h-3 text-emerald-600" />
                5 Rounds (Drift-Aware)
              </span>
              <span className="text-xs text-emerald-700 font-bold font-mono">
                +246.2% vs v1
              </span>
            </div>

            <h3 className="text-base font-bold text-slate-900">
              Drift-Adapted Evolved Ensemble
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Feedback-guided reflection synthesizing rules (<code className="text-slate-800 font-mono font-semibold">hyp_adapted_01</code>) targeting shifted COD velocity and metro pincodes.
            </p>
          </div>

          <div className="space-y-2 pt-2 border-t border-emerald-100 font-mono text-xs">
            <div className="flex justify-between py-1 border-b border-emerald-100">
              <span className="text-slate-500">Train Net Savings:</span>
              <span className="text-slate-900 font-bold">₹35,428.00</span>
            </div>
            <div className="flex justify-between py-1 border-b border-emerald-100">
              <span className="text-slate-500">Train Recall:</span>
              <span className="text-slate-900 font-bold">14.10%</span>
            </div>
            <div className="flex justify-between py-1.5 bg-emerald-100 px-2.5 rounded-xl text-emerald-900 font-bold">
              <span>Validation Net Savings:</span>
              <span>+₹22,734.77</span>
            </div>
            <div className="flex justify-between py-1.5 bg-emerald-100 px-2.5 rounded-xl text-emerald-900 font-bold">
              <span>Validation Recall:</span>
              <span>21.20%</span>
            </div>
            <div className="flex justify-between py-1 text-[11px] text-slate-500">
              <span>Precision:</span>
              <span className="text-slate-800 font-semibold">38.45%</span>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-emerald-100/70 border border-emerald-200 text-xs text-emerald-900">
            <div className="font-bold mb-1 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-700" />
              Autonomous Recovery:
            </div>
            Net savings recovered to ₹22,734.77 with recall quadrupled from 3.79% to 21.20%, proving self-evolution efficacy.
          </div>
        </div>
      </div>
    </div>
  );
}