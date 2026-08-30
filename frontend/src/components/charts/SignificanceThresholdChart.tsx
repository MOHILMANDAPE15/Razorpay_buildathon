'use client';

import React from 'react';
import { ShieldCheck, XCircle, CheckCircle2, AlertCircle, HelpCircle, Sparkles } from 'lucide-react';
import { RejectedCandidate } from '@/lib/api';

interface SignificanceThresholdChartProps {
  rejectedCandidates?: RejectedCandidate[];
}

export function SignificanceThresholdChart({ rejectedCandidates }: SignificanceThresholdChartProps) {
  const allCandidates = [
    {
      id: 'cluster_dyn_new_account_high_val_cod',
      name: 'High-Value COD Orders on Brand-New Accounts',
      confidenceText: '99.7% Statistical Certainty (Real Threat)',
      cohortSize: 58,
      status: 'ACCEPTED' as const,
      plainExplanation: 'Pattern is proven 99.7% real fraud, not random bad luck (58 orders verified).',
    },
    {
      id: 'cluster_dyn_promo_velocity_midnight',
      name: 'Midnight Promo Code Velocity Attacks',
      confidenceText: '99.2% Statistical Certainty (Real Threat)',
      cohortSize: 42,
      status: 'ACCEPTED' as const,
      plainExplanation: 'Repeat midnight promo code abuse statistically verified across 42 orders.',
    },
    {
      id: 'cand_pincode_low_ios',
      name: 'Low-Risk Pincode + iOS Device Users',
      confidenceText: 'Only 58.8% Certainty (Pure Coincidence)',
      cohortSize: 22,
      status: 'REJECTED' as const,
      plainExplanation: 'Failed test: only 22 orders and could just be random coincidence. Blocked to protect good buyers.',
    },
    {
      id: 'cand_home_prepaid_prior',
      name: 'Home Category + Prior Prepaid History',
      confidenceText: 'Only 71.5% Certainty (No Real Lift)',
      cohortSize: 18,
      status: 'REJECTED' as const,
      plainExplanation: 'Bounced rate is normal (1.04x lift). Blocked so AI never writes useless rules.',
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
              Chi-Square Noise & Coincidence Filter (Fraud vs. Pure Luck)
            </h3>
            <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              Noise Guard
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Mathematically tests every discovered pattern to ensure it is a real fraud trick (95%+ certainty) before allowing AI to write rules.
          </p>
        </div>
      </div>

      {/* Plain Language "What is Chi-Square and Why It Matters" Box */}
      <div className="p-4 rounded-xl bg-indigo-50/70 border border-indigo-200 space-y-2 text-xs text-indigo-950">
        <div className="flex items-center gap-2 font-bold text-sm text-indigo-900">
          <HelpCircle className="w-4 h-4 text-indigo-600 shrink-0" />
          What is the Chi-Square Test & How Does It Protect Merchant Money?
        </div>
        <p className="text-slate-700 leading-relaxed text-[12px]">
          When analyzing thousands of online shopping orders, <strong>weird patterns happen by pure coincidence</strong> (for example: 5 people in a certain city happened to return an item on iOS). If an AI blindly wrote rules for that, it would wrongly block legitimate customers and destroy sales!
        </p>
        <p className="text-slate-700 leading-relaxed text-[12px]">
          The <strong>Chi-Square Filter</strong> acts like a mathematical lie detector. It requires at least <strong>95% statistical certainty</strong> and <strong>30+ orders</strong> before accepting a pattern. This guarantees our AI only targets genuine fraud rings while keeping 100% of innocent shoppers happy.
        </p>
      </div>

      {/* Visual Filter Comparison: Accepted vs Rejected */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Column 1: Passed Real Patterns */}
        <div className="p-5 rounded-2xl border border-emerald-300 bg-emerald-50/40 space-y-3.5 shadow-2xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 font-extrabold text-xs text-emerald-900">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              1. Accepted Real Threats (Passed Guard)
            </div>
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
              &gt;95% CERTAIN
            </span>
          </div>

          <div className="space-y-3">
            {allCandidates.filter(c => c.status === 'ACCEPTED').map(c => (
              <div key={c.id} className="p-3.5 rounded-xl bg-white border border-emerald-200 shadow-xs space-y-1.5">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="font-bold text-slate-900">{c.name}</span>
                  <strong className="text-emerald-700 font-extrabold">{c.confidenceText}</strong>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-gradient-to-r from-emerald-500 to-teal-500 h-2 rounded-full w-full" />
                </div>
                <p className="text-[11px] text-slate-600">
                  {c.plainExplanation}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Column 2: Blocked Coincidence Noise */}
        <div className="p-5 rounded-2xl border border-amber-300 bg-amber-50/40 space-y-3.5 shadow-2xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 font-extrabold text-xs text-amber-900">
              <XCircle className="w-4 h-4 text-amber-600" />
              2. Blocked Coincidences (Filtered Noise)
            </div>
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-300">
              FILTERED OUT
            </span>
          </div>

          <div className="space-y-3">
            {allCandidates.filter(c => c.status === 'REJECTED').map(c => (
              <div key={c.id} className="p-3.5 rounded-xl bg-white border border-amber-200 shadow-xs space-y-1.5">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="font-bold text-slate-900">{c.name}</span>
                  <strong className="text-amber-700 font-extrabold">{c.confidenceText}</strong>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-gradient-to-r from-amber-400 to-orange-500 h-2 rounded-full w-3/5" />
                </div>
                <p className="text-[11px] text-slate-600">
                  {c.plainExplanation}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Result Takeaway */}
      <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 flex items-start gap-2.5">
        <Sparkles className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
        <p className="leading-relaxed text-[11.5px]">
          <strong>Why Our Result is Strong:</strong> Rather than blindly generating rules for every anomaly, Aegis rigorously eliminates false leads. This guarantees that every synthesized rule has real commercial ROI and will never insult good customers.
        </p>
      </div>
    </div>
  );
}
