'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Activity, 
  AlertTriangle, 
  ShieldAlert, 
  TrendingUp, 
  Zap, 
  RefreshCw, 
  Sliders, 
  CheckCircle2,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Radio,
} from 'lucide-react';
import clsx from 'clsx';
import { 
  fetchMonitorStatus, 
  fetchMonitorHistory, 
  triggerTrafficSimulation, 
  MonitorSnapshot, 
  TimeSeriesPoint 
} from '@/lib/api';

const WINDOW_VIEW_SIZE = 40;

export default function SpikeMonitorPage() {
  const [snapshot, setSnapshot] = useState<MonitorSnapshot | null>(null);
  const [history, setHistory] = useState<TimeSeriesPoint[]>([]);
  const [simulating, setSimulating] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [windowOffset, setWindowOffset] = useState(0);
  const [isLivePinned, setIsLivePinned] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [snap, hist] = await Promise.all([
        fetchMonitorStatus(),
        fetchMonitorHistory(500),
      ]);
      setSnapshot(snap);
      setHistory(hist);
    } catch (err) {
      console.error('Failed to load monitor data:', err);
    }
  }, []);

  // Update windowOffset when new history arrives and user is pinned to live
  useEffect(() => {
    if (isLivePinned && history.length > 0) {
      const maxOffset = Math.max(0, history.length - WINDOW_VIEW_SIZE);
      setWindowOffset(maxOffset);
    }
  }, [history, isLivePinned]);

  useEffect(() => {
    loadData();
    if (!autoRefresh) return;
    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, [loadData, autoRefresh]);

  const handleSimulate = async (spikeRate: number, totalEvents: number) => {
    setSimulating(true);
    try {
      await triggerTrafficSimulation(totalEvents, spikeRate);
      setIsLivePinned(true);
      await loadData();
    } catch (err) {
      console.error('Simulation failed:', err);
    } finally {
      setSimulating(false);
    }
  };

  const maxOffset = useMemo(() => Math.max(0, history.length - WINDOW_VIEW_SIZE), [history.length]);

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = Number(e.target.value);
    setWindowOffset(val);
    if (val >= maxOffset) {
      setIsLivePinned(true);
    } else {
      setIsLivePinned(false);
    }
  };

  const handleJumpToStart = () => {
    setWindowOffset(0);
    setIsLivePinned(false);
  };

  const handlePrevPage = () => {
    setWindowOffset((prev) => Math.max(0, prev - WINDOW_VIEW_SIZE));
    setIsLivePinned(false);
  };

  const handleNextPage = () => {
    setWindowOffset((prev) => {
      const next = Math.min(maxOffset, prev + WINDOW_VIEW_SIZE);
      if (next >= maxOffset) setIsLivePinned(true);
      return next;
    });
  };

  const handleJumpToLive = () => {
    setWindowOffset(maxOffset);
    setIsLivePinned(true);
  };

  const displayedPoints = useMemo(() => {
    if (history.length === 0) return [];
    return history.slice(windowOffset, windowOffset + WINDOW_VIEW_SIZE);
  }, [history, windowOffset]);

  const startEventNumber = displayedPoints.length > 0 ? (displayedPoints[0].step || (windowOffset + 1)) : 0;
  const endEventNumber = displayedPoints.length > 0 ? (displayedPoints[displayedPoints.length - 1].step || (windowOffset + displayedPoints.length)) : 0;

  // Segment shortcuts for fast jumps
  const segments = useMemo(() => {
    if (history.length <= WINDOW_VIEW_SIZE) return [];
    const segList: { label: string; offset: number }[] = [];
    for (let i = 0; i < history.length; i += WINDOW_VIEW_SIZE) {
      const start = i + 1;
      const end = Math.min(i + WINDOW_VIEW_SIZE, history.length);
      const actualOffset = Math.min(i, maxOffset);
      segList.push({ label: `#${start}–#${end}`, offset: actualOffset });
    }
    return segList;
  }, [history.length, maxOffset]);

  const isCritical = snapshot?.status === 'CRITICAL';
  const isWarning = snapshot?.status === 'WARNING';
  const activeWindowSize = snapshot?.window_size || WINDOW_VIEW_SIZE;

  return (
    <div className="space-y-8 animate-fade-in font-sans">
      {/* Top Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600">
              <Activity className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
                  Real-Time Spike Monitor
                </h1>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1.5 font-mono font-bold">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                  Live Telemetry
                </span>
              </div>
              <p className="text-sm text-slate-600 mt-1 max-w-3xl leading-relaxed">
                Sliding-window binomial Z-score and CUSUM change-point detector tracking live checkout scoring events across 40-order sliding intervals.
              </p>
            </div>
          </div>
        </div>

        {/* Action Toolbar */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-3.5 py-2 text-xs font-bold rounded-xl border transition-all flex items-center gap-2 shadow-xs cursor-pointer ${
              autoRefresh 
                ? 'bg-indigo-50 text-indigo-700 border-indigo-200' 
                : 'bg-white text-slate-600 border-slate-200 hover:text-slate-900'
            }`}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${autoRefresh ? 'animate-spin text-indigo-600' : ''}`} />
            {autoRefresh ? 'Auto-Polling (3s)' : 'Polling Paused'}
          </button>
          <button
            onClick={loadData}
            className="px-3.5 py-2 text-xs font-bold rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 shadow-xs transition flex items-center gap-1.5 cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5 text-indigo-600" />
            Refresh
          </button>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Status Card */}
        <div className={`p-5 rounded-2xl border transition-all shadow-xs ${
          isCritical 
            ? 'border-rose-300 bg-rose-50/50 shadow-rose-500/5' 
            : isWarning 
              ? 'border-amber-300 bg-amber-50/50' 
              : 'border-emerald-300 bg-emerald-50/40'
        }`}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">Stream Health</span>
            {isCritical ? (
              <ShieldAlert className="w-5 h-5 text-rose-600 animate-bounce" />
            ) : isWarning ? (
              <AlertTriangle className="w-5 h-5 text-amber-600" />
            ) : (
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            )}
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className={`text-2xl font-black ${
              isCritical ? 'text-rose-600' : isWarning ? 'text-amber-600' : 'text-emerald-700'
            }`}>
              {snapshot?.status || 'HEALTHY'}
            </span>
            <span className="text-xs text-slate-500 font-mono">
              ({snapshot?.total_orders_processed || history.length || 0} total)
            </span>
          </div>
          <p className="text-xs text-slate-600 mt-2">
            {isCritical 
              ? 'Critical shift: Z-score breached threshold.' 
              : isWarning 
                ? 'Elevated flag rate detected.' 
                : 'Scoring stream within expected variance.'}
          </p>
        </div>

        {/* Flag Rate Card */}
        <div className="p-5 rounded-2xl border border-slate-200/90 bg-white shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">Rolling Flag Rate</span>
            <TrendingUp className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-black text-slate-900 font-mono">
              {((snapshot?.current_flag_rate || 0) * 100).toFixed(1)}%
            </span>
            <span className="text-xs text-slate-500">
              vs {((snapshot?.baseline_expected_rate || 0.08) * 100).toFixed(1)}% base
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Sliding window size: <span className="font-mono font-bold text-slate-800">{activeWindowSize}</span> orders
          </p>
        </div>

        {/* Z-Score Card */}
        <div className="p-5 rounded-2xl border border-slate-200/90 bg-white shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">Drift Z-Score</span>
            <Sliders className="w-4 h-4 text-sky-600" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-black text-sky-700 font-mono">
              {snapshot?.z_score?.toFixed(2) || '0.00'}σ
            </span>
            <span className="text-xs text-slate-500">
              (Critical at &ge; 2.50σ)
            </span>
          </div>
          <div className="mt-3 w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
            <div 
              className={`h-full transition-all duration-500 ${
                (snapshot?.z_score || 0) >= 2.5 
                  ? 'bg-rose-500' 
                  : (snapshot?.z_score || 0) >= 1.75 
                    ? 'bg-amber-500' 
                    : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(100, Math.max(5, ((snapshot?.z_score || 0) / 4) * 100))}%` }}
            />
          </div>
        </div>

        {/* CUSUM Accumulator */}
        <div className="p-5 rounded-2xl border border-slate-200/90 bg-white shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">CUSUM Anomaly</span>
            <Zap className="w-4 h-4 text-purple-600" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-black text-purple-700 font-mono">
              {snapshot?.cusum_positive?.toFixed(3) || '0.000'}
            </span>
            <span className="text-xs text-slate-500">
              / {snapshot?.cusum_threshold || 0.15}
            </span>
          </div>
          <div className="mt-3 w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
            <div 
              className="h-full bg-purple-600 transition-all duration-500"
              style={{ width: `${Math.min(100, ((snapshot?.cusum_positive || 0) / (snapshot?.cusum_threshold || 0.15)) * 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Real-Time Chart & Diagnostic Controls */}
        <div className="lg:col-span-2 space-y-6">
          {/* Chart Card */}
          <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-indigo-600" />
                  Rolling Flag Rate Trajectory
                  {history.length > 0 && (
                    <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
                      Events #{startEventNumber}–#{endEventNumber}
                    </span>
                  )}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Showing 40-order sliding window interval. Baseline: 8.0%; red threshold is upper 2.5σ bound.
                </p>
              </div>

              <div className="flex items-center gap-2">
                {isLivePinned ? (
                  <span className="text-[11px] font-mono font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    Live View (Latest 40)
                  </span>
                ) : (
                  <button
                    onClick={handleJumpToLive}
                    className="text-[11px] font-mono font-bold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 px-2.5 py-1 rounded-full flex items-center gap-1.5 transition cursor-pointer"
                  >
                    <Radio className="w-3 h-3 text-indigo-600" />
                    Jump to Live
                  </button>
                )}

                <span className="text-xs font-mono text-slate-500 font-medium px-2 py-1 bg-slate-50 border border-slate-200 rounded-lg">
                  {displayedPoints.length} of {history.length} events
                </span>
              </div>
            </div>

            {/* Interactive Timeline Navigation & Slider for 40-event windows */}
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                <span className="font-bold text-slate-700 flex items-center gap-1.5 font-mono">
                  <Sliders className="w-3.5 h-3.5 text-indigo-600" />
                  Timeline Scrubber: Slide across {history.length} session events
                </span>
                <span className="text-[11px] font-mono text-slate-500 font-medium">
                  Showing Window Offset: [{windowOffset + 1} – {Math.min(windowOffset + WINDOW_VIEW_SIZE, history.length)}]
                </span>
              </div>

              {/* Slider Track */}
              <div className="space-y-1.5">
                <input
                  type="range"
                  min={0}
                  max={maxOffset}
                  value={windowOffset}
                  disabled={history.length <= WINDOW_VIEW_SIZE}
                  onChange={handleSliderChange}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600 disabled:opacity-40 disabled:cursor-not-allowed"
                />
                <div className="flex justify-between text-[10px] font-mono text-slate-400">
                  <span>Start (#1)</span>
                  {history.length > WINDOW_VIEW_SIZE && (
                    <span>Midpoint (#{Math.floor(history.length / 2)})</span>
                  )}
                  <span>Latest (#{history.length || 40})</span>
                </div>
              </div>

              {/* Navigation Stepper Buttons */}
              <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={handleJumpToStart}
                    disabled={windowOffset === 0}
                    className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 text-[11px] font-semibold flex items-center gap-1 transition disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
                    title="Jump to Earliest 40 Events"
                  >
                    <ChevronsLeft className="w-3.5 h-3.5" />
                    First 40
                  </button>
                  <button
                    onClick={handlePrevPage}
                    disabled={windowOffset === 0}
                    className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 text-[11px] font-semibold flex items-center gap-1 transition disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
                    title="Previous 40 Events"
                  >
                    <ChevronLeft className="w-3.5 h-3.5" />
                    Prev 40
                  </button>
                  <button
                    onClick={handleNextPage}
                    disabled={windowOffset >= maxOffset}
                    className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 text-[11px] font-semibold flex items-center gap-1 transition disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
                    title="Next 40 Events"
                  >
                    Next 40
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={handleJumpToLive}
                    disabled={windowOffset >= maxOffset && isLivePinned}
                    className="px-2.5 py-1 rounded-lg bg-indigo-50 border border-indigo-200 hover:bg-indigo-100 text-indigo-700 text-[11px] font-semibold flex items-center gap-1 transition disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
                    title="Jump to Latest 40 Events"
                  >
                    Latest 40
                    <ChevronsRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* Quick Segment Pills */}
                {segments.length > 1 && (
                  <div className="flex items-center gap-1 overflow-x-auto max-w-full">
                    {segments.map((seg, sIdx) => {
                      const isCurrentSeg = windowOffset >= seg.offset && windowOffset < seg.offset + WINDOW_VIEW_SIZE;
                      return (
                        <button
                          key={sIdx}
                          onClick={() => {
                            setWindowOffset(seg.offset);
                            if (seg.offset >= maxOffset) setIsLivePinned(true);
                            else setIsLivePinned(false);
                          }}
                          className={clsx(
                            'px-2 py-0.5 rounded-md text-[10px] font-mono font-bold transition cursor-pointer',
                            isCurrentSeg
                              ? 'bg-slate-900 text-white shadow-xs'
                              : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
                          )}
                        >
                          {seg.label}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* Custom SVG Line Chart */}
            <div className="h-56 w-full bg-slate-50 border border-slate-200 rounded-xl p-4 relative overflow-hidden flex flex-col justify-end">
              {displayedPoints.length === 0 ? (
                <div className="flex items-center justify-center h-full text-slate-400 text-xs font-mono">
                  No telemetry recorded yet. Use the simulation buttons below to generate test events.
                </div>
              ) : (
                <div className="h-full w-full flex items-end gap-1.5 relative pt-6 pb-4">
                  {/* Baseline reference line (8%) */}
                  <div className="absolute left-0 right-0 bottom-[25%] border-b border-dashed border-emerald-500/40 z-0 pointer-events-none" />
                  {/* Upper bound reference line */}
                  <div className="absolute left-0 right-0 top-[25%] border-b border-dashed border-rose-500/40 z-0 pointer-events-none" />

                  {displayedPoints.map((point, idx) => {
                    const heightPct = Math.min(100, Math.max(8, point.flag_rate * 160));
                    const isSpike = point.status === 'CRITICAL';
                    const isWarn = point.status === 'WARNING';
                    return (
                      <div
                        key={idx}
                        className="flex-1 flex flex-col items-center justify-end h-full group relative z-10"
                      >
                        <div
                          className={`w-full rounded-t-sm transition-all duration-300 ${
                            isSpike 
                              ? 'bg-rose-500 shadow-sm shadow-rose-500/30' 
                              : isWarn 
                                ? 'bg-amber-500' 
                                : 'bg-indigo-600 hover:bg-indigo-700'
                          }`}
                          style={{ height: `${heightPct}%` }}
                        />
                        {/* Tooltip on hover */}
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute bottom-full mb-2 pointer-events-none bg-slate-900 border border-slate-700 text-white text-[10px] rounded p-1.5 shadow-xl whitespace-nowrap z-20 font-mono">
                          <div>Event: #{point.step || (windowOffset + idx + 1)}</div>
                          <div>Rate: {(point.flag_rate * 100).toFixed(1)}%</div>
                          <div>Z-Score: {point.z_score.toFixed(2)}σ</div>
                          <div>Status: {point.status}</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Chart Legend */}
              <div className="flex items-center justify-between text-[10px] text-slate-500 border-t border-slate-200 pt-2 font-mono">
                <div className="flex items-center gap-4">
                  <span className="flex items-center gap-1 text-emerald-700 font-semibold">
                    <span className="w-2 h-0.5 bg-emerald-500 inline-block" /> Baseline: 8.0%
                  </span>
                  <span className="flex items-center gap-1 text-rose-700 font-semibold">
                    <span className="w-2 h-0.5 bg-rose-500 inline-block" /> Threshold (2.5σ)
                  </span>
                  <span className="flex items-center gap-1 text-indigo-700 font-semibold">
                    <span className="w-2 h-2 bg-indigo-600 inline-block rounded-xs" /> Rolling Rate
                  </span>
                </div>
                <span>Sliding Window: {activeWindowSize} orders</span>
              </div>
            </div>
          </div>

          {/* Traffic Simulation Controls */}
          <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-5">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Sliders className="w-4 h-4 text-indigo-600" />
                Traffic Simulation
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Inject synthetic order events into the detector to watch how it responds in real time.
              </p>
            </div>

            {/* What these buttons do */}
            <div className="rounded-xl border border-indigo-100 bg-indigo-50/40 p-4 space-y-2">
              <p className="text-xs font-bold text-indigo-800 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                What happens when you click?
              </p>
              <ul className="text-[11px] text-slate-700 space-y-1.5 leading-relaxed">
                <li className="flex items-start gap-1.5">
                  <span className="text-emerald-600 font-bold mt-0.5">→</span>
                  <span><strong className="text-slate-900">Stream Genuine Traffic</strong> — pushes 25 normal orders through the detector. The rolling flag rate stays near the 8% baseline, the Z-score stays low, and the chart bars stay blue. Status remains <span className="font-mono font-bold text-emerald-700">HEALTHY</span>.</span>
                </li>
                <li className="flex items-start gap-1.5">
                  <span className="text-rose-600 font-bold mt-0.5">→</span>
                  <span><strong className="text-slate-900">Trigger RTO Drift Burst</strong> — pushes 30 high-fraud orders (55% flag rate). The rolling window spikes, Z-score crosses the 2.5σ critical threshold, bars turn red, and the system fires <span className="font-mono font-bold text-rose-700">CRITICAL_SPIKE</span> alerts in the panel on the right. This is how real adversarial fraud drift looks to the engine.</span>
                </li>
              </ul>
              <p className="text-[10px] text-slate-500 pt-1">
                No real orders are affected — these events only update the in-memory sliding window used for drift detection testing.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <button
                disabled={simulating}
                onClick={() => handleSimulate(0.08, 25)}
                className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/40 hover:bg-emerald-50/80 text-left transition-all group disabled:opacity-50 shadow-xs cursor-pointer"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-emerald-800 flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    Stream Genuine Traffic
                  </span>
                  <span className="text-[10px] font-mono font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full">
                    ~8% flagged
                  </span>
                </div>
                <p className="text-[11px] text-slate-600 group-hover:text-slate-900">
                  25 normal orders · keeps system in healthy range · Z-score stays below 1.0
                </p>
              </button>

              <button
                disabled={simulating}
                onClick={() => handleSimulate(0.55, 30)}
                className="p-4 rounded-xl border border-rose-200 bg-rose-50/40 hover:bg-rose-50/80 text-left transition-all group disabled:opacity-50 shadow-xs cursor-pointer"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-rose-800 flex items-center gap-1.5">
                    <ShieldAlert className="w-4 h-4 text-rose-600 animate-pulse" />
                    Trigger RTO Drift Burst
                  </span>
                  <span className="text-[10px] font-mono font-bold bg-rose-100 text-rose-800 px-2 py-0.5 rounded-full">
                    ~55% flagged
                  </span>
                </div>
                <p className="text-[11px] text-slate-600 group-hover:text-slate-900">
                  30 attack-pattern orders · breaches 2.5σ · fires CRITICAL alerts
                </p>
              </button>
            </div>

            {simulating && (
              <div className="flex items-center gap-2 text-xs text-indigo-700 font-mono font-bold animate-pulse">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Streaming events to detector...
              </div>
            )}
          </div>
        </div>

        {/* Right 1 Col: Active Drift Alerts */}
        <div className="space-y-4">
          <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                Active Alerts ({snapshot?.active_alerts?.length || 0})
              </h3>
              <span className="text-xs text-slate-500 font-mono">
                Real-time
              </span>
            </div>

            {(!snapshot?.active_alerts || snapshot.active_alerts.length === 0) ? (
              <div className="py-12 text-center text-slate-400 space-y-2">
                <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto" />
                <p className="text-xs font-bold text-slate-800">Zero Active Anomalies</p>
                <p className="text-[11px] text-slate-500 max-w-xs mx-auto">
                  Traffic is behaving within expected pre-drift bounds. No autonomous evolution trigger needed.
                </p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
                {snapshot.active_alerts.map((alert, idx) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-xl border text-xs space-y-2.5 transition-all ${
                      alert.severity === 'CRITICAL_SPIKE'
                        ? 'border-rose-200 bg-rose-50/60 text-rose-900'
                        : 'border-amber-200 bg-amber-50/60 text-amber-900'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold font-mono text-[11px] uppercase tracking-wider flex items-center gap-1.5">
                        <ShieldAlert className="w-3.5 h-3.5" />
                        {alert.severity}
                      </span>
                      <span className="text-[10px] opacity-75 font-mono">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                    </div>

                    <p className="text-xs leading-relaxed text-slate-800 font-medium">
                      {alert.message}
                    </p>

                    <div className="p-2.5 rounded-lg bg-white border border-slate-200 text-[10px] space-y-1 shadow-xs">
                      <div className="font-bold text-indigo-700 flex items-center gap-1">
                        <Sparkles className="w-3 h-3 text-indigo-600" />
                        Recommended Mitigation:
                      </div>
                      <p className="text-slate-600">
                        {alert.recommended_action}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}