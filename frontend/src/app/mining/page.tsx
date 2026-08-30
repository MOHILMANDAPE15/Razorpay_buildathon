'use client';

import React, { useState, useEffect } from 'react';
import {
  Activity,
  Layers,
  Sparkles,
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Flame,
  XCircle,
  AlertTriangle,
  Code2,
  Calendar,
  History,
  TrendingUp,
  RefreshCw,
  Info,
  ChevronRight,
  X,
  Lock
} from 'lucide-react';
import clsx from 'clsx';
import {
  fetchResidualMiningScan,
  fetchClusterHistory,
  ResidualMiningScanResponse,
  DiscoveredCluster,
  ClusterHistoryResponse,
  RejectedCandidate
} from '@/lib/api';

export default function ResidualMiningPage() {
  const [scanData, setScanData] = useState<ResidualMiningScanResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedClusterId, setSelectedClusterId] = useState<string | null>(null);
  const [clusterHistory, setClusterHistory] = useState<ClusterHistoryResponse | null>(null);
  const [historyLoading, setHistoryLoading] = useState<boolean>(false);
  const [activeSplit, setActiveSplit] = useState<'training' | 'validation'>('training');

  const loadScan = (split: 'training' | 'validation') => {
    setLoading(true);
    fetchResidualMiningScan(split)
      .then((data) => setScanData(data))
      .catch((err) => console.error('Failed to load residual mining scan:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadScan(activeSplit);
  }, [activeSplit]);

  const handleSelectCluster = (clusterId: string) => {
    setSelectedClusterId(clusterId);
    setHistoryLoading(true);
    fetchClusterHistory(clusterId)
      .then((data) => setClusterHistory(data))
      .catch((err) => console.error('Failed to load cluster history:', err))
      .finally(() => setHistoryLoading(false));
  };

  const meta = scanData?.scan_metadata;
  const clusters = scanData?.discovered_clusters || [];
  const rejected = scanData?.rejected_candidates || [];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Header */}
      <div className="border-b border-slate-200 pb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-600 shadow-xs">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
                Residual Mining & Cooldown Lifecycle
              </h1>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200 font-mono font-bold">
                Section 4.5 & 4.6
              </span>
            </div>
            <p className="text-sm text-slate-600 mt-1 max-w-3xl leading-relaxed">
              Mines mature false negatives (&gt;5 days delivery resolution) to cluster unflagged abuse patterns, 
              construct targeted deterministic agendas, and manage cooldown suppression windows.
            </p>
          </div>
        </div>

        {/* Split Switcher */}
        <div className="flex items-center gap-2">
          <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-semibold">
            <button
              onClick={() => setActiveSplit('training')}
              className={clsx(
                'px-3 py-1.5 rounded-lg transition',
                activeSplit === 'training'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              )}
            >
              orders_train (Days 0–55)
            </button>
            <button
              onClick={() => setActiveSplit('validation')}
              className={clsx(
                'px-3 py-1.5 rounded-lg transition',
                activeSplit === 'validation'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              )}
            >
              orders_val (Days 56–75)
            </button>
          </div>

          <button
            onClick={() => loadScan(activeSplit)}
            className="p-2 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-600 shadow-xs transition"
            title="Re-run Residual Scan"
          >
            <RefreshCw className={clsx('w-4 h-4', loading && 'animate-spin text-purple-600')} />
          </button>
        </div>
      </div>

      {/* Data Split & Scope Banner */}
      <div className="p-3.5 rounded-2xl bg-purple-50/60 border border-purple-200 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 text-purple-900 font-medium">
          <Info className="w-4 h-4 text-purple-600 shrink-0" />
          <span>
            {activeSplit === 'training' ? (
              <>
                <strong>Training Split:</strong> <code className="font-mono font-bold text-purple-800">orders_train</code> · Days 0–55 (Jan 01 – Feb 25, 2026) · 10,807 total orders · <strong className="text-slate-900">9,911 mature</strong> (day_index &le; 50)
              </>
            ) : (
              <>
                <strong>Validation Split:</strong> <code className="font-mono font-bold text-purple-800">orders_validation</code> · Days 56–75 (Feb 26 – Mar 17, 2026) · 3,885 total orders · <strong className="text-slate-900">2,918 mature</strong> (day_index &le; 70)
              </>
            )}
          </span>
        </div>
        <span className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-800 border border-purple-200">
          Maturity Guard: Fulfillment Window &gt; 5 Days
        </span>
      </div>

      {/* Header KPI Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
          <span className="text-xs text-slate-500 font-medium block">Mature Orders Scanned</span>
          <div className="text-xl font-bold font-mono text-slate-900 mt-1">
            {loading || !meta ? (
              <span className="inline-block h-6 w-20 bg-slate-200 animate-pulse rounded-md mt-1" />
            ) : (
              meta.mature_orders_count.toLocaleString()
            )}
          </div>
          <span className="text-[11px] text-slate-400 font-mono mt-0.5 block">
            {loading || !meta ? (
              <span className="inline-block h-3 w-28 bg-slate-100 animate-pulse rounded mt-0.5" />
            ) : (
              `${meta.unmatured_orders_deferred} in-flight deferred`
            )}
          </span>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
          <span className="text-xs text-slate-500 font-medium block">Realized False Negatives</span>
          <div className="text-xl font-bold font-mono text-rose-600 mt-1">
            {loading || !meta ? (
              <span className="inline-block h-6 w-16 bg-slate-200 animate-pulse rounded-md mt-1" />
            ) : (
              meta.total_false_negatives.toLocaleString()
            )}
          </div>
          <span className="text-[11px] text-slate-400 font-mono mt-0.5 block">Unflagged RTO abuse</span>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
          <span className="text-xs text-slate-500 font-medium block">False Negative Rate</span>
          <div className="text-xl font-bold font-mono text-amber-600 mt-1">
            {loading || !meta ? (
              <span className="inline-block h-6 w-16 bg-slate-200 animate-pulse rounded-md mt-1" />
            ) : (
              `${(meta.false_negative_rate * 100).toFixed(2)}%`
            )}
          </div>
          <span className="text-[11px] text-slate-400 font-mono mt-0.5 block">Of mature population</span>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
          <span className="text-xs text-slate-500 font-medium block">Significant Clusters</span>
          <div className="text-xl font-bold font-mono text-purple-600 mt-1">
            {loading || !meta ? (
              <span className="inline-block h-6 w-10 bg-slate-200 animate-pulse rounded-md mt-1" />
            ) : (
              clusters.length
            )}
          </div>
          <span className="text-[11px] text-purple-600/80 font-mono mt-0.5 block">Passed Chi-Square p &lt; 0.05</span>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
          <span className="text-xs text-slate-500 font-medium block">Significance Guard Filtered</span>
          <div className="text-xl font-bold font-mono text-slate-700 mt-1">
            {loading || !meta ? (
              <span className="inline-block h-6 w-10 bg-slate-200 animate-pulse rounded-md mt-1" />
            ) : (
              rejected.length
            )}
          </div>
          <span className="text-[11px] text-slate-400 font-mono mt-0.5 block">Blocked false discovery</span>
        </div>
      </div>

      {/* Main Grid: Discovered Clusters */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Layers className="w-5 h-5 text-purple-600" />
            Discovered False Negative Clusters (Round {meta?.current_round || 3})
          </h2>
          <span className="text-xs text-slate-500">
            Click any cluster card to inspect full cross-scan timeline & cooldown history
          </span>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {[1, 2].map((i) => (
              <div key={i} className="p-6 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-4 animate-pulse">
                <div className="flex justify-between items-center">
                  <div className="h-4 w-32 bg-slate-200 rounded" />
                  <div className="h-4 w-16 bg-slate-200 rounded" />
                </div>
                <div className="h-5 w-3/4 bg-slate-200 rounded" />
                <div className="h-16 w-full bg-slate-100 rounded-xl" />
                <div className="grid grid-cols-3 gap-2 pt-2">
                  <div className="h-12 bg-slate-100 rounded-xl" />
                  <div className="h-12 bg-slate-100 rounded-xl" />
                  <div className="h-12 bg-slate-100 rounded-xl" />
                </div>
              </div>
            ))}
          </div>
        ) : clusters.length === 0 ? (
          <div className="p-12 rounded-2xl bg-white border border-slate-200 text-center space-y-3">
            <Activity className="w-8 h-8 text-slate-300 mx-auto" />
            <p className="text-sm font-semibold text-slate-700">No unhandled false negative clusters found</p>
            <p className="text-xs text-slate-500">Current champion ensemble has successfully mitigated known residual patterns.</p>
            <button
              onClick={() => loadScan(activeSplit)}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-semibold shadow-xs transition"
            >
              Re-scan Split
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {clusters.map((cluster) => {
              const isAutonomous = cluster.is_autonomous_discovery;
              const isOnCooldown = cluster.status === 'on_cooldown';
              const isSurgeBypassed = cluster.status === 'bypassed_surge';
              const hyp = cluster.resulting_hypothesis;

              return (
                <div
                  key={cluster.cluster_id}
                  onClick={() => handleSelectCluster(cluster.cluster_id)}
                  className={clsx(
                    'p-6 rounded-2xl border transition-all duration-200 cursor-pointer flex flex-col justify-between relative group hover:shadow-md',
                    isAutonomous
                      ? 'bg-purple-50/40 border-purple-300 hover:border-purple-400'
                      : isOnCooldown
                      ? 'bg-amber-50/30 border-amber-200 hover:border-amber-300'
                      : 'bg-white border-slate-200 hover:border-slate-300 shadow-xs'
                  )}
                >
                  <div className="space-y-4">
                    {/* Top Badges */}
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex flex-wrap items-center gap-1.5">
                        {isAutonomous && (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 border border-purple-200 flex items-center gap-1">
                            <Sparkles className="w-3 h-3 text-purple-600" />
                            Autonomous Discovery
                          </span>
                        )}

                        {isOnCooldown ? (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200 flex items-center gap-1">
                            <Clock className="w-3 h-3 text-amber-600" />
                            On Cooldown (Until R{cluster.cooldown_info.cooldown_until_round})
                          </span>
                        ) : isSurgeBypassed ? (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 border border-rose-200 flex items-center gap-1">
                            <Flame className="w-3 h-3 text-rose-600" />
                            Surge Bypass Active (&gt;50% spike)
                          </span>
                        ) : (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                            Significant → Dispatched
                          </span>
                        )}

                        <span className="text-[10px] font-mono text-slate-500">
                          p={cluster.p_value.toFixed(4)}
                        </span>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-slate-900 group-hover:translate-x-0.5 transition shrink-0" />
                    </div>

                    {/* Title & Signature */}
                    <div>
                      <h3 className="text-base font-bold text-slate-900 group-hover:text-purple-700 transition">
                        {cluster.cluster_name}
                      </h3>
                      {isAutonomous && (
                        <p className="text-[11px] text-purple-700 font-medium mt-0.5">
                          * Mined dynamically with zero hand-coded static equivalent.
                        </p>
                      )}

                      {/* Signature Tags */}
                      <div className="flex flex-wrap gap-1.5 mt-2.5">
                        {Object.entries(cluster.signature_patterns).map(([k, v]) => (
                          <span
                            key={k}
                            className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200/80"
                          >
                            {k}={String(v)}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-3 gap-2 py-2.5 px-3 rounded-xl bg-slate-50 border border-slate-200/80 text-xs font-mono">
                      <div>
                        <span className="text-slate-500 text-[10px] block">Miss Volume:</span>
                        <strong className="text-rose-600 font-bold">{cluster.miss_volume} orders</strong>
                      </div>
                      <div>
                        <span className="text-slate-500 text-[10px] block">Cohort Size:</span>
                        <strong className="text-slate-800 font-bold">{cluster.cohort_size}</strong>
                      </div>
                      <div>
                        <span className="text-slate-500 text-[10px] block">Statistical Lift:</span>
                        <strong className="text-purple-700 font-bold">{cluster.statistical_lift}x</strong>
                      </div>
                    </div>

                    {/* Resulting Hypothesis Synthesis Preview */}
                    {hyp && (
                      <div className="p-3 rounded-xl bg-white border border-slate-200 space-y-2 text-xs">
                        <div className="flex items-center justify-between">
                          <span className="text-slate-500 font-medium flex items-center gap-1.5">
                            <Code2 className="w-3.5 h-3.5 text-indigo-600" />
                            Synthesized Rule: <code className="font-mono text-slate-800">{hyp.hypothesis_id}</code>
                          </span>
                          <span
                            className={clsx(
                              'text-[10px] font-bold px-2 py-0.5 rounded-full',
                              hyp.gate_verdict === 'PROMOTED'
                                ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                                : 'bg-rose-100 text-rose-800 border border-rose-200'
                            )}
                          >
                            {`${hyp.gate_verdict} (${hyp.net_financial_delta_inr >= 0 ? `+₹${hyp.net_financial_delta_inr.toLocaleString()}` : `-₹${Math.abs(hyp.net_financial_delta_inr).toLocaleString()}`})`}
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-600 font-mono bg-slate-50 p-2 rounded-lg border border-slate-100 line-clamp-2">
                          {hyp.rule_code}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Footer Action */}
                  <div className="pt-3 mt-3 border-t border-slate-100 flex items-center justify-between text-xs text-purple-700 font-semibold">
                    <span className="flex items-center gap-1">
                      <History className="w-3.5 h-3.5" />
                      Inspect Lifecycle & Cooldown
                    </span>
                    <span className="text-slate-400 text-[11px]">Click to view</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Significance Guard Rejections Section */}
      <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200 space-y-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-600" />
          <h3 className="text-base font-bold text-slate-900">
            Statistical Significance Guard: Filtered Non-Significant Candidates
          </h3>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200 font-mono">
            Working as Intended
          </span>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed max-w-4xl">
          The significance guard rejects candidate feature combinations where <code className="font-mono bg-white px-1 py-0.5 rounded border border-slate-200">p &ge; 0.05</code> or cohort size &lt; 30. 
          This prevents multiple-testing false discoveries and blocks circular decoy features from polluting the generator agenda.
        </p>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
            {[1, 2].map((i) => (
              <div key={i} className="p-4 rounded-xl bg-white border border-slate-200 space-y-2 text-xs animate-pulse">
                <div className="flex justify-between items-center">
                  <div className="h-4 w-40 bg-slate-200 rounded" />
                  <div className="h-4 w-16 bg-slate-100 rounded" />
                </div>
                <div className="h-3 w-3/4 bg-slate-100 rounded" />
                <div className="h-3 w-1/2 bg-slate-100 rounded" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
            {rejected.map((r, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-white border border-slate-200 space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900">{r.cluster_name}</span>
                  <span className="text-[10px] font-mono font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full border border-rose-200">
                    p = {r.p_value.toFixed(4)}
                  </span>
                </div>
                <div className="text-[11px] text-slate-600 leading-snug">
                  <strong>Reason:</strong> {r.rejection_reason}
                </div>
                <div className="text-[10px] text-slate-400 font-mono">
                  Cohort: {r.cohort_size} orders | Misses: {r.miss_count} | Lift: {r.lift}x
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Slide-out Cluster History Modal / Drawer */}
      {selectedClusterId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4 animate-fade-in">
          <div className="bg-white rounded-3xl border border-slate-200 shadow-2xl max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden">
            {/* Modal Header */}
            <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-bold text-slate-900">
                    {clusterHistory?.cluster_name || selectedClusterId}
                  </h3>
                  {clusterHistory?.discovery_type === 'autonomous_discovery' && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 border border-purple-200">
                      Autonomous Discovery
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 font-mono mt-0.5">
                  Cluster ID: {selectedClusterId}
                </p>
              </div>
              <button
                onClick={() => setSelectedClusterId(null)}
                className="w-8 h-8 rounded-full hover:bg-slate-200 flex items-center justify-center text-slate-500 hover:text-slate-800 transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Body: Timeline */}
            <div className="p-6 overflow-y-auto space-y-6">
              {historyLoading ? (
                <div className="py-12 flex flex-col items-center justify-center gap-2 text-slate-400">
                  <RefreshCw className="w-6 h-6 animate-spin text-purple-600" />
                  <p className="text-xs">Loading cluster lifecycle timeline...</p>
                </div>
              ) : clusterHistory ? (
                <div className="space-y-4">
                  <div className="text-xs font-bold text-slate-900 uppercase tracking-wider text-[10px]">
                    Cross-Scan Evolutionary Timeline
                  </div>
                  <div className="relative pl-6 border-l-2 border-purple-200 space-y-6">
                    {clusterHistory.timeline.map((event, idx) => (
                      <div key={idx} className="relative group">
                        <div className="absolute -left-[31px] top-1 w-3.5 h-3.5 rounded-full bg-purple-600 border-2 border-white ring-2 ring-purple-100" />
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-slate-900 font-mono">
                              Round {event.round}: {event.event}
                            </span>
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-mono">
                              {event.status}
                            </span>
                          </div>
                          <p className="text-xs text-slate-600 leading-relaxed">
                            {event.description}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end">
              <button
                onClick={() => setSelectedClusterId(null)}
                className="px-5 py-2 rounded-xl bg-slate-900 text-white font-semibold text-xs hover:bg-slate-800 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
