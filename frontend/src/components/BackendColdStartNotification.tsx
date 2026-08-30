'use client';

import React, { useState, useEffect } from 'react';
import { CheckCircle2, RefreshCw, X, Zap, Server, ShieldCheck, ArrowUpRight } from 'lucide-react';

export function BackendColdStartNotification() {
  const [status, setStatus] = useState<'idle' | 'probing' | 'waking' | 'connected' | 'slow'>('idle');
  const [secondsElapsed, setSecondsElapsed] = useState<number>(0);
  const [dismissed, setDismissed] = useState<boolean>(false);
  const [isRetrying, setIsRetrying] = useState<boolean>(false);

  const checkHealth = async (isMounted = true) => {
    try {
      setIsRetrying(true);
      const apiBase = process.env.NEXT_PUBLIC_API_URL || '/api/v1';
      const res = await fetch(`${apiBase}/health`, { cache: 'no-store' });
      if (res.ok && isMounted) {
        setStatus('connected');
        setTimeout(() => {
          if (isMounted) setDismissed(true);
        }, 3800);
      }
    } catch {
      // Container still warming up
    } finally {
      setIsRetrying(false);
    }
  };

  useEffect(() => {
    let timer: NodeJS.Timeout;
    let pollInterval: NodeJS.Timeout;
    let isMounted = true;

    setStatus('probing');
    const startTime = Date.now();

    timer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      setSecondsElapsed(elapsed);
      if (elapsed >= 3 && isMounted) {
        setStatus((prev) => (prev === 'connected' ? 'connected' : elapsed > 20 ? 'slow' : 'waking'));
      }
    }, 1000);

    // Initial check
    checkHealth(isMounted);
    pollInterval = setInterval(() => checkHealth(isMounted), 3000);

    return () => {
      isMounted = false;
      clearInterval(timer);
      clearInterval(pollInterval);
    };
  }, []);

  if (dismissed || status === 'idle' || (status === 'probing' && secondsElapsed < 2)) {
    return null;
  }

  // Calculate estimated progress bar percentage (assuming typical 40s cold start)
  const progressPercent = Math.min(100, Math.round((secondsElapsed / 40) * 100));

  return (
    <aside
      aria-label="Backend connection status"
      className="fixed top-5 right-5 z-[9999] max-w-sm sm:max-w-md w-full animate-in fade-in slide-in-from-top-4 duration-300 pointer-events-auto"
    >
      {status === 'connected' ? (
        /* Connected State - Radiant Emerald Theme */
        <div className="relative p-[1.5px] rounded-2xl bg-gradient-to-r from-emerald-400 via-teal-400 to-emerald-500 shadow-[0_12px_40px_-8px_rgba(16,185,129,0.45)]">
          <div className="bg-slate-950/95 backdrop-blur-xl rounded-[15px] px-4 py-3.5 flex items-center justify-between gap-3 text-slate-100">
            <div className="flex items-center gap-3">
              <div className="relative flex items-center justify-center w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-[0_0_15px_rgba(16,185,129,0.35)] shrink-0">
                <CheckCircle2 className="w-5 h-5 animate-pulse" />
                <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <p className="text-xs font-extrabold text-emerald-300 tracking-wide uppercase font-mono">
                    Backend Live
                  </p>
                  <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-700/60 font-mono">
                    200 OK
                  </span>
                </div>
                <p className="text-[11px] text-slate-300 mt-0.5">
                  Aegis-RTO Python FastAPI engine is fully operational.
                </p>
              </div>
            </div>
            <button
              onClick={() => setDismissed(true)}
              className="text-slate-400 hover:text-slate-100 p-1.5 rounded-lg hover:bg-slate-800/80 transition"
              title="Dismiss notification"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      ) : (
        /* Warming Up / Slow State - Glowing Indigo & Amber Theme */
        <div className="relative p-[1.5px] rounded-2xl bg-gradient-to-r from-amber-500 via-indigo-500 to-purple-600 shadow-[0_14px_45px_-5px_rgba(99,102,241,0.45)]">
          <div className="bg-slate-950/95 backdrop-blur-xl rounded-[15px] p-4 text-slate-100 space-y-3">
            {/* Header with Pulsing Radar and Timer */}
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-3">
                <div className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/40 shadow-[0_0_20px_rgba(99,102,241,0.4)] shrink-0">
                  <RefreshCw className={`w-4 h-4 text-indigo-300 ${isRetrying ? 'animate-spin' : 'animate-spin'}`} />
                  <span className="absolute -top-1 -right-1 flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500" />
                  </span>
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-extrabold text-slate-100 font-mono tracking-wide uppercase">
                      {status === 'slow' ? 'Container Waking Up' : 'Connecting To Backend'}
                    </span>
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/30">
                      {secondsElapsed}s
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    {status === 'slow'
                      ? 'Render.com container is spinning up free tier instance...'
                      : 'Probing live FastAPI & PostgreSQL data layer...'}
                  </p>
                </div>
              </div>

              <button
                onClick={() => setDismissed(true)}
                className="text-slate-400 hover:text-slate-100 p-1.5 rounded-lg hover:bg-slate-800/80 transition shrink-0"
                title="Dismiss notification"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Context Notice */}
            <div className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800/80 text-[11px] text-slate-300 leading-relaxed">
              <p>
                Render spins down free backend instances after inactivity. First request takes{' '}
                <strong className="text-amber-300 font-bold">~30–45s</strong> to wake up. Dashboard charts and live numbers will stream in automatically.
              </p>
            </div>

            {/* Progress Bar & Actions */}
            <div className="space-y-1.5 pt-1">
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-amber-400 via-indigo-400 to-purple-400 h-1.5 rounded-full transition-all duration-1000 ease-out"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-0.5">
                <span>Estimated wake-up: ~35s</span>
                <button
                  onClick={() => checkHealth()}
                  disabled={isRetrying}
                  className="text-indigo-300 hover:text-indigo-100 font-semibold underline hover:no-underline flex items-center gap-1 transition"
                >
                  <RefreshCw className={`w-2.5 h-2.5 ${isRetrying ? 'animate-spin' : ''}`} />
                  <span>Check Status</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}

