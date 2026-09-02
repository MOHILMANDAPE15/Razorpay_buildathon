'use client';

import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  ShieldCheck, 
  Cpu, 
  Activity, 
  Database, 
  Zap, 
  Clock, 
  CheckCircle2, 
  RotateCcw,
  Sliders,
  X,
  ZoomIn,
  ZoomOut,
  RotateCw,
  Play,
  Pause,
} from 'lucide-react';
import clsx from 'clsx';
import { GLOSSARY, GlossaryEntry } from '@/lib/glossary';

export default function ArchitectureDiagram() {
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [zoom, setZoom] = useState<number>(1.0);
  const [flowLights, setFlowLights] = useState<boolean>(true);

  // Close modal on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSelectedKey(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleZoomIn = () => setZoom((prev) => Math.min(1.5, Number((prev + 0.1).toFixed(1))));
  const handleZoomOut = () => setZoom((prev) => Math.max(0.6, Number((prev - 0.1).toFixed(1))));
  const handleResetZoom = () => setZoom(1.0);

  const activeEntry: GlossaryEntry | undefined = selectedKey ? GLOSSARY[selectedKey] : undefined;

  const categoryColorStyles: Record<string, { bg: string; text: string; border: string; badge: string }> = {
    pipeline: { bg: 'bg-indigo-50', text: 'text-indigo-900', border: 'border-indigo-200', badge: 'bg-indigo-100 text-indigo-800' },
    agent: { bg: 'bg-purple-50', text: 'text-purple-900', border: 'border-purple-200', badge: 'bg-purple-100 text-purple-800' },
    gate: { bg: 'bg-emerald-50', text: 'text-emerald-900', border: 'border-emerald-200', badge: 'bg-emerald-100 text-emerald-800' },
    trigger: { bg: 'bg-amber-50', text: 'text-amber-900', border: 'border-amber-200', badge: 'bg-amber-100 text-amber-800' },
    routing: { bg: 'bg-sky-50', text: 'text-sky-900', border: 'border-sky-200', badge: 'bg-sky-100 text-sky-800' },
    security: { bg: 'bg-rose-50', text: 'text-rose-900', border: 'border-rose-200', badge: 'bg-rose-100 text-rose-800' },
  };

  const handleNodeClick = (key: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setSelectedKey(key);
  };

  return (
    <div className="rounded-3xl border border-slate-200 bg-white shadow-xs p-6 sm:p-8 space-y-6 animate-fade-in font-sans relative">
      <style jsx global>{`
        @keyframes pulseGlow {
          0%, 100% { opacity: 0.8; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.3); }
        }
        @keyframes flowDashForward {
          from { stroke-dashoffset: 40; }
          to { stroke-dashoffset: 0; }
        }
        @keyframes flowDashReverse {
          from { stroke-dashoffset: 0; }
          to { stroke-dashoffset: 40; }
        }
        .flow-line-forward {
          animation: flowDashForward 1.2s linear infinite;
        }
        .flow-line-reverse {
          animation: flowDashReverse 1.5s linear infinite;
        }
      `}</style>

      {/* Header with Navigation Hint & Interactive Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-100 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5" />
              Interactive Closed-Loop Architecture
            </span>
            <h2 className="text-lg font-bold text-slate-900">
              Closed-Loop Autonomous Architecture (Fully Expanded Vertical Flow)
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Scroll vertically to follow the full defense lifecycle. Pan horizontally to inspect full outer loops. <strong>Click any stage</strong> for a clear plain-language breakdown.
          </p>
        </div>

        {/* Toolbar: Zoom Controls & Flow Lights Toggle */}
        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          {/* Flow Lights Toggle */}
          <button
            onClick={() => setFlowLights(!flowLights)}
            className={clsx(
              "px-3 py-1.5 rounded-xl border text-xs font-mono font-bold flex items-center gap-1.5 transition cursor-pointer shadow-xs",
              flowLights 
                ? "bg-emerald-50 text-emerald-800 border-emerald-300 hover:bg-emerald-100"
                : "bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100"
            )}
            title="Toggle animated workflow lights"
          >
            <span className={clsx("w-2 h-2 rounded-full", flowLights ? "bg-emerald-500 animate-ping" : "bg-slate-400")} />
            {flowLights ? 'Flow Lights: Active' : 'Flow Lights: Paused'}
          </button>

          {/* Zoom In/Out/Reset Toolbar */}
          <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-xs">
            <button
              onClick={handleZoomOut}
              disabled={zoom <= 0.6}
              className="p-1.5 rounded-lg bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition shadow-xs cursor-pointer"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="px-2.5 text-xs font-mono font-bold text-slate-700 min-w-[50px] text-center">
              {Math.round(zoom * 100)}%
            </span>
            <button
              onClick={handleZoomIn}
              disabled={zoom >= 1.5}
              className="p-1.5 rounded-lg bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition shadow-xs cursor-pointer"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={handleResetZoom}
              className="p-1.5 ml-1 rounded-lg bg-white text-slate-700 hover:bg-slate-50 transition shadow-xs cursor-pointer"
              title="Reset Zoom (100%)"
            >
              <RotateCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Horizontally Scrollable SVG Canvas Container with Zoom Scale Support */}
      <div className="p-4 sm:p-6 rounded-2xl bg-slate-50 border border-slate-200 overflow-x-auto shadow-inner">
        <div 
          className="min-w-[1450px] max-w-[1500px] mx-auto relative transition-transform duration-200 origin-top"
          style={{ transform: `scale(${zoom})` }}
        >
          <svg
            viewBox="0 0 1500 2720"
            className="w-full h-auto font-sans select-none overflow-visible"
            style={{ minHeight: '2720px' }}
          >
            <defs>
              {/* Arrowhead Markers */}
              <marker id="v-arr-slate" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#64748b" />
              </marker>
              <marker id="v-arr-emerald" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#059669" />
              </marker>
              <marker id="v-arr-sky" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#0284c7" />
              </marker>
              <marker id="v-arr-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#d97706" />
              </marker>
              <marker id="v-arr-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#7c3aed" />
              </marker>
              <marker id="v-arr-rose" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#e11d48" />
              </marker>
              <marker id="v-arr-loop" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#059669" />
              </marker>

              {/* Main Promotion Return Loop Gradient */}
              <linearGradient id="v-main-loop-gradient" x1="0%" y1="100%" x2="0%" y2="0%">
                <stop offset="0%" stopColor="#059669" />
                <stop offset="35%" stopColor="#6366f1" />
                <stop offset="70%" stopColor="#7c3aed" />
                <stop offset="100%" stopColor="#059669" />
              </linearGradient>

              {/* Light Particle Glow Filter */}
              <filter id="glow-light" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="3.5" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {/* ========================================================================= */}
            {/* RECURSIVE LOOP 3 (MAIN CLOSING PROMOTION LOOP): UNIFIED, CONTINUOUS PATH */}
            {/* Starts from Promoted Champion bottom (750, 2455) -> (750, 2540) -> (1320, 2540) -> up to (1320, 217) -> enters Node 2 at (980, 217) */}
            {/* ========================================================================= */}
            <path
              id="path-promotion-loop"
              d="M 750 2455 L 750 2540 L 1320 2540 L 1320 217 L 980 217"
              stroke="url(#v-main-loop-gradient)"
              strokeWidth="4"
              strokeDasharray={flowLights ? "9 5" : "none"}
              className={clsx(flowLights && "flow-line-reverse")}
              fill="none"
              markerEnd="url(#v-arr-loop)"
            />
            {/* Origin Circle at Promoted Node exit */}
            <circle cx="750" cy="2455" r="5" fill="#059669" />

            {/* Animated Flow Light Particle traveling UP the Promotion Return Loop */}
            {flowLights && (
              <circle r="6" fill="#10b981" filter="url(#glow-light)">
                <animateMotion
                  path="M 750 2455 L 750 2540 L 1320 2540 L 1320 217 L 980 217"
                  dur="4s"
                  repeatCount="indefinite"
                  keyPoints="0;1"
                  keyTimes="0;1"
                />
              </circle>
            )}

            {/* Main Promotion Loop Condition Badge midway along track */}
            <g
              transform="translate(1320, 1050)"
              className="cursor-pointer group"
              onClick={() => handleNodeClick('loop_promotion')}
            >
              <rect
                x="-160"
                y="-25"
                width="320"
                height="50"
                rx="25"
                fill="#ffffff"
                stroke="#6366f1"
                strokeWidth="2.5"
                className="shadow-lg group-hover:stroke-indigo-600 transition"
              />
              <text x="0" y="-4" textAnchor="middle" className="text-[11.5px] fill-indigo-900 font-mono font-black">
                ↻ if promoted / updates serving ensemble
              </text>
              <text x="0" y="14" textAnchor="middle" className="text-[10px] fill-slate-500 font-mono">
                Atomic version bump &amp; serving snapshot (Click)
              </text>
            </g>


            {/* ========================================================================= */}
            {/* RECURSIVE LOOP 1: EVALUATOR FAIL -> GENERATOR RETRY (LEFT INNER TRACK) */}
            {/* ========================================================================= */}
            {/* Left track at x = 280 */}
            <path
              id="path-evaluator-retry"
              d="M 510 1560 L 280 1560 L 280 1415 L 505 1415"
              stroke="#e11d48"
              strokeWidth="2.5"
              strokeDasharray={flowLights ? "6 4" : "none"}
              className={clsx(flowLights && "flow-line-forward")}
              fill="none"
              markerEnd="url(#v-arr-rose)"
            />
            {/* Flow light particle for syntax retry */}
            {flowLights && (
              <circle r="4.5" fill="#f43f5e" filter="url(#glow-light)">
                <animateMotion
                  path="M 510 1560 L 280 1560 L 280 1415 L 505 1415"
                  dur="2.2s"
                  repeatCount="indefinite"
                />
              </circle>
            )}
            <g
              transform="translate(280, 1488)"
              className="cursor-pointer group"
              onClick={() => handleNodeClick('loop_syntax_fail')}
            >
              <rect
                x="-115"
                y="-16"
                width="230"
                height="32"
                rx="16"
                fill="#ffffff"
                stroke="#e11d48"
                strokeWidth="2"
                className="shadow-sm group-hover:scale-105 transition"
              />
              <text x="0" y="4" textAnchor="middle" className="text-[10px] fill-rose-700 font-mono font-bold">
                ✕ syntax fail → dropped; Gen re-runs ⓘ
              </text>
            </g>


            {/* ========================================================================= */}
            {/* RECURSIVE LOOP 2: REGRESSION GATE FAIL -> GENERATOR RETRY (LEFT OUTER TRACK) */}
            {/* ========================================================================= */}
            {/* Left track at x = 100 */}
            <path
              id="path-regression-retry"
              d="M 510 1995 L 100 1995 L 100 1390 L 505 1390"
              stroke="#e11d48"
              strokeWidth="3"
              strokeDasharray={flowLights ? "7 5" : "none"}
              className={clsx(flowLights && "flow-line-forward")}
              fill="none"
              markerEnd="url(#v-arr-rose)"
            />
            {/* Flow light particle for regression retry */}
            {flowLights && (
              <circle r="5" fill="#e11d48" filter="url(#glow-light)">
                <animateMotion
                  path="M 510 1995 L 100 1995 L 100 1390 L 505 1390"
                  dur="3s"
                  repeatCount="indefinite"
                />
              </circle>
            )}
            <g
              transform="translate(100, 1690)"
              className="cursor-pointer group"
              onClick={() => handleNodeClick('loop_regression_fail')}
            >
              <rect
                x="-80"
                y="-20"
                width="160"
                height="40"
                rx="12"
                fill="#ffffff"
                stroke="#e11d48"
                strokeWidth="2"
                className="shadow-sm group-hover:scale-105 transition"
              />
              <text x="0" y="-4" textAnchor="middle" className="text-[10px] fill-rose-700 font-mono font-bold">
                ✕ if regression &gt; 5%
              </text>
              <text x="0" y="12" textAnchor="middle" className="text-[9px] fill-slate-500 font-mono">
                prune; digest → next-round Gen ⓘ
              </text>
            </g>


            {/* ========================================================================= */}
            {/* SECTION 1: INCOMING ORDER TELEMETRY */}
            {/* ========================================================================= */}
            {/* 1. New Order */}
            <g transform="translate(540, 40)" className="cursor-pointer" onClick={() => handleNodeClick('new_order')}>
              <foreignObject width="420" height="85">
                <div className="w-full h-full p-4 rounded-2xl bg-white border-2 border-slate-300 shadow-xs flex items-center justify-between hover:border-indigo-500 hover:shadow-md transition">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
                      <span className="text-xs font-black text-slate-900 font-mono uppercase">1. New Order Stream</span>
                      <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-bold">CLICK DETAILS</span>
                    </div>
                    <p className="text-[11.5px] text-slate-600 font-medium leading-tight">Live Checkout Transaction Telemetry</p>
                    <span className="text-[10px] text-indigo-600 font-mono font-bold block">&lt;10ms Scoring SLA · 17 Extracted Order Signals</span>
                  </div>
                  <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-700 shrink-0">
                    <Zap className="w-5 h-5" />
                  </div>
                </div>
              </foreignObject>
            </g>

            {/* Connecting line: 1 -> 2 */}
            <path d="M 750 125 L 750 167" stroke="#64748b" strokeWidth="2.5" fill="none" markerEnd="url(#v-arr-slate)" />
            <rect x="718" y="136" width="64" height="20" rx="4" fill="#ffffff" stroke="#cbd5e1" strokeWidth="1.5" />
            <text x="750" y="150" textAnchor="middle" className="text-[9.5px] fill-slate-600 font-mono font-bold">stream</text>
            {flowLights && (
              <circle r="4" fill="#6366f1" filter="url(#glow-light)">
                <animateMotion path="M 750 125 L 750 167" dur="1s" repeatCount="indefinite" />
              </circle>
            )}


            {/* ========================================================================= */}
            {/* SECTION 2: FROZEN SERVING ENSEMBLE */}
            {/* ========================================================================= */}
            {/* 2. Frozen Ensemble (Target of closing loop) */}
            <g transform="translate(520, 170)" className="cursor-pointer" onClick={() => handleNodeClick('frozen_ensemble')}>
              <foreignObject width="460" height="95">
                <div className="w-full h-full p-4 rounded-2xl bg-emerald-50/70 border-2 border-emerald-500 shadow-xs flex items-center justify-between hover:bg-emerald-50 hover:shadow-md transition">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-black text-emerald-950 font-mono uppercase">2. Frozen Serving Ensemble</span>
                      <span className="text-[9px] font-mono px-2 py-0.5 rounded-md bg-emerald-200/80 text-emerald-900 font-bold">LOCKED PRODUCTION</span>
                    </div>
                    <p className="text-[11.5px] text-emerald-900 font-medium leading-tight">Validated Python AST Rule Weights Snapshot</p>
                    <span className="text-[10px] text-emerald-700 font-mono font-semibold block">Zero Online LLM Dependency · Sub-millisecond Execution</span>
                  </div>
                  <div className="w-11 h-11 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-xs shrink-0">
                    <ShieldCheck className="w-6 h-6" />
                  </div>
                </div>
              </foreignObject>
            </g>

            {/* Connecting line: 2 -> 3 */}
            <path d="M 750 265 L 750 307" stroke="#059669" strokeWidth="2.5" fill="none" markerEnd="url(#v-arr-emerald)" />
            <rect x="706" y="276" width="88" height="20" rx="4" fill="#ecfdf5" stroke="#a7f3d0" strokeWidth="1.5" />
            <text x="750" y="290" textAnchor="middle" className="text-[9.5px] fill-emerald-800 font-mono font-bold">score (&lt;10ms)</text>
            {flowLights && (
              <circle r="4.5" fill="#10b981" filter="url(#glow-light)">
                <animateMotion path="M 750 265 L 750 307" dur="1s" repeatCount="indefinite" />
              </circle>
            )}


            {/* ========================================================================= */}
            {/* SECTION 3: 3-WAY DECISION ROUTER */}
            {/* ========================================================================= */}
            {/* 3. 3-Way Router */}
            <g transform="translate(510, 310)" className="cursor-pointer" onClick={() => handleNodeClick('three_way_router')}>
              <foreignObject width="480" height="105">
                <div className="w-full h-full p-4 rounded-2xl bg-white border-2 border-sky-400 shadow-xs space-y-2 hover:border-sky-600 hover:shadow-md transition">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-black text-sky-950 font-mono uppercase">3. 3-Way Decision Router</span>
                      <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-sky-100 text-sky-800 font-bold">CLICK DETAILS</span>
                    </div>
                    <span className="text-[9px] font-mono font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded-md border border-sky-200">
                      Zero Cherry-Picking
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-center text-[10.5px] font-mono font-bold">
                    <div className="p-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200">
                      AUTO_APPROVE (T&lt;0.35)
                    </div>
                    <div className="p-1 rounded-lg bg-amber-50 text-amber-800 border border-amber-200">
                      MANUAL_REVIEW
                    </div>
                    <div className="p-1 rounded-lg bg-rose-50 text-rose-800 border border-rose-200">
                      AUTO_BLOCK (T≥0.70)
                    </div>
                  </div>
                </div>
              </foreignObject>
            </g>

            {/* Connecting line: 3 -> 4 */}
            <path d="M 750 415 L 750 457" stroke="#0284c7" strokeWidth="2.5" fill="none" markerEnd="url(#v-arr-sky)" />
            <rect x="710" y="426" width="80" height="20" rx="4" fill="#f0f9ff" stroke="#bae6fd" strokeWidth="1.5" />
            <text x="750" y="440" textAnchor="middle" className="text-[9.5px] fill-sky-800 font-mono font-bold">log actions</text>
            {flowLights && (
              <circle r="4.5" fill="#0284c7" filter="url(#glow-light)">
                <animateMotion path="M 750 415 L 750 457" dur="1s" repeatCount="indefinite" />
              </circle>
            )}


            {/* ========================================================================= */}
            {/* SECTION 4: OUTCOME LOGGED & 5-DAY MATURATION */}
            {/* ========================================================================= */}
            {/* 4. Outcomes */}
            <g transform="translate(530, 460)" className="cursor-pointer" onClick={() => handleNodeClick('outcome_logged')}>
              <foreignObject width="440" height="90">
                <div className="w-full h-full p-4 rounded-2xl bg-white border-2 border-slate-300 shadow-xs flex items-center justify-between hover:border-slate-500 hover:shadow-md transition">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-black text-slate-900 font-mono uppercase block">4. Outcome Logged &amp; Maturation</span>
                      <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-bold">5-DAY WINDOW</span>
                    </div>
                    <p className="text-[11.5px] text-slate-700 font-medium leading-tight">Physical Delivery vs RTO Courier Labels</p>
                    <span className="text-[10px] text-slate-500 font-mono font-semibold block">Settlement Window · Verified Ground Truth Ingestion</span>
                  </div>
                  <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-700 shrink-0">
                    <Clock className="w-5 h-5" />
                  </div>
                </div>
              </foreignObject>
            </g>

            {/* Connecting line: 4 -> Triggers Splitter */}
            <path d="M 750 550 L 750 595" stroke="#64748b" strokeWidth="2.5" fill="none" markerEnd="url(#v-arr-slate)" />
            <rect x="670" y="563" width="160" height="20" rx="4" fill="#ffffff" stroke="#cbd5e1" strokeWidth="1.5" />
            <text x="750" y="577" textAnchor="middle" className="text-[9.5px] fill-slate-600 font-mono font-bold">mature courier ground truth</text>


            {/* ========================================================================= */}
            {/* SECTION 5: CONTINUOUS MONITORING & TRIGGER SENTINELS (3 PARALLEL BOXES) */}
            {/* ========================================================================= */}
            {/* Group container bounding box */}
            <rect x="360" y="605" width="780" height="585" rx="22" fill="#fffbeb" fillOpacity="0.4" stroke="#fde68a" strokeWidth="2" strokeDasharray="5 5" />
            <text x="385" y="633" className="text-xs font-mono font-bold fill-amber-900 uppercase tracking-wide">
              5. Autonomous Adaptation Trigger Layer (Continuous Sentinels)
            </text>

            {/* Trigger Distribution Line from Step 4 */}
            <path d="M 750 595 L 750 655" stroke="#d97706" strokeWidth="2.5" fill="none" />
            <path d="M 490 655 L 1010 655" stroke="#d97706" strokeWidth="2.5" fill="none" />
            <path d="M 490 655 L 490 670" stroke="#d97706" strokeWidth="2.5" fill="none" markerEnd="url(#v-arr-amber)" />
            <path d="M 750 655 L 750 670" stroke="#d97706" strokeWidth="2.5" fill="none" markerEnd="url(#v-arr-amber)" />
            <path d="M 1010 655 L 1010 670" stroke="#d97706" strokeWidth="2.5" fill="none" markerEnd="url(#v-arr-amber)" />

            {/* 5A. Spike Monitor Sentinel */}
            <g transform="translate(380, 670)" className="cursor-pointer" onClick={() => handleNodeClick('spike_monitor')}>
              <foreignObject width="220" height="95">
                <div className="w-full h-full p-3.5 rounded-2xl bg-white border-2 border-sky-400 shadow-xs flex flex-col justify-between hover:border-sky-600 hover:shadow-md transition text-left">
                  <div>
                    <span className="text-xs font-black text-sky-950 font-mono uppercase block">Spike Monitor</span>
                    <span className="text-[10.5px] text-slate-600 font-medium">Sliding Binomial Z-Score</span>
                  </div>
                  <div className="text-[10px] font-mono font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded-md border border-sky-200">
                    Z &gt; 2.50σ Anomaly Alert
                  </div>
                </div>
              </foreignObject>
            </g>

            {/* 5B. Concept Drift Sentinel */}
            <g transform="translate(640, 670)" className="cursor-pointer" onClick={() => handleNodeClick('drift_detector')}>
              <foreignObject width="220" height="95">
                <div className="w-full h-full p-3.5 rounded-2xl bg-white border-2 border-purple-400 shadow-xs flex flex-col justify-between hover:border-purple-600 hover:shadow-md transition text-left">
                  <div>
                    <span className="text-xs font-black text-purple-950 font-mono uppercase block">Drift Detector</span>
                    <span className="text-[10.5px] text-slate-600 font-medium">Population Stability (PSI)</span>
                  </div>
                  <div className="text-[10px] font-mono font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded-md border border-purple-200">
                    PSI &gt; 0.25 Distribution Shift
                  </div>
                </div>
              </foreignObject>
            </g>

            {/* 5C. Residual Miner Sentinel (Top Level) */}
            <g transform="translate(900, 670)" className="cursor-pointer" onClick={() => handleNodeClick('residual_miner')}>
              <foreignObject width="220" height="95">
                <div className="w-full h-full p-3.5 rounded-2xl bg-amber-50 border-2 border-amber-500 shadow-xs flex flex-col justify-between hover:bg-amber-100 hover:shadow-md transition text-left">
                  <div>
                    <span className="text-xs font-black text-amber-950 font-mono uppercase block">Residual Miner</span>
                    <span className="text-[10.5px] text-amber-900 font-medium leading-tight">False-Negative Cluster Isolation</span>
                  </div>
                  <div className="text-[10px] font-mono font-bold text-amber-800 bg-white px-2 py-0.5 rounded-md border border-amber-300">
                    Chi-Square p &lt; 0.01 Guard
                  </div>
                </div>
              </foreignObject>
            </g>


            {/* ========================================================================= */}
            {/* RESIDUAL MINER INLINE SUB-STEPS (FLOWING VERTICALLY UNDER 5C) */}
            {/* ========================================================================= */}
            {/* Connecting arrow 5C -> Sub-step 1 */}
            <path d="M 1010 765 L 1010 790" stroke="#d97706" strokeWidth="2" fill="none" markerEnd="url(#v-arr-amber)" />

            {/* Sub-step 1: Mature Orders */}
            <g transform="translate(900, 795)" className="cursor-pointer" onClick={() => handleNodeClick('mature_orders')}>
              <foreignObject width="220" height="54">
                <div className="w-full h-full px-3 py-2 rounded-xl bg-white border border-amber-300 shadow-xs flex items-center justify-between text-left hover:border-amber-500 hover:bg-amber-50/50 transition">
                  <span className="text-[10.5px] font-bold text-slate-800 font-mono">1. Mature Orders (5d+)</span>
                  <span className="text-[9.5px] font-mono text-amber-700 bg-amber-50 px-2 py-0.5 rounded">Ground Truth</span>
                </div>
              </foreignObject>
            </g>

            {/* Connecting arrow Sub-step 1 -> Sub-step 2 */}
            <path d="M 1010 849 L 1010 865" stroke="#d97706" strokeWidth="1.5" fill="none" markerEnd="url(#v-arr-amber)" />

            {/* Sub-step 2: Miss Clustering */}
            <g transform="translate(900, 870)" className="cursor-pointer" onClick={() => handleNodeClick('miss_clustering')}>
              <foreignObject width="220" height="54">
                <div className="w-full h-full px-3 py-2 rounded-xl bg-white border border-amber-300 shadow-xs flex items-center justify-between text-left hover:border-amber-500 hover:bg-purple-50/50 transition">
                  <span className="text-[10.5px] font-bold text-slate-800 font-mono">2. Miss Clustering</span>
                  <span className="text-[9.5px] font-mono text-purple-700 bg-purple-50 px-2 py-0.5 rounded">HDBSCAN</span>
                </div>
              </foreignObject>
            </g>

            {/* Connecting arrow Sub-step 2 -> Sub-step 3 */}
            <path d="M 1010 924 L 1010 940" stroke="#d97706" strokeWidth="1.5" fill="none" markerEnd="url(#v-arr-amber)" />

            {/* Sub-step 3: Significance Guard */}
            <g transform="translate(900, 945)" className="cursor-pointer" onClick={() => handleNodeClick('significance_guard')}>
              <foreignObject width="220" height="54">
                <div className="w-full h-full px-3 py-2 rounded-xl bg-white border border-emerald-400 shadow-xs flex items-center justify-between text-left hover:border-emerald-600 hover:bg-emerald-50/50 transition">
                  <span className="text-[10.5px] font-bold text-emerald-950 font-mono">3. Fisher's Exact Test</span>
                  <span className="text-[9.5px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-bold">p &lt; 0.01</span>
                </div>
              </foreignObject>
            </g>

            {/* Connecting arrow Sub-step 3 -> Sub-step 4 */}
            <path d="M 1010 999 L 1010 1015" stroke="#d97706" strokeWidth="1.5" fill="none" markerEnd="url(#v-arr-amber)" />

            {/* Sub-step 4: Cooldown Check */}
            <g transform="translate(900, 1020)" className="cursor-pointer" onClick={() => handleNodeClick('cooldown_check')}>
              <foreignObject width="220" height="54">
                <div className="w-full h-full px-3 py-2 rounded-xl bg-white border border-indigo-300 shadow-xs flex items-center justify-between text-left hover:border-indigo-500 hover:bg-indigo-50/50 transition">
                  <span className="text-[10.5px] font-bold text-indigo-950 font-mono">4. Cooldown Check</span>
                  <span className="text-[9.5px] font-mono text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded font-bold">3 Rounds</span>
                </div>
              </foreignObject>
            </g>

            {/* Connecting arrow Sub-step 4 -> Sub-step 5 */}
            <path d="M 1010 1074 L 1010 1090" stroke="#d97706" strokeWidth="2" fill="none" markerEnd="url(#v-arr-amber)" />

            {/* Sub-step 5: Targeted Defense Agenda */}
            <g transform="translate(900, 1095)" className="cursor-pointer" onClick={() => handleNodeClick('defense_agenda')}>
              <foreignObject width="220" height="60">
                <div className="w-full h-full px-3.5 py-2.5 rounded-xl bg-gradient-to-r from-amber-100 to-amber-200 border-2 border-amber-600 shadow-xs flex items-center justify-between text-left hover:scale-[1.02] transition">
                  <div>
                    <span className="text-xs font-black text-amber-950 font-mono uppercase block">5. Defense Agenda</span>
                    <span className="text-[10px] text-amber-900 font-bold font-mono">Targeted Brief</span>
                  </div>
                  <Sparkles className="w-5 h-5 text-amber-700 shrink-0" />
                </div>
              </foreignObject>
            </g>


            {/* ========================================================================= */}
            {/* TRANSITION BUS: CONNECTING SENTINELS (490/750/1010) -> GENERATOR (750) */}
            {/* ========================================================================= */}
            {/* Clean, generously spaced transition band between Y = 1155 and Y = 1350 */}
            <path d="M 490 765 L 490 1245 L 750 1245" stroke="#0284c7" strokeWidth="2" strokeDasharray={flowLights ? "5 4" : "none"} className={clsx(flowLights && "flow-line-forward")} fill="none" />
            <path d="M 750 765 L 750 1245" stroke="#7c3aed" strokeWidth="2" strokeDasharray={flowLights ? "5 4" : "none"} className={clsx(flowLights && "flow-line-forward")} fill="none" />
            <path d="M 1010 1155 L 1010 1245 L 750 1245" stroke="#d97706" strokeWidth="3" fill="none" />
            
            {/* Feeder line continuing vertically down from Y = 1245 into Generator at Y = 1365 */}
            <path d="M 750 1245 L 750 1365" stroke="#7c3aed" strokeWidth="3" fill="none" markerEnd="url(#v-arr-purple)" />

            {/* Pulsing Light particle from Residual Agenda into Generator */}
            {flowLights && (
              <circle r="5" fill="#f59e0b" filter="url(#glow-light)">
                <animateMotion
                  path="M 1010 1155 L 1010 1245 L 750 1245 L 750 1365"
                  dur="2.5s"
                  repeatCount="indefinite"
                />
              </circle>
            )}

            {/* Pill Badge positioned in the open vertical space at Y = 1245 */}
            <g transform="translate(750, 1245)">
              <rect x="-130" y="-14" width="260" height="28" rx="14" fill="#fffbeb" stroke="#d97706" strokeWidth="2" className="shadow-md" />
              <text x="0" y="5" textAnchor="middle" className="text-[10.5px] fill-amber-950 font-mono font-black tracking-wide">
                feeds agenda into Generator ▾
              </text>
            </g>


            {/* ========================================================================= */}
            {/* SECTION 6: CORE MULTI-AGENT EVOLUTION LOOP & VERIFICATION GATES */}
            {/* ========================================================================= */}
            {/* Group container bounding box shifted down to Y = 1315 */}
            <rect x="450" y="1315" width="600" height="1235" rx="24" fill="#faf5ff" fillOpacity="0.5" stroke="#e9d5ff" strokeWidth="2" strokeDasharray="5 5" />
            <text x="475" y="1345" className="text-xs font-mono font-bold fill-purple-950 uppercase tracking-wide">
              6. Core Multi-Agent Evolution Loop &amp; Safety Verification Gates
            </text>

            {/* 6A. Generator Agent */}
            <g transform="translate(510, 1370)" className="cursor-pointer" onClick={() => handleNodeClick('generator')}>
              <foreignObject width="480" height="90">
                <div className="w-full h-full p-4 rounded-2xl bg-white border-2 border-purple-500 shadow-xs flex items-center justify-between hover:border-purple-700 hover:shadow-md transition">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-black text-purple-950 font-mono uppercase">1. Generator Agent</span>
                      <span className="text-[9px] font-mono px-2 py-0.5 rounded-md bg-purple-100 text-purple-800 font-bold">LLM SYNTHESIS</span>
                    </div>
                    <p className="text-[11.5px] text-slate-700 font-medium leading-tight">Synthesizes candidate Python AST boolean rules from agenda &amp; reflections</p>
                    <span className="text-[10px] text-purple-600 font-mono font-semibold block">Gemini / Claude · Guarded grammar · Zero eval()</span>
                  </div>
                  <div className="w-11 h-11 rounded-xl bg-purple-600 text-white flex items-center justify-center shrink-0">
                    <Cpu className="w-6 h-6" />
                  </div>
                </div>
              </foreignObject>
            </g>

            {/* Connecting line 6A -> 6B */}
            <path d="M 750 1460 L 750 1505" stroke="#7c3aed" strokeWidth="2.5" fill="none" markerEnd="url(#v-arr-purple)" />
            <rect x="700" y="1473" width="100" height="20" rx="4" fill="#faf5ff" stroke="#d8b4fe" strokeWidth="1.5" />
            <text x="750" y="1487" textAnchor="middle" className="text-[9.5px] fill-purple-800 font-mono font-bold">candidate AST</text>
            {flowLights && (
              <circle r="4" fill="#a855f7" filter="url(#glow-light)">
                <animateMotion path="M 750 1460 L 750 1505" dur="1s" repeatCount="indefinite" />
              </circle>
            )}

            {/* 6B. Evaluator Agent */}
            <g transform="translate(510, 1510)" className="cursor-pointer" onClick={() => handleNodeClick('evaluator')}>
              <foreignObject width="480" height="90">
                <div className="w-full h-full p-4 rounded-2xl bg-white border-2 border-purple-500 shadow-xs flex items-center justify-between hover:border-purple-700 hover:shadow-md transition">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-black text-purple-950 font-mono uppercase">2. Evaluator Agent</span>
                      <span className="text-[9px] font-mono px-2 py-0.5 rounded-md bg-purple-100 text-purple-800 font-bold">SANDBOX EXEC</span>
                    </div>
                    <p className="text-[11.5px] text-slate-700 font-medium leading-tight">Executes AST in memory sandbox; computes precision, recall, INR savings</p>
                    <span className="text-[10px] text-purple-600 font-mono font-semibold block">Net Savings = (TP × ₹250) - (FP × Margin Loss)</span>
                  </div>
                  <div className="w-11 h-11 rounded-xl bg-purple-600 text-white flex items-center justify-center shrink-0">
                    <Activity className="w-6 h-6" />
                  </div>
                </div>
              </foreignObject>
            </g>

            {/* Connecting line 6B -> 6C */}
            <path d="M 750 1600 L 750 1645" stroke="#7c3aed" strokeWidth="2.5" fill="none" markerEnd="url(#v-arr-purple)" />
            <rect x="708" y="1613" width="84" height="20" rx="4" fill="#faf5ff" stroke="#d8b4fe" strokeWidth="1.5" />
            <text x="750" y="1627" textAnchor="middle" className="text-[9.5px] fill-purple-800 font-mono font-bold">valid AST</text>
            {flowLights && (
              <circle r="4" fill="#a855f7" filter="url(#glow-light)">
                <animateMotion path="M 750 1600 L 750 1645" dur="1s" repeatCount="indefinite" />
              </circle>
            )}

            {/* 6C. Reflector Agent */}
            <g transform="translate(510, 1650)" className="cursor-pointer" onClick={() => handleNodeClick('reflector')}>
              <foreignObject width="480" height="90">
                <div className="w-full h-full p-4 rounded-2xl bg-white border-2 border-purple-500 shadow-xs flex items-center justify-between hover:border-purple-700 hover:shadow-md transition">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-black text-purple-950 font-mono uppercase">3. Reflector Agent</span>
                      <span className="text-[9px] font-mono px-2 py-0.5 rounded-md bg-purple-100 text-purple-800 font-bold">CAUSAL DIAGNOSIS</span>
                    </div>
                    <p className="text-[11.5px] text-slate-700 font-medium leading-tight">Diagnoses false positives &amp; directly synthesizes a mutated child rule via its own LLM call</p>
                    <span className="text-[10px] text-purple-600 font-mono font-semibold block">Self-Reflective Mutation · Failure digest persists to Notepad</span>
                  </div>
                  <div className="w-11 h-11 rounded-xl bg-purple-600 text-white flex items-center justify-center shrink-0">
                    <RotateCcw className="w-6 h-6" />
                  </div>
                </div>
              </foreignObject>
            </g>

            {/* Connecting line 6C -> 6D */}
            <path d="M 750 1740 L 750 1785" stroke="#7c3aed" strokeWidth="2.5" fill="none" markerEnd="url(#v-arr-purple)" />
            <rect x="660" y="1753" width="180" height="20" rx="4" fill="#faf5ff" stroke="#d8b4fe" strokeWidth="1.5" />
            <text x="750" y="1767" textAnchor="middle" className="text-[9.5px] fill-purple-800 font-mono font-bold">mutated child → Evaluator (re-scored)</text>
            {flowLights && (
              <circle r="4" fill="#a855f7" filter="url(#glow-light)">
                <animateMotion path="M 750 1740 L 750 1785" dur="1s" repeatCount="indefinite" />
              </circle>
            )}

            {/* 6D. Selector & Ensemble Pruner */}
            <g transform="translate(510, 1790)" className="cursor-pointer" onClick={() => handleNodeClick('selector')}>
              <foreignObject width="480" height="90">
                <div className="w-full h-full p-4 rounded-2xl bg-white border-2 border-purple-500 shadow-xs flex items-center justify-between hover:border-purple-700 hover:shadow-md transition">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-black text-purple-950 font-mono uppercase">4. Selector &amp; Pruner</span>
                      <span className="text-[9px] font-mono px-2 py-0.5 rounded-md bg-purple-100 text-purple-800 font-bold">PARETO FRONTIER</span>
                    </div>
                    <p className="text-[11.5px] text-slate-700 font-medium leading-tight">Greedy forward selection: prunes collinear rules and builds ensemble</p>
                    <span className="text-[10px] text-purple-600 font-mono font-semibold block">Multi-Objective Optimization · Collinearity Guard</span>
                  </div>
                  <div className="w-11 h-11 rounded-xl bg-purple-600 text-white flex items-center justify-center shrink-0">
                    <Sliders className="w-6 h-6" />
                  </div>
                </div>
              </foreignObject>
            </g>

            {/* Connecting line 6D -> 6E */}
            <path d="M 750 1880 L 750 1925" stroke="#059669" strokeWidth="2.5" fill="none" markerEnd="url(#v-arr-emerald)" />
            <rect x="676" y="1893" width="148" height="20" rx="4" fill="#ecfdf5" stroke="#a7f3d0" strokeWidth="1.5" />
            <text x="750" y="1907" textAnchor="middle" className="text-[9.5px] fill-emerald-800 font-mono font-bold">pareto ensemble candidate</text>
            {flowLights && (
              <circle r="4.5" fill="#10b981" filter="url(#glow-light)">
                <animateMotion path="M 750 1880 L 750 1925" dur="1s" repeatCount="indefinite" />
              </circle>
            )}


            {/* ========================================================================= */}
            {/* SAFETY VERIFICATION GATES (GATES 1, 2, 3) */}
            {/* ========================================================================= */}
            {/* 6E. Gate 1: Regression Gate */}
            <g transform="translate(510, 1930)" className="cursor-pointer" onClick={() => handleNodeClick('regression_gate')}>
              <foreignObject width="480" height="90">
                <div className="w-full h-full p-4 rounded-2xl bg-white border-2 border-emerald-500 shadow-xs flex items-center justify-between hover:border-emerald-700 hover:shadow-md transition">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-black text-emerald-950 font-mono uppercase">5. Gate 1: Pre-Drift Regression</span>
                      <span className="text-[9px] font-mono px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800 font-bold">SAFETY GATE</span>
                    </div>
                    <p className="text-[11.5px] text-slate-700 font-medium leading-tight">Tests against historical training data (Days 0–55). Enforces &le;5% regression</p>
                    <span className="text-[10px] text-emerald-700 font-mono font-semibold block">Zero-Tolerance Baseline Protection</span>
                  </div>
                  <div className="w-11 h-11 rounded-xl bg-emerald-600 text-white flex items-center justify-center shrink-0">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                </div>
              </foreignObject>
            </g>

            {/* Connecting line 6E -> 6F */}
            <path d="M 750 2020 L 750 2065" stroke="#059669" strokeWidth="2.5" fill="none" markerEnd="url(#v-arr-emerald)" />
            <rect x="666" y="2033" width="168" height="20" rx="4" fill="#ecfdf5" stroke="#a7f3d0" strokeWidth="1.5" />
            <text x="750" y="2047" textAnchor="middle" className="text-[9.5px] fill-emerald-800 font-mono font-bold">regression &lt; 5% [PASS]</text>
            {flowLights && (
              <circle r="4.5" fill="#10b981" filter="url(#glow-light)">
                <animateMotion path="M 750 2020 L 750 2065" dur="1s" repeatCount="indefinite" />
              </circle>
            )}

            {/* 6F. Gate 2: Held-Out Verification Gate */}
            <g transform="translate(510, 2070)" className="cursor-pointer" onClick={() => handleNodeClick('held_out_gate')}>
              <foreignObject width="480" height="90">
                <div className="w-full h-full p-4 rounded-2xl bg-white border-2 border-emerald-500 shadow-xs flex items-center justify-between hover:border-emerald-700 hover:shadow-md transition">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-black text-emerald-950 font-mono uppercase">6. Gate 2: Held-Out Validation</span>
                      <span className="text-[9px] font-mono px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800 font-bold">SAFETY GATE</span>
                    </div>
                    <p className="text-[11.5px] text-slate-700 font-medium leading-tight">Single-touch evaluation on physically isolated validation split (Days 56–75)</p>
                    <span className="text-[10px] text-emerald-700 font-mono font-semibold block">Prevents Data Snooping &amp; Cherry-Picking</span>
                  </div>
                  <div className="w-11 h-11 rounded-xl bg-emerald-600 text-white flex items-center justify-center shrink-0">
                    <Database className="w-6 h-6" />
                  </div>
                </div>
              </foreignObject>
            </g>

            {/* Connecting line 6F -> 6G */}
            <path d="M 750 2160 L 750 2205" stroke="#059669" strokeWidth="2.5" fill="none" markerEnd="url(#v-arr-emerald)" />
            <rect x="666" y="2173" width="168" height="20" rx="4" fill="#ecfdf5" stroke="#a7f3d0" strokeWidth="1.5" />
            <text x="750" y="2187" textAnchor="middle" className="text-[9.5px] fill-emerald-800 font-mono font-bold">validation split [PASS]</text>
            {flowLights && (
              <circle r="4.5" fill="#10b981" filter="url(#glow-light)">
                <animateMotion path="M 750 2160 L 750 2205" dur="1s" repeatCount="indefinite" />
              </circle>
            )}

            {/* 6G. Gate 3: Decoy Guard & AST Security Audit */}
            <g transform="translate(510, 2210)" className="cursor-pointer" onClick={() => handleNodeClick('decoy_guard')}>
              <foreignObject width="480" height="90">
                <div className="w-full h-full p-4 rounded-2xl bg-white border-2 border-indigo-500 shadow-xs flex items-center justify-between hover:border-indigo-700 hover:shadow-md transition">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-black text-indigo-950 font-mono uppercase">7. Decoy Guard &amp; AST Audit</span>
                      <span className="text-[9px] font-mono px-2 py-0.5 rounded-md bg-indigo-100 text-indigo-800 font-bold">SECURITY AUDIT</span>
                    </div>
                    <p className="text-[11.5px] text-slate-700 font-medium leading-tight">Honeypot perturbation audit + zero circularity / decoy feature leakage</p>
                    <span className="text-[10px] text-indigo-700 font-mono font-semibold block">Zero Unauthorized Imports · Sandboxed Runtime</span>
                  </div>
                  <div className="w-11 h-11 rounded-xl bg-indigo-600 text-white flex items-center justify-center shrink-0">
                    <ShieldCheck className="w-6 h-6" />
                  </div>
                </div>
              </foreignObject>
            </g>

            {/* Connecting line 6G -> 7 */}
            <path d="M 750 2300 L 750 2345" stroke="#059669" strokeWidth="3" fill="none" markerEnd="url(#v-arr-emerald)" />
            <rect x="656" y="2313" width="188" height="20" rx="4" fill="#ecfdf5" stroke="#a7f3d0" strokeWidth="1.5" />
            <text x="750" y="2327" textAnchor="middle" className="text-[9.5px] fill-emerald-800 font-mono font-bold">all gates verified [PASS]</text>
            {flowLights && (
              <circle r="5" fill="#10b981" filter="url(#glow-light)">
                <animateMotion path="M 750 2300 L 750 2345" dur="1s" repeatCount="indefinite" />
              </circle>
            )}


            {/* ========================================================================= */}
            {/* SECTION 7: PROMOTED CHAMPION ENSEMBLE */}
            {/* ========================================================================= */}
            {/* 7. Promoted Rule */}
            <g transform="translate(490, 2350)" className="cursor-pointer" onClick={() => handleNodeClick('promoted_ensemble')}>
              <foreignObject width="520" height="105">
                <div className="w-full h-full p-4 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-700 text-white shadow-xl flex items-center justify-between border-2 border-emerald-400 hover:scale-[1.01] transition">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-black font-mono uppercase tracking-wide">8. Promoted Champion Rule</span>
                      <span className="text-[9px] font-mono px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-200 font-bold border border-emerald-400">
                        PROMOTED LIVE
                      </span>
                    </div>
                    <p className="text-[12px] text-emerald-50 font-bold leading-tight">
                      Promoted to Production Registry · Serving Weights Updated
                    </p>
                    <span className="text-[10.5px] text-emerald-200 font-mono font-semibold block">
                      Shadow Deployment → Canary Testing → Live Serving Snapshot (Node 2)
                    </span>
                  </div>
                  <div className="w-12 h-12 rounded-2xl bg-white/20 border border-white/30 flex items-center justify-center text-white shrink-0">
                    <Sparkles className="w-7 h-7" />
                  </div>
                </div>
              </foreignObject>
            </g>
          </svg>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* INTERACTIVE DESCRIPTIVE DETAIL MODAL (OPENS ON CLICK) */}
      {/* ========================================================================= */}
      {selectedKey && activeEntry && (
        <div
          className="fixed inset-0 z-[99999] bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6 animate-fade-in"
          onClick={() => setSelectedKey(null)}
        >
          <div
            className="w-full max-w-2xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh] animate-scale-in"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className={clsx('p-6 border-b flex items-start justify-between gap-4', categoryColorStyles[activeEntry.category]?.bg || 'bg-slate-50')}>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className={clsx('text-[10px] font-mono font-bold uppercase px-2.5 py-0.5 rounded-full border', categoryColorStyles[activeEntry.category]?.badge)}>
                    {activeEntry.category}
                  </span>
                  <span className="text-xs font-mono text-slate-500 font-semibold">Architectural Stage Contract</span>
                </div>
                <h3 className="text-xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
                  {activeEntry.term}
                </h3>
              </div>

              <button
                onClick={() => setSelectedKey(null)}
                className="w-9 h-9 rounded-xl bg-white border border-slate-200 hover:bg-slate-100 flex items-center justify-center text-slate-500 hover:text-slate-900 transition cursor-pointer shrink-0 shadow-xs"
                title="Close (Esc)"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Scrollable Body */}
            <div className="p-6 overflow-y-auto space-y-5 text-sm">
              {/* 1. Plain-English Summary */}
              <div className="p-4 rounded-2xl bg-indigo-50/70 border border-indigo-200 text-indigo-950 space-y-1.5">
                <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-700 uppercase tracking-wider font-mono">
                  <Sparkles className="w-4 h-4 text-indigo-600 shrink-0" />
                  Plain-English Summary (Easy to Understand)
                </div>
                <p className="text-sm font-medium leading-relaxed">
                  {activeEntry.simpleExplanation}
                </p>
              </div>

              {/* 2. Full Technical Description */}
              <div className="space-y-1.5">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono">
                  Detailed Architectural Mechanics
                </h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {activeEntry.fullDesc}
                </p>
              </div>

              {/* 3. Inputs & Outputs Data Contract */}
              {activeEntry.inputsAndOutputs && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                    <span className="text-[11px] font-bold text-slate-700 uppercase font-mono block">Inputs Ingested</span>
                    <p className="text-xs text-slate-600 leading-relaxed font-mono">
                      {activeEntry.inputsAndOutputs.inputs}
                    </p>
                  </div>
                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                    <span className="text-[11px] font-bold text-emerald-800 uppercase font-mono block">Outputs Delivered</span>
                    <p className="text-xs text-slate-600 leading-relaxed font-mono">
                      {activeEntry.inputsAndOutputs.outputs}
                    </p>
                  </div>
                </div>
              )}

              {/* 4. Formula / Mathematical Metric */}
              {activeEntry.metricOrFormula && (
                <div className="p-3.5 rounded-xl bg-slate-900 text-slate-200 border border-slate-800 space-y-1 font-mono">
                  <span className="text-[10px] text-indigo-400 uppercase font-bold tracking-wider block">
                    Operating Formula / Safety Rule
                  </span>
                  <div className="text-xs text-emerald-300 font-bold">
                    {activeEntry.metricOrFormula}
                  </div>
                </div>
              )}

              {/* 5. Real-World Live Example */}
              {activeEntry.realWorldExample && (
                <div className="p-3.5 rounded-xl bg-amber-50/60 border border-amber-200 space-y-1">
                  <span className="text-[11px] font-bold text-amber-900 uppercase font-mono block">
                    Real-World Example in Aegis-RTO
                  </span>
                  <p className="text-xs text-amber-900 font-medium leading-relaxed">
                    {activeEntry.realWorldExample}
                  </p>
                </div>
              )}

              {/* 6. Why It Matters */}
              {activeEntry.whyItMatters && (
                <div className="space-y-1 border-t border-slate-100 pt-3">
                  <span className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono block">
                    Why It Matters for COD Fraud Defense
                  </span>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    {activeEntry.whyItMatters}
                  </p>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs">
              <span className="text-slate-400 font-mono text-[11px]">
                Press <kbd className="px-1.5 py-0.5 rounded bg-white border border-slate-300 text-slate-700 font-bold">ESC</kbd> or click outside to close
              </span>
              <button
                onClick={() => setSelectedKey(null)}
                className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs transition cursor-pointer shadow-xs"
              >
                Close Breakdown
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
