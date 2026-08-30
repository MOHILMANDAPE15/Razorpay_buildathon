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
import { DiscoveredClustersBarChart } from '@/components/charts/DiscoveredClustersBarChart';
import { SignificanceThresholdChart } from '@/components/charts/SignificanceThresholdChart';

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

      {/* Header KPI Strip (Human-Friendly Terms) */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
          <span className="text-xs text-slate-500 font-medium block">Delivered Orders Scanned</span>
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
          <span className="text-xs text-slate-500 font-medium block">Uncaught Bounced Orders</span>
          <div className="text-xl font-bold font-mono text-rose-600 mt-1">
            {loading || !meta ? (
              <span className="inline-block h-6 w-16 bg-slate-200 animate-pulse rounded-md mt-1" />
            ) : (
              meta.total_false_negatives.toLocaleString()
            )}
          </div>
          <span className="text-[11px] text-slate-400 font-mono mt-0.5 block">RTO fraud missed by old rules</span>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
          <span className="text-xs text-slate-500 font-medium block">Uncaught Miss Rate</span>
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
          <span className="text-xs text-slate-500 font-medium block">Verified Real Threats</span>
          <div className="text-xl font-bold font-mono text-purple-600 mt-1">
            {loading || !meta ? (
              <span className="inline-block h-6 w-10 bg-slate-200 animate-pulse rounded-md mt-1" />
            ) : (
              clusters.length
            )}
          </div>
          <span className="text-[11px] text-purple-600/80 font-mono mt-0.5 block">&gt;95% Statistical Certainty</span>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
          <span className="text-xs text-slate-500 font-medium block">Fake Patterns Blocked</span>
          <div className="text-xl font-bold font-mono text-slate-700 mt-1">
            {loading || !meta ? (
              <span className="inline-block h-6 w-10 bg-slate-200 animate-pulse rounded-md mt-1" />
            ) : (
              rejected.length
            )}
          </div>
          <span className="text-[11px] text-slate-400 font-mono mt-0.5 block">Prevented random coincidences</span>
        </div>
      </div>

      {/* Visual Discovered Clusters Component (Single Unified View) */}
      {loading ? (
        <div className="p-12 rounded-2xl bg-white border border-slate-200 text-center space-y-3 animate-pulse">
          <div className="h-6 w-48 bg-slate-200 rounded mx-auto" />
          <div className="h-4 w-96 bg-slate-100 rounded mx-auto" />
        </div>
      ) : clusters.length === 0 ? (
        <div className="p-12 rounded-2xl bg-white border border-slate-200 text-center space-y-3">
          <Activity className="w-8 h-8 text-slate-300 mx-auto" />
          <p className="text-sm font-semibold text-slate-700">No unhandled fraud clusters found</p>
          <p className="text-xs text-slate-500">Current champion ensemble has successfully mitigated all active fraud patterns.</p>
          <button
            onClick={() => loadScan(activeSplit)}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-semibold shadow-xs transition"
          >
            Re-scan Split
          </button>
        </div>
      ) : (
        <DiscoveredClustersBarChart
          clusters={clusters}
          selectedClusterId={selectedClusterId}
          onSelectCluster={handleSelectCluster}
        />
      )}

      {/* Visual Significance Threshold Plot (Explains Chi-Square & Protects GMV) */}
      <SignificanceThresholdChart rejectedCandidates={rejected} />

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
