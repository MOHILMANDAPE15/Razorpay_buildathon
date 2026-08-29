'use client';

import React, { useState } from 'react';
import { 
  RotateCcw, 
  Sparkles, 
  ShieldCheck, 
  Cpu, 
  GitBranch, 
  Activity, 
  Database, 
  Filter, 
  Zap, 
  ChevronDown, 
  ChevronUp, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  Compass, 
  Radio, 
  ShieldAlert,
  ArrowRight,
  RefreshCw,
  Info
} from 'lucide-react';
import InfoTooltip from '@/components/InfoTooltip';

type ActiveDetail = 'none' | 'evolution' | 'triggers';

export default function ArchitectureDiagram() {
  const [activeDetail, setActiveDetail] = useState<ActiveDetail>('none');

  const toggleDetail = (target: 'evolution' | 'triggers') => {
    setActiveDetail((prev) => (prev === target ? 'none' : target));
  };

  return (
    <div className="rounded-3xl border border-slate-200 bg-white shadow-xs p-6 sm:p-8 space-y-6 animate-fade-in">
      {/* Header with Title and Mode Toggles */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
              Interactive System Architecture
            </span>
            <h2 className="text-lg font-bold text-slate-900">
              Closed-Loop Autonomous Flowchart
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Hover over any badge for glossary definitions. Click <strong>Core Evolution Loop</strong> or <strong>Triggers</strong> to expand internal multi-agent flowcharts.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => toggleDetail('evolution')}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-2xs ${
              activeDetail === 'evolution'
                ? 'bg-purple-600 text-white shadow-xs'
                : 'bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200'
            }`}
          >
            <Cpu className="w-3.5 h-3.5" />
            Core Evolution Loop
            {activeDetail === 'evolution' ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          <button
            onClick={() => toggleDetail('triggers')}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-2xs ${
              activeDetail === 'triggers'
                ? 'bg-amber-600 text-white shadow-xs'
                : 'bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200'
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            Triggers & Mining
            {activeDetail === 'triggers' ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* 1. TOP-LEVEL 7-STAGE FLOWCHART (PERFECT 920px FIT - NO SCROLL CUTOFF) */}
      <div className="relative p-5 sm:p-6 rounded-2xl bg-slate-50 border border-slate-200 overflow-x-auto">
        <div className="min-w-[880px]">
          <svg viewBox="0 0 920 220" className="w-full h-auto font-sans select-none overflow-visible">
            <defs>
              {/* Arrowhead Markers */}
              <marker id="arr-slate" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#64748b" />
              </marker>
              <marker id="arr-emerald" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#059669" />
              </marker>
              <marker id="arr-sky" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#0284c7" />
              </marker>
              <marker id="arr-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#d97706" />
              </marker>
              <marker id="arr-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#7c3aed" />
              </marker>

              {/* Gradient for Return Loop */}
              <linearGradient id="return-gradient" x1="100%" y1="0%" x2="0%" y2="0%">
                <stop offset="0%" stopColor="#7c3aed" />
                <stop offset="50%" stopColor="#6366f1" />
                <stop offset="100%" stopColor="#059669" />
              </linearGradient>
            </defs>

            {/* CONNECTING ARROWS & PILL BADGES */}
            {/* 1. New Order -> Frozen Ensemble */}
            <path d="M 130 65 L 163 65" stroke="#64748b" strokeWidth="2" fill="none" markerEnd="url(#arr-slate)" />
            <rect x="133" y="38" width="30" height="16" rx="4" fill="#ffffff" stroke="#cbd5e1" strokeWidth="1" />
            <text x="148" y="49" textAnchor="middle" className="text-[8.5px] fill-slate-600 font-mono font-bold">stream</text>

            {/* 2. Frozen Ensemble -> 3-Way Router */}
            <path d="M 284 65 L 317 65" stroke="#059669" strokeWidth="2" fill="none" markerEnd="url(#arr-emerald)" />
            <rect x="287" y="38" width="28" height="16" rx="4" fill="#ecfdf5" stroke="#a7f3d0" strokeWidth="1" />
            <text x="301" y="49" textAnchor="middle" className="text-[8.5px] fill-emerald-800 font-mono font-bold">score</text>

            {/* 3. 3-Way Router -> Outcomes */}
            <path d="M 438 65 L 471 65" stroke="#0284c7" strokeWidth="2" fill="none" markerEnd="url(#arr-sky)" />
            <rect x="441" y="38" width="30" height="16" rx="4" fill="#f0f9ff" stroke="#bae6fd" strokeWidth="1" />
            <text x="456" y="49" textAnchor="middle" className="text-[8.5px] fill-sky-800 font-mono font-bold">action</text>

            {/* 4. Outcomes -> Triggers */}
            <path d="M 592 65 L 625 65" stroke="#64748b" strokeWidth="2" fill="none" markerEnd="url(#arr-slate)" />
            <rect x="595" y="38" width="30" height="16" rx="4" fill="#ffffff" stroke="#cbd5e1" strokeWidth="1" />
            <text x="610" y="49" textAnchor="middle" className="text-[8.5px] fill-slate-600 font-mono font-bold">mature</text>

            {/* 5. Triggers -> Core Evolution Loop */}
            <path d="M 746 65 L 779 65" stroke="#d97706" strokeWidth="2" fill="none" markerEnd="url(#arr-amber)" />
            <rect x="749" y="38" width="30" height="16" rx="4" fill="#fffbeb" stroke="#fde68a" strokeWidth="1" />
            <text x="764" y="49" textAnchor="middle" className="text-[8.5px] fill-amber-800 font-mono font-bold">agenda</text>

            {/* 6. VISIBLE RETURN LOOP-BACK ARROW (Node 6 to Node 2) */}
            <path 
              d="M 845 105 C 845 180, 227 180, 227 113" 
              stroke="url(#return-gradient)" 
              strokeWidth="2.5" 
              strokeDasharray="6 4"
              fill="none" 
              markerEnd="url(#arr-emerald)" 
            />
            {/* Condition Label on the Return Loop */}
            <rect x="300" y="166" width="320" height="26" rx="13" fill="#ffffff" stroke="#6366f1" strokeWidth="1.5" className="shadow-xs" />
            <text x="460" y="183" textAnchor="middle" className="text-[10px] fill-indigo-800 font-mono font-bold">
              ↻ if promoted / atomic serving weights update &amp; snapshot
            </text>

            {/* ========================================================================= */}
            {/* NODE 1: New Order Stream */}
            {/* ========================================================================= */}
            <g transform="translate(15, 25)">
              <rect width="115" height="80" rx="14" fill="#ffffff" stroke="#cbd5e1" strokeWidth="1.5" className="shadow-xs hover:stroke-indigo-400 transition" />
              <text x="12" y="26" className="text-[11px] font-bold fill-slate-900">1. New Order</text>
              <text x="12" y="44" className="text-[9px] font-mono fill-slate-600">Live Traffic Stream</text>
              <text x="12" y="62" className="text-[8.5px] font-mono fill-indigo-600 font-semibold">&lt;10ms Scoring</text>
            </g>

            {/* ========================================================================= */}
            {/* NODE 2: Frozen Serving Ensemble */}
            {/* ========================================================================= */}
            <g transform="translate(169, 25)">
              <rect width="115" height="80" rx="14" fill="#ffffff" stroke="#059669" strokeWidth="2.5" className="shadow-xs" />
              <text x="12" y="26" className="text-[11px] font-bold fill-emerald-950">2. Frozen Model</text>
              <text x="12" y="44" className="text-[9px] font-mono fill-emerald-700 font-bold">Locked AST Rules</text>
              <text x="12" y="62" className="text-[8.5px] font-mono fill-emerald-600">Serving Snapshot</text>
            </g>

            {/* ========================================================================= */}
            {/* NODE 3: 3-Way Decision Router */}
            {/* ========================================================================= */}
            <g transform="translate(323, 25)">
              <rect width="115" height="80" rx="14" fill="#ffffff" stroke="#0284c7" strokeWidth="2" className="shadow-xs" />
              <text x="12" y="26" className="text-[11px] font-bold fill-sky-950">3. 3-Way Router</text>
              <text x="12" y="44" className="text-[9px] font-mono fill-sky-700 font-bold">Auto vs Review</text>
              <text x="12" y="62" className="text-[8.5px] font-mono fill-sky-600">T=0.70 / T=0.35</text>
            </g>

            {/* ========================================================================= */}
            {/* NODE 4: Outcome Logged & Maturation */}
            {/* ========================================================================= */}
            <g transform="translate(477, 25)">
              <rect width="115" height="80" rx="14" fill="#ffffff" stroke="#94a3b8" strokeWidth="1.5" className="shadow-xs" />
              <text x="12" y="26" className="text-[11px] font-bold fill-slate-900">4. Outcomes</text>
              <text x="12" y="44" className="text-[9px] font-mono fill-slate-700 font-bold">5-Day Mature</text>
              <text x="12" y="62" className="text-[8.5px] font-mono fill-slate-500">Delivery vs RTO</text>
            </g>

            {/* ========================================================================= */}
            {/* NODE 5: Autonomous Triggers Sentinel (Clickable) */}
            {/* ========================================================================= */}
            <g transform="translate(631, 25)" className="cursor-pointer" onClick={() => toggleDetail('triggers')}>
              <rect 
                width="115" 
                height="80" 
                rx="14" 
                fill={activeDetail === 'triggers' ? '#fffbeb' : '#ffffff'} 
                stroke="#d97706" 
                strokeWidth={activeDetail === 'triggers' ? '2.5' : '2'} 
                className="shadow-xs hover:shadow-md transition"
              />
              <text x="12" y="26" className="text-[11px] font-bold fill-amber-950">5. Triggers ▾</text>
              <text x="12" y="44" className="text-[9px] font-mono fill-amber-800 font-bold">Spike·Drift·Miner</text>
              <text x="12" y="62" className="text-[8.5px] font-mono fill-amber-600 font-bold">Click to Expand</text>
            </g>

            {/* ========================================================================= */}
            {/* NODE 6: Core Evolution Loop (Clickable) */}
            {/* ========================================================================= */}
            <g transform="translate(785, 25)" className="cursor-pointer" onClick={() => toggleDetail('evolution')}>
              <rect 
                width="120" 
                height="80" 
                rx="14" 
                fill={activeDetail === 'evolution' ? '#faf5ff' : '#ffffff'} 
                stroke="#7c3aed" 
                strokeWidth={activeDetail === 'evolution' ? '2.5' : '2'} 
                className="shadow-xs hover:shadow-md transition"
              />
              <text x="12" y="26" className="text-[11px] font-bold fill-purple-950">6. Evolution ▾</text>
              <text x="12" y="44" className="text-[9px] font-mono fill-purple-800 font-bold">Multi-Agent AST</text>
              <text x="12" y="62" className="text-[8.5px] font-mono fill-purple-600 font-bold">Click to Expand</text>
            </g>
          </svg>
        </div>

        {/* Quick Tooltip Badges beneath diagram */}
        <div className="pt-3 flex flex-wrap items-center justify-center gap-2 text-xs border-t border-slate-200/80">
          <span className="text-slate-500 font-mono text-[11px]">Hover or click for technical definitions &amp; formulas:</span>
          <InfoTooltip glossaryKey="new_order"><span className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-slate-700 font-mono text-[11px] hover:border-indigo-400">1. New Order</span></InfoTooltip>
          <InfoTooltip glossaryKey="frozen_ensemble"><span className="px-2.5 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 font-mono text-[11px] hover:border-emerald-400">2. Frozen Ensemble</span></InfoTooltip>
          <InfoTooltip glossaryKey="three_way_router"><span className="px-2.5 py-1 rounded-lg bg-sky-50 border border-sky-200 text-sky-800 font-mono text-[11px] hover:border-sky-400">3. 3-Way Router</span></InfoTooltip>
          <InfoTooltip glossaryKey="outcome_logged"><span className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-slate-700 font-mono text-[11px] hover:border-slate-400">4. Outcomes</span></InfoTooltip>
          <InfoTooltip glossaryKey="triggers"><span className="px-2.5 py-1 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 font-mono text-[11px] hover:border-amber-400">5. Triggers</span></InfoTooltip>
          <InfoTooltip glossaryKey="core_evolution_loop"><span className="px-2.5 py-1 rounded-lg bg-purple-50 border border-purple-200 text-purple-800 font-mono text-[11px] hover:border-purple-400">6. Evolution Loop</span></InfoTooltip>
        </div>
      </div>

      {/* 2. DETAIL PANEL A: Core Evolution Loop (Perfect 920px Fit) */}
      {activeDetail === 'evolution' && (
        <div className="p-5 sm:p-6 rounded-2xl bg-purple-50/70 border border-purple-200 space-y-4 animate-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-purple-200 pb-3">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-lg bg-purple-600 text-white flex items-center justify-center text-xs font-mono font-bold">
                6
              </div>
              <div>
                <h3 className="text-sm font-bold text-purple-950">
                  Inside Node 6: Multi-Agent Synthesis, Gate Verification &amp; Retry Loop
                </h3>
                <p className="text-[11px] text-purple-700">
                  Candidate rules pass strict cost-weighted verification gates before promotion.
                </p>
              </div>
            </div>

            <button
              onClick={() => setActiveDetail('none')}
              className="text-xs text-purple-700 hover:text-purple-900 font-mono font-semibold"
            >
              ✕ Close Detail
            </button>
          </div>

          {/* SVG Flowchart for Core Evolution Loop */}
          <div className="overflow-x-auto">
            <div className="min-w-[880px]">
              <svg viewBox="0 0 920 260" className="w-full h-auto font-sans select-none overflow-visible">
                {/* FORWARD STEP ARROWS */}
                <path d="M 98 50 L 118 50" stroke="#7c3aed" strokeWidth="2" fill="none" markerEnd="url(#arr-purple)" />
                <path d="M 213 50 L 233 50" stroke="#7c3aed" strokeWidth="2" fill="none" markerEnd="url(#arr-purple)" />
                <path d="M 328 50 L 348 50" stroke="#7c3aed" strokeWidth="2" fill="none" markerEnd="url(#arr-purple)" />
                <path d="M 443 50 L 463 50" stroke="#7c3aed" strokeWidth="2" fill="none" markerEnd="url(#arr-purple)" />
                <path d="M 563 50 L 583 50" stroke="#059669" strokeWidth="2" fill="none" markerEnd="url(#arr-emerald)" />
                <path d="M 678 50 L 698 50" stroke="#059669" strokeWidth="2" fill="none" markerEnd="url(#arr-emerald)" />
                <path d="M 793 50 L 813 50" stroke="#059669" strokeWidth="2" fill="none" markerEnd="url(#arr-emerald)" />

                {/* ========================================================================= */}
                {/* LOOP 1: Reflector Diagnostic Feedback -> Generator */}
                {/* ========================================================================= */}
                <path 
                  d="M 280 82 C 280 160, 52 160, 52 88" 
                  stroke="#7c3aed" 
                  strokeWidth="2" 
                  strokeDasharray="4 3" 
                  fill="none" 
                  markerEnd="url(#arr-purple)" 
                />
                <rect x="70" y="148" width="220" height="24" rx="12" fill="#ffffff" stroke="#7c3aed" strokeWidth="1.5" className="shadow-xs" />
                <text x="180" y="164" textAnchor="middle" className="text-[9.5px] fill-purple-900 font-mono font-bold">
                  ↻ if rejected / diagnostic reflection feedback
                </text>

                {/* ========================================================================= */}
                {/* LOOP 2: Gate 1 Regression -> Generator */}
                {/* ========================================================================= */}
                <path 
                  d="M 513 82 C 513 220, 32 220, 32 88" 
                  stroke="#e11d48" 
                  strokeWidth="2" 
                  strokeDasharray="4 3" 
                  fill="none" 
                  markerEnd="url(#arr-purple)" 
                />
                <rect x="180" y="208" width="240" height="24" rx="12" fill="#ffffff" stroke="#e11d48" strokeWidth="1.5" className="shadow-xs" />
                <text x="300" y="224" textAnchor="middle" className="text-[9.5px] fill-rose-700 font-mono font-bold">
                  ✕ if regressed &gt; 5% / prune &amp; re-mutate
                </text>

                {/* SUB-NODES */}
                {/* 1. Generator */}
                <g transform="translate(10, 20)">
                  <rect width="88" height="62" rx="12" fill="#ffffff" stroke="#7c3aed" strokeWidth="1.5" className="shadow-xs" />
                  <text x="10" y="26" className="text-[10.5px] font-bold fill-purple-950">1. Generator</text>
                  <text x="10" y="44" className="text-[8.5px] font-mono fill-purple-700">AST Synthesis</text>
                </g>

                {/* 2. Evaluator */}
                <g transform="translate(125, 20)">
                  <rect width="88" height="62" rx="12" fill="#ffffff" stroke="#7c3aed" strokeWidth="1.5" className="shadow-xs" />
                  <text x="10" y="26" className="text-[10.5px] font-bold fill-purple-950">2. Evaluator</text>
                  <text x="10" y="44" className="text-[8.5px] font-mono fill-purple-700">Sandbox Exec</text>
                </g>

                {/* 3. Reflector */}
                <g transform="translate(240, 20)">
                  <rect width="88" height="62" rx="12" fill="#ffffff" stroke="#7c3aed" strokeWidth="1.5" className="shadow-xs" />
                  <text x="10" y="26" className="text-[10.5px] font-bold fill-purple-950">3. Reflector</text>
                  <text x="10" y="44" className="text-[8.5px] font-mono fill-purple-700">FP Diagnosis</text>
                </g>

                {/* 4. Selector */}
                <g transform="translate(355, 20)">
                  <rect width="88" height="62" rx="12" fill="#ffffff" stroke="#7c3aed" strokeWidth="1.5" className="shadow-xs" />
                  <text x="10" y="26" className="text-[10.5px] font-bold fill-purple-950">4. Selector</text>
                  <text x="10" y="44" className="text-[8.5px] font-mono fill-purple-700">Greedy Pruning</text>
                </g>

                {/* 5. Gate 1: Regression */}
                <g transform="translate(470, 20)">
                  <rect width="93" height="62" rx="12" fill="#ffffff" stroke="#059669" strokeWidth="2" className="shadow-xs" />
                  <text x="10" y="26" className="text-[10.5px] font-bold fill-emerald-950">5. Gate 1</text>
                  <text x="10" y="44" className="text-[8.5px] font-mono fill-emerald-700 font-bold">Pre-Drift</text>
                </g>

                {/* 6. Gate 2: Held-Out */}
                <g transform="translate(585, 20)">
                  <rect width="93" height="62" rx="12" fill="#ffffff" stroke="#059669" strokeWidth="2" className="shadow-xs" />
                  <text x="10" y="26" className="text-[10.5px] font-bold fill-emerald-950">6. Gate 2</text>
                  <text x="10" y="44" className="text-[8.5px] font-mono fill-emerald-700 font-bold">Single-Touch</text>
                </g>

                {/* 7. Decoy Audit */}
                <g transform="translate(700, 20)">
                  <rect width="93" height="62" rx="12" fill="#ffffff" stroke="#6366f1" strokeWidth="1.5" className="shadow-xs" />
                  <text x="10" y="26" className="text-[10.5px] font-bold fill-indigo-950">7. Decoy Guard</text>
                  <text x="10" y="44" className="text-[8.5px] font-mono fill-indigo-700">0 Leaks Audit</text>
                </g>

                {/* 8. Promoted */}
                <g transform="translate(815, 20)">
                  <rect width="95" height="62" rx="12" fill="#059669" stroke="#047857" strokeWidth="2" className="shadow-xs" />
                  <text x="12" y="26" className="text-[10.5px] font-bold fill-white">8. Promoted</text>
                  <text x="12" y="44" className="text-[8.5px] font-mono fill-emerald-100">Update Node 2</text>
                </g>
              </svg>
            </div>
          </div>
        </div>
      )}

      {/* 3. DETAIL PANEL B: Triggers & Residual Miner Pipeline (Perfect 920px Fit) */}
      {activeDetail === 'triggers' && (
        <div className="p-5 sm:p-6 rounded-2xl bg-amber-50/70 border border-amber-200 space-y-4 animate-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-amber-200 pb-3">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-lg bg-amber-600 text-white flex items-center justify-center text-xs font-mono font-bold">
                5
              </div>
              <div>
                <h3 className="text-sm font-bold text-amber-950">
                  Inside Node 5: Autonomous Trigger Sentinels &amp; Residual Mining Pipeline
                </h3>
                <p className="text-[11px] text-amber-700">
                  Showing how mature false-negative residual clustering feeds targeted agendas into the shared Core Evolution Loop.
                </p>
              </div>
            </div>

            <button
              onClick={() => setActiveDetail('none')}
              className="text-xs text-amber-700 hover:text-amber-900 font-mono font-semibold"
            >
              ✕ Close Detail
            </button>
          </div>

          {/* SVG Flowchart for Triggers & Residual Mining */}
          <div className="overflow-x-auto">
            <div className="min-w-[880px]">
              <svg viewBox="0 0 920 190" className="w-full h-auto font-sans select-none overflow-visible">
                {/* FORWARD STEP ARROWS */}
                <path d="M 140 115 L 165 115" stroke="#d97706" strokeWidth="2" fill="none" markerEnd="url(#arr-amber)" />
                <path d="M 305 115 L 330 115" stroke="#d97706" strokeWidth="2" fill="none" markerEnd="url(#arr-amber)" />
                <path d="M 470 115 L 495 115" stroke="#d97706" strokeWidth="2" fill="none" markerEnd="url(#arr-amber)" />
                <path d="M 635 115 L 660 115" stroke="#d97706" strokeWidth="2" fill="none" markerEnd="url(#arr-amber)" />
                <path d="M 800 115 L 830 115" stroke="#7c3aed" strokeWidth="2.5" fill="none" markerEnd="url(#arr-purple)" />

                {/* Top Branches cleanly curving into Target Agenda (Step 5) */}
                <path d="M 235 48 C 235 65, 732 60, 732 78" stroke="#0284c7" strokeWidth="1.5" strokeDasharray="3 3" fill="none" markerEnd="url(#arr-sky)" />
                <path d="M 405 48 C 405 65, 732 65, 732 78" stroke="#9333ea" strokeWidth="1.5" strokeDasharray="3 3" fill="none" markerEnd="url(#arr-purple)" />

                {/* Top Node 1: Spike Monitor */}
                <g transform="translate(160, 10)">
                  <rect width="150" height="38" rx="8" fill="#ffffff" stroke="#0284c7" strokeWidth="1.5" className="shadow-xs" />
                  <text x="12" y="24" className="text-[10px] font-bold fill-sky-950">Spike Monitor (Z &gt; 3.0σ)</text>
                </g>

                {/* Top Node 2: Drift Detector */}
                <g transform="translate(330, 10)">
                  <rect width="150" height="38" rx="8" fill="#ffffff" stroke="#9333ea" strokeWidth="1.5" className="shadow-xs" />
                  <text x="12" y="24" className="text-[10px] font-bold fill-purple-950">Drift Detector (PSI &gt; 0.25)</text>
                </g>

                {/* Bottom Row: Residual Miner Steps */}
                {/* Step 1: Mature Orders */}
                <g transform="translate(10, 80)">
                  <rect width="130" height="70" rx="12" fill="#ffffff" stroke="#d97706" strokeWidth="1.5" className="shadow-xs" />
                  <text x="12" y="26" className="text-[10.5px] font-bold fill-amber-950">1. Mature Orders</text>
                  <text x="12" y="46" className="text-[9px] font-mono fill-amber-800">5+ Days Post-Order</text>
                </g>

                {/* Step 2: Miss Clustering */}
                <g transform="translate(170, 80)">
                  <rect width="135" height="70" rx="12" fill="#ffffff" stroke="#d97706" strokeWidth="1.5" className="shadow-xs" />
                  <text x="12" y="26" className="text-[10.5px] font-bold fill-amber-950">2. Miss Clustering</text>
                  <text x="12" y="46" className="text-[9px] font-mono fill-amber-800">False-Negative Patterns</text>
                </g>

                {/* Step 3: Significance Guard */}
                <g transform="translate(335, 80)">
                  <rect width="135" height="70" rx="12" fill="#ffffff" stroke="#059669" strokeWidth="2" className="shadow-xs" />
                  <text x="12" y="26" className="text-[10.5px] font-bold fill-emerald-950">3. Chi-Square</text>
                  <text x="12" y="46" className="text-[9px] font-mono fill-emerald-700 font-bold">p &lt; 0.05, min 30</text>
                </g>

                {/* Step 4: Cooldown Check */}
                <g transform="translate(500, 80)">
                  <rect width="135" height="70" rx="12" fill="#ffffff" stroke="#6366f1" strokeWidth="1.5" className="shadow-xs" />
                  <text x="12" y="26" className="text-[10.5px] font-bold fill-indigo-950">4. Cooldown Check</text>
                  <text x="12" y="46" className="text-[9px] font-mono fill-indigo-700 font-bold">3-Round Guard</text>
                </g>

                {/* Step 5: Targeted Agenda */}
                <g transform="translate(665, 80)">
                  <rect width="135" height="70" rx="12" fill="#fffbeb" stroke="#d97706" strokeWidth="2" className="shadow-xs" />
                  <text x="12" y="26" className="text-[10.5px] font-bold fill-amber-950">5. Target Agenda</text>
                  <text x="12" y="46" className="text-[9px] font-mono fill-amber-800 font-bold">Synthesize Rules</text>
                </g>

                {/* Shared Node 6 Target Box */}
                <g transform="translate(835, 80)">
                  <rect width="75" height="70" rx="12" fill="#7c3aed" stroke="#6d28d9" strokeWidth="2" className="shadow-xs" />
                  <text x="10" y="30" className="text-[11px] font-bold fill-white">Node 6</text>
                  <text x="10" y="48" className="text-[9px] font-mono fill-purple-100 font-bold">Shared Loop</text>
                </g>
              </svg>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
