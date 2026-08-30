'use client';

import React from 'react';
import { Activity, Sparkles, AlertTriangle, ArrowUpRight } from 'lucide-react';

export function TrajectoryLineChart() {
  return (
    <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-600" />
              Drift Shock & Autonomous Adaptation Trajectory
            </h3>
            <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              +246% Recovery
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Visualizing net savings collapse under drift shock versus autonomous recovery via Residual Miner clustering.
          </p>
        </div>
      </div>

      {/* Responsive SVG Spline Line Graph */}
      <div className="relative w-full overflow-hidden rounded-xl bg-slate-950 p-6 text-white border border-slate-800">
        {/* Background Gridlines */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_2.5rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-30" />

        <div className="relative z-10 space-y-6">
          {/* Top Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 space-y-1">
              <span className="text-[11px] font-mono text-slate-400">1. Genesis Baseline</span>
              <p className="text-lg font-extrabold text-sky-400 font-mono">₹24,312.15</p>
              <p className="text-[10.5px] text-slate-400">Days 0–55 Pre-drift training</p>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/90 border border-amber-500/30 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono text-amber-400">2. Drift Shock Collapse</span>
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-amber-950 text-amber-300 border border-amber-700/50">
                  -72.99%
                </span>
              </div>
              <p className="text-lg font-extrabold text-amber-400 font-mono">₹6,567.62</p>
              <p className="text-[10.5px] text-slate-400">Static rules on Days 56–75</p>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/90 border border-emerald-500/40 space-y-1 shadow-[0_0_20px_rgba(16,185,129,0.15)]">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono text-emerald-400">3. Evolved Recovery</span>
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-300 border border-emerald-700/50">
                  +246.16%
                </span>
              </div>
              <p className="text-lg font-extrabold text-emerald-300 font-mono">₹22,734.77</p>
              <p className="text-[10.5px] text-slate-400">Adapted with Residual Miner</p>
            </div>
          </div>

          {/* SVG Line Graph */}
          <div className="pt-2 pb-2">
            <svg viewBox="0 0 700 180" className="w-full h-40 overflow-visible">
              <defs>
                <linearGradient id="lineGlow" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#38bdf8" />
                  <stop offset="45%" stopColor="#f59e0b" />
                  <stop offset="100%" stopColor="#10b981" />
                </linearGradient>
                <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Shaded Area */}
              <path
                d="M 50 40 L 350 140 L 650 48 L 650 170 L 50 170 Z"
                fill="url(#areaGradient)"
              />

              {/* Trajectory Path */}
              <path
                d="M 50 40 Q 200 60 350 140 Q 500 130 650 48"
                fill="none"
                stroke="url(#lineGlow)"
                strokeWidth="4"
                strokeLinecap="round"
              />

              {/* Data Points */}
              {/* Point 1: Genesis */}
              <circle cx="50" cy="40" r="7" className="fill-sky-400 stroke-slate-950 stroke-2" />
              <circle cx="50" cy="40" r="14" className="fill-sky-400/20 animate-ping" />
              <text x="50" y="24" textAnchor="middle" className="text-[11px] font-mono font-bold fill-sky-300">
                ₹24,312
              </text>

              {/* Point 2: Drift Shock */}
              <circle cx="350" cy="140" r="7" className="fill-amber-400 stroke-slate-950 stroke-2" />
              <circle cx="350" cy="140" r="14" className="fill-amber-400/20 animate-ping" />
              <text x="350" y="165" textAnchor="middle" className="text-[11px] font-mono font-bold fill-amber-300">
                ₹6,567 (-73%)
              </text>

              {/* Point 3: Evolved Recovery */}
              <circle cx="650" cy="48" r="8" className="fill-emerald-400 stroke-slate-950 stroke-2" />
              <circle cx="650" cy="48" r="16" className="fill-emerald-400/30 animate-pulse" />
              <text x="650" y="30" textAnchor="middle" className="text-[11px] font-mono font-bold fill-emerald-300">
                ₹22,734 (+246%)
              </text>
            </svg>
          </div>
        </div>
      </div>

      {/* Scientific Context */}
      <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 flex items-start gap-2.5">
        <Sparkles className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
        <p className="leading-relaxed text-[11.5px]">
          <strong>Mechanism Proof:</strong> When unflagged promotional bursts shifted fraud distribution on Days 56–75, static pre-drift rules collapsed by 72.99%. Autonomous Residual Mining extracted the missed RTO clusters and synthesized promo velocity shields, recovering net savings to ₹22,734.77 (+246.16% recovery lift).
        </p>
      </div>
    </div>
  );
}
