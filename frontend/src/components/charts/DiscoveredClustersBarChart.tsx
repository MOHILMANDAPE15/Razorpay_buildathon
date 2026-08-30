'use client';

import React from 'react';
import { Layers, Flame, TrendingUp, CheckCircle2 } from 'lucide-react';
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
    <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
              <Layers className="w-5 h-5 text-purple-600" />
              Discovered Residual Clusters (Visual Lift & Miss Comparison)
            </h3>
            <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200">
              Chi-Square p &lt; 0.05
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Comparing statistical lift, missed false negative volume, and cohort size across active discovered signatures.
          </p>
        </div>
      </div>

      {/* Cluster Comparative Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {clusters.map((cluster) => {
          const isSelected = selectedClusterId === cluster.cluster_id;
          const missPercent = Math.max(12, (cluster.miss_volume / maxMiss) * 100);
          const cohortPercent = Math.max(12, (cluster.cohort_size / maxCohort) * 100);

          return (
            <div
              key={cluster.cluster_id}
              onClick={() => onSelectCluster(cluster.cluster_id)}
              className={clsx(
                'p-5 rounded-2xl border transition-all cursor-pointer space-y-4 shadow-xs',
                isSelected
                  ? 'border-purple-500 bg-purple-50/40 ring-2 ring-purple-500/20'
                  : 'border-slate-200 bg-white hover:border-purple-300 hover:bg-slate-50/50'
              )}
            >
              {/* Card Header */}
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="font-mono text-[10px] text-purple-600 uppercase font-bold tracking-wider">
                    {cluster.cluster_id}
                  </span>
                  <h4 className="text-sm font-bold text-slate-900 mt-0.5">{cluster.cluster_name}</h4>
                </div>
                <span
                  className={clsx(
                    'px-2 py-0.5 rounded-full text-[10px] font-bold font-mono border shrink-0',
                    cluster.status === 'on_cooldown'
                      ? 'bg-amber-50 text-amber-700 border-amber-200'
                      : cluster.status === 'bypassed_surge'
                      ? 'bg-rose-50 text-rose-700 border-rose-200 animate-pulse'
                      : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  )}
                >
                  {cluster.status === 'on_cooldown'
                    ? `Cooldown (R${cluster.cooldown_info?.cooldown_until_round || 3})`
                    : cluster.status === 'bypassed_surge'
                    ? 'Surge Bypass'
                    : 'Significant'}
                </span>
              </div>

              {/* Visual Bars */}
              <div className="space-y-3 pt-1">
                {/* Miss Volume Bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-slate-500 text-[11px]">Missed RTOs:</span>
                    <span className="font-bold text-rose-600">{cluster.miss_volume} orders</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-rose-500 to-pink-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${missPercent}%` }}
                    />
                  </div>
                </div>

                {/* Cohort Size Bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-slate-500 text-[11px]">Cohort Volume (N):</span>
                    <span className="font-bold text-slate-800">{cluster.cohort_size} orders</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-indigo-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${cohortPercent}%` }}
                    />
                  </div>
                </div>

                {/* Key Metrics Row */}
                <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-100 font-mono text-center">
                  <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
                    <span className="text-[10px] text-slate-400 block">Risk Lift</span>
                    <span className="text-xs font-extrabold text-purple-700">{cluster.statistical_lift.toFixed(2)}×</span>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
                    <span className="text-[10px] text-slate-400 block">p-Value</span>
                    <span className="text-xs font-extrabold text-emerald-700">{cluster.p_value.toFixed(4)}</span>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
                    <span className="text-[10px] text-slate-400 block">Miss Rate</span>
                    <span className="text-xs font-extrabold text-slate-800">{cluster.miss_percentage_of_cohort.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
