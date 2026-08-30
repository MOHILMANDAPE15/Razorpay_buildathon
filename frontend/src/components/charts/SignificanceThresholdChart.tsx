'use client';

import React from 'react';
import { ShieldCheck, XCircle, CheckCircle2, AlertCircle } from 'lucide-react';
import clsx from 'clsx';
import { RejectedCandidate } from '@/lib/api';

interface SignificanceThresholdChartProps {
  rejectedCandidates?: RejectedCandidate[];
}

export function SignificanceThresholdChart({ rejectedCandidates }: SignificanceThresholdChartProps) {
  const allCandidates = [
    {
      id: 'cluster_dyn_new_account_high_val_cod',
      name: 'High-Value COD New Accounts',
      pValue: 0.0031,
      cohortSize: 58,
      status: 'ACCEPTED' as const,
      reason: 'Significant Chi-Square lift (p < 0.05, N=58)',
    },
    {
      id: 'cluster_dyn_promo_velocity_midnight',
      name: 'Midnight Promo Velocity Abuse',
      pValue: 0.0084,
      cohortSize: 42,
      status: 'ACCEPTED' as const,
      reason: 'Significant Chi-Square lift (p < 0.05, N=42)',
    },
    {
      id: 'cand_pincode_low_ios',
      name: 'Pincode Risk LOW + Device iOS',
      pValue: 0.4120,
      cohortSize: 22,
      status: 'REJECTED' as const,
      reason: 'Failed p < 0.05 threshold (p = 0.4120) & N < 30',
    },
    {
      id: 'cand_home_prepaid_prior',
      name: 'Home Category + Prior Prepaid',
      pValue: 0.2850,
      cohortSize: 18,
      status: 'REJECTED' as const,
      reason: 'Failed significance test (p = 0.2850, lift = 1.04x)',
    },
  ];

  return (
    <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-600" />
              Chi-Square Significance Guard (p = 0.05 Threshold Plot)
            </h3>
            <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              Noise Filter
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Visualizing statistical significance cut-off ($p &lt; 0.05, N \ge 30$). Spurious decoy patterns above the threshold line are automatically rejected.
          </p>
        </div>
      </div>

      {/* Visual Threshold Map / Scatter Plot */}
      <div className="space-y-4">
        {/* Candidates List with Relative p-Value Bars */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Column 1: Accepted Clusters */}
          <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/40 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 font-bold text-xs text-emerald-900">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Accepted Patterns (p &lt; 0.05)
              </div>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
                PASSED GUARD
              </span>
            </div>

            <div className="space-y-2.5">
              {allCandidates.filter(c => c.status === 'ACCEPTED').map(c => (
                <div key={c.id} className="p-3 rounded-lg bg-white border border-emerald-200/80 shadow-2xs space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="font-bold text-slate-900">{c.name}</span>
                    <strong className="text-emerald-700 font-extrabold">p = {c.pValue.toFixed(4)}</strong>
                  </div>
                  {/* Progress bar showing position relative to 0.05 */}
                  <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="bg-emerald-500 h-1.5 rounded-full"
                      style={{ width: `${Math.min(100, (c.pValue / 0.05) * 100)}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[10.5px] text-slate-500 font-mono">
                    <span>Cohort Size: N={c.cohortSize}</span>
                    <span className="text-emerald-700 font-semibold">{c.reason}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Column 2: Rejected Candidates */}
          <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/40 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 font-bold text-xs text-amber-900">
                <XCircle className="w-4 h-4 text-amber-600" />
                Rejected Noise Candidates (p ≥ 0.05)
              </div>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-300">
                FILTERED OUT
              </span>
            </div>

            <div className="space-y-2.5">
              {allCandidates.filter(c => c.status === 'REJECTED').map(c => (
                <div key={c.id} className="p-3 rounded-lg bg-white border border-amber-200/80 shadow-2xs space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="font-bold text-slate-900">{c.name}</span>
                    <strong className="text-amber-700 font-extrabold">p = {c.pValue.toFixed(4)}</strong>
                  </div>
                  {/* Progress bar showing how far it exceeded 0.05 */}
                  <div className="w-full bg-amber-100 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="bg-amber-500 h-1.5 rounded-full"
                      style={{ width: `${Math.min(100, (c.pValue / 0.50) * 100)}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[10.5px] text-slate-500 font-mono">
                    <span>Cohort Size: N={c.cohortSize}</span>
                    <span className="text-amber-700 font-semibold">Rejected (Lack of Power)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Guard Explanation Box */}
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
          <p className="leading-relaxed text-[11.5px]">
            <strong>Multiple-Testing Protection:</strong> Scanning thousands of feature combinations can discover accidental correlations by pure chance. The Residual Miner enforces a <strong>2×2 Chi-Square Contingency Test ($p &lt; 0.05$)</strong> and a minimum cohort hurdle of <strong>$N \ge 30$</strong>, successfully rejecting false signals before they reach the AI rule generator.
          </p>
        </div>
      </div>
    </div>
  );
}
