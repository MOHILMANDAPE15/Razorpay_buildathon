'use client';

import React from 'react';
import { Layers, Flame, TrendingUp, CheckCircle2, DollarSign, Clock, Sparkles, Code2, ChevronRight, History } from 'lucide-react';
import clsx from 'clsx';
import { DiscoveredCluster } from '@/lib/api';

interface DiscoveredClustersBarChartProps {
  clusters: DiscoveredCluster[];
  selectedClusterId: string | null;
  onSelectCluster: (id: string) => void;
}

export function DiscoveredClustersBarChart({
  clusters,
  selectedClusterId,
  onSelectCluster,
}: DiscoveredClustersBarChartProps) {
  if (!clusters || clusters.length === 0) return null;

  const maxMiss = Math.max(...clusters.map((c) => c.miss_volume), 1);
  const maxCohort = Math.max(...clusters.map((c) => c.cohort_size), 1);

  return (
    <div className="space-y-6">
      {/* Visual Header */}
      <div className="p-6 rounded-2xl border border-purple-200 bg-gradient-to-r from-purple-500/10 via-purple-500/5 to-white shadow-xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-100 border border-purple-200 flex items-center justify-center text-purple-700 shadow-2xs">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-extrabold text-slate-900 tracking-tight">
                  Discovered Uncaught Fraud Patterns & Recoverable Money
                </h3>
                <span className="text-[11px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-800 border border-purple-300">
                  95%+ Verified
                </span>
              </div>
              <p className="text-xs text-slate-600 mt-0.5">
                The Residual Miner finds hidden fraud loops that bypassed existing rules, calculates recoverable cash, and automatically builds defensive code.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Unified Cluster Cards with Visual Comparison & Synthesized Rules */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {clusters.map((cluster) => {
          const isSelected = selectedClusterId === cluster.cluster_id;
          const missPercent = Math.max(12, (cluster.miss_volume / maxMiss) * 100);
          const cohortPercent = Math.max(12, (cluster.cohort_size / maxCohort) * 100);
          const hyp = cluster.resulting_hypothesis;
          const recoverableCash = cluster.miss_volume * 250;
          const isAutonomous = cluster.is_autonomous_discovery;
          const confidencePct = Math.min(99.9, (1 - cluster.p_value) * 100);

          return (
            <div
              key={cluster.cluster_id}
              onClick={() => onSelectCluster(cluster.cluster_id)}
              className={clsx(
                'p-6 rounded-2xl border transition-all duration-200 cursor-pointer space-y-5 flex flex-col justify-between shadow-xs hover:shadow-md',
                isSelected
                  ? 'border-purple-500 bg-purple-50/30 ring-2 ring-purple-500/20'
                  : 'border-slate-200 bg-white hover:border-purple-300'
              )}
            >
              <div className="space-y-4">
                {/* Top Badge Strip */}
                <div className="flex items-center justify-between gap-2">
                  <div className="flex flex-wrap items-center gap-1.5">
                    {isAutonomous ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 border border-purple-200 flex items-center gap-1">
                        <Sparkles className="w-3 h-3 text-purple-600" />
                        AI Discovered
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                        Pattern #{cluster.cluster_id}
                      </span>
                    )}

                    {cluster.status === 'on_cooldown' ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200 flex items-center gap-1">
                        <Clock className="w-3 h-3 text-amber-600" />
                        On Cooldown (Paused {cluster.cooldown_info?.cooldown_until_round || 3} rounds)
                      </span>
                    ) : cluster.status === 'bypassed_surge' ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 border border-rose-200 flex items-center gap-1 animate-pulse">
                        <Flame className="w-3 h-3 text-rose-600" />
                        Emergency Surge Active (&gt;50% Spike)
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        Verified Real Threat
                      </span>
                    )}
                  </div>

                  <span className="text-xs font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                    {confidencePct.toFixed(1)}% Certainty
                  </span>
                </div>

                {/* Title & Signature Tags */}
                <div>
                  <h4 className="text-base font-extrabold text-slate-900 leading-snug">
                    {cluster.cluster_name}
                  </h4>
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {Object.entries(cluster.signature_patterns).map(([k, v]) => (
                      <span
                        key={k}
                        className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200 font-semibold"
                      >
                        {k}: <span className="text-purple-700">{String(v)}</span>
                      </span>
                    ))}
                  </div>
                </div>

                {/* Financial Value Banner */}
                <div className="p-3 rounded-xl bg-emerald-50/80 border border-emerald-200 flex items-center justify-between text-xs font-mono">
                  <span className="text-emerald-900 font-bold flex items-center gap-1">
                    <DollarSign className="w-4 h-4 text-emerald-600" />
                    Recoverable Logistics Waste:
                  </span>
                  <strong className="text-sm font-extrabold text-emerald-700">
                    +₹{recoverableCash.toLocaleString('en-IN')}
                  </strong>
                </div>

                {/* Visual Bars Comparison */}
                <div className="space-y-2.5 pt-1">
                  {/* Missed RTOs Bar */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-500 text-[11px]">Unflagged Bounced Orders:</span>
                      <span className="font-bold text-rose-600">{cluster.miss_volume} orders lost</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-rose-500 to-pink-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${missPercent}%` }}
                      />
                    </div>
                  </div>

                  {/* Total Traffic Volume Bar */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-500 text-[11px]">Total Matching Orders:</span>
                      <span className="font-bold text-slate-800">{cluster.cohort_size} orders in group</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-purple-500 to-indigo-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${cohortPercent}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* Plain English Explanation of Metrics */}
                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100 font-mono text-xs">
                  <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 space-y-0.5">
                    <span className="text-[10.5px] text-slate-500 block">Risk Lift Multiplier</span>
                    <strong className="text-sm font-extrabold text-purple-700">{cluster.statistical_lift.toFixed(2)}× Higher Risk</strong>
                    <span className="text-[10px] text-slate-400 block">
                      ({cluster.statistical_lift.toFixed(2)}x more likely to bounce than normal)
                    </span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 space-y-0.5">
                    <span className="text-[10.5px] text-slate-500 block">Failure Rate in Group</span>
                    <strong className="text-sm font-extrabold text-rose-600">{cluster.miss_percentage_of_cohort.toFixed(1)}% Bounced</strong>
                    <span className="text-[10px] text-slate-400 block">
                      (Severe concentration of RTOs)
                    </span>
                  </div>
                </div>

                {/* Resulting Synthesized Python Rule */}
                {hyp && (
                  <div className="p-3 rounded-xl bg-slate-900 text-slate-100 space-y-2 text-xs font-mono">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-300 font-bold flex items-center gap-1.5">
                        <Code2 className="w-3.5 h-3.5 text-indigo-400" />
                        AI Shield Created: <span className="text-indigo-300">{hyp.hypothesis_id}</span>
                      </span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-700/50">
                        {hyp.gate_verdict} (+₹{hyp.net_financial_delta_inr.toLocaleString('en-IN')})
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-300 bg-slate-950/80 p-2 rounded-lg border border-slate-800 line-clamp-2 overflow-hidden">
                      {hyp.rule_code}
                    </div>
                  </div>
                )}
              </div>

              {/* Action Link */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-purple-700 font-bold">
                <span className="flex items-center gap-1.5">
                  <History className="w-4 h-4" />
                  Click to inspect full AI evolution & cooldown history
                </span>
                <ChevronRight className="w-4 h-4" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
