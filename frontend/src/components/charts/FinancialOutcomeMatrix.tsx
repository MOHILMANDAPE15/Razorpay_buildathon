'use client';

import React from 'react';
import { ShieldAlert, Users, CheckCircle2, DollarSign, TrendingUp, AlertTriangle } from 'lucide-react';

export function FinancialOutcomeMatrix() {
  return (
    <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-emerald-600" />
              Financial 3-Way Outcome Matrix (Held-Out Test Set)
            </h3>
            <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              Unit Economics
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Cost-weighted breakdown of the 2,641 locked test orders across the 3-Way Policy Router at production threshold <span className="font-mono font-bold text-slate-800">T = 0.70</span>.
          </p>
        </div>
        <div className="text-right hidden sm:block">
          <span className="text-[11px] font-mono text-slate-400">Locked Test Split (Days 76–89)</span>
          <p className="text-xs font-bold text-slate-700 font-mono">2,641 Total Orders</p>
        </div>
      </div>

      {/* 3 Outcome Rows / Quadrant Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Tier 1: Auto-Blocked */}
        <div className="p-5 rounded-2xl border border-emerald-300 bg-gradient-to-b from-emerald-500/10 via-emerald-500/5 to-transparent space-y-4 flex flex-col justify-between shadow-xs">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold font-mono bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1">
                <ShieldAlert className="w-3 h-3 text-emerald-600" />
                Score ≥ 0.70
              </span>
              <span className="text-xs font-mono font-bold text-emerald-800">51 Orders (1.93%)</span>
            </div>
            <h4 className="text-sm font-extrabold text-slate-900">1. Auto-Block (High Risk)</h4>
            <p className="text-[11.5px] text-slate-600 leading-relaxed">
              Automated hold requiring online prepayment. Clears the 22.26% break-even hurdle.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-white/90 border border-emerald-200 space-y-2 font-mono text-xs shadow-2xs">
            <div className="flex justify-between items-center text-slate-700">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
                19 True Positives (RTOs):
              </span>
              <strong className="text-emerald-700">+₹4,750.00</strong>
            </div>
            <div className="flex justify-between items-center text-slate-700">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-amber-500 inline-block" />
                32 False Positives (Insults):
              </span>
              <strong className="text-rose-600">-₹2,291.09</strong>
            </div>
            <div className="pt-2 border-t border-slate-100 flex justify-between items-center text-sm font-extrabold text-emerald-800 bg-emerald-50/70 p-1.5 rounded-lg">
              <span>Auto Net Profit:</span>
              <span>+₹2,458.91</span>
            </div>
          </div>

          <div className="text-[10.5px] text-emerald-800/90 font-mono bg-emerald-50/80 px-2.5 py-1.5 rounded-lg border border-emerald-200/60">
            ✓ 37.25% Precision &gt; 22.26% Break-Even
          </div>
        </div>

        {/* Tier 2: Manual Review Queue */}
        <div className="p-5 rounded-2xl border border-indigo-200 bg-gradient-to-b from-indigo-500/10 via-indigo-500/5 to-transparent space-y-4 flex flex-col justify-between shadow-xs">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold font-mono bg-indigo-100 text-indigo-800 border border-indigo-200 flex items-center gap-1">
                <Users className="w-3 h-3 text-indigo-600" />
                0.35 ≤ Score &lt; 0.70
              </span>
              <span className="text-xs font-mono font-bold text-indigo-800">53 Orders (2.01%)</span>
            </div>
            <h4 className="text-sm font-extrabold text-slate-900">2. Review Queue (Ambiguous)</h4>
            <p className="text-[11.5px] text-slate-600 leading-relaxed">
              Triage queue for human agents or automated WhatsApp/IVR OTP confirmation.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-white/90 border border-indigo-100 space-y-2 font-mono text-xs shadow-2xs">
            <div className="flex justify-between items-center text-slate-700">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-indigo-500 inline-block" />
                25 Real RTOs Isolated:
              </span>
              <strong className="text-indigo-700">47.17% Concentration</strong>
            </div>
            <div className="flex justify-between items-center text-slate-700">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-slate-400 inline-block" />
                28 Legitimate Buyers:
              </span>
              <strong className="text-slate-600">Zero Margin Loss</strong>
            </div>
            <div className="pt-2 border-t border-slate-100 flex justify-between items-center text-sm font-extrabold text-indigo-900 bg-indigo-50/70 p-1.5 rounded-lg">
              <span>Risk Density Lift:</span>
              <span>1.52× Enrichment</span>
            </div>
          </div>

          <div className="text-[10.5px] text-indigo-800/90 font-mono bg-indigo-50/80 px-2.5 py-1.5 rounded-lg border border-indigo-200/60">
            ✓ Captures RTOs with zero customer insult penalties
          </div>
        </div>

        {/* Tier 3: Auto-Approved */}
        <div className="p-5 rounded-2xl border border-slate-200 bg-gradient-to-b from-slate-100 via-slate-50 to-white space-y-4 flex flex-col justify-between shadow-xs">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold font-mono bg-slate-100 text-slate-700 border border-slate-200 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-slate-600" />
                Score &lt; 0.35
              </span>
              <span className="text-xs font-mono font-bold text-slate-800">2,537 Orders (96.06%)</span>
            </div>
            <h4 className="text-sm font-extrabold text-slate-900">3. Auto-Approve (Clean)</h4>
            <p className="text-[11.5px] text-slate-600 leading-relaxed">
              Frictionless instant dispatch for trusted shoppers, maximizing conversion.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-white/90 border border-slate-200 space-y-2 font-mono text-xs shadow-2xs">
            <div className="flex justify-between items-center text-slate-700">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
                Clean Buyers Approved:
              </span>
              <strong className="text-slate-800">96.06% Volume</strong>
            </div>
            <div className="flex justify-between items-center text-slate-700">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-slate-400 inline-block" />
                Checkout Latency:
              </span>
              <strong className="text-slate-700">&lt;10ms (In-Memory)</strong>
            </div>
            <div className="pt-2 border-t border-slate-100 flex justify-between items-center text-sm font-extrabold text-slate-900 bg-slate-100/70 p-1.5 rounded-lg">
              <span>Gross GMV Protected:</span>
              <span>100% Retained</span>
            </div>
          </div>

          <div className="text-[10.5px] text-slate-700 font-mono bg-slate-100/80 px-2.5 py-1.5 rounded-lg border border-slate-200">
            ✓ Zero cart abandonment on verified buyers
          </div>
        </div>
      </div>

      {/* Comparison Callout vs GBDT */}
      <div className="p-4 rounded-xl bg-slate-900 text-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <span className="text-[11px] font-mono uppercase tracking-wider text-indigo-400 font-bold">
            Industry Benchmark Contrast
          </span>
          <p className="text-xs text-slate-300 leading-relaxed">
            Standard ML (LightGBM GBDT) blindly flags 113 false positives on high-ticket items, incurring <strong>-₹33,441 in margin insult penalties</strong> and collapsing to a <strong>-₹3,941.66 net loss</strong>. Aegis's bounded routing secures <strong>+₹2,458.91 in net profit</strong> (+₹6,400 outperformance).
          </p>
        </div>
        <div className="flex items-center gap-2 self-start sm:self-auto shrink-0 font-mono text-xs">
          <div className="px-3 py-1.5 rounded-lg bg-emerald-950 border border-emerald-500/40 text-emerald-300 font-bold">
            Aegis: +₹2,458.91
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-rose-950 border border-rose-500/40 text-rose-300 font-bold">
            GBDT: -₹3,941.66
          </div>
        </div>
      </div>
    </div>
  );
}
