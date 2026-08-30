'use client';

import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle2, RefreshCw, X, AlertTriangle, CloudRain, Zap } from 'lucide-react';
import clsx from 'clsx';

export function BackendColdStartNotification() {
  const [status, setStatus] = useState<'idle' | 'probing' | 'waking' | 'connected' | 'slow'>('idle');
  const [secondsElapsed, setSecondsElapsed] = useState<number>(0);
  const [dismissed, setDismissed] = useState<boolean>(false);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    let pollInterval: NodeJS.Timeout;
    let isMounted = true;

    setStatus('probing');
    const startTime = Date.now();

    timer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      setSecondsElapsed(elapsed);
      if (elapsed >= 4 && isMounted) {
        setStatus((prev) => (prev === 'connected' ? 'connected' : elapsed > 18 ? 'slow' : 'waking'));
      }
    }, 1000);

    const checkHealth = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || '/api/v1';
        const res = await fetch(`${apiBase}/health`, { cache: 'no-store' });
        if (res.ok && isMounted) {
          setStatus('connected');
          clearInterval(timer);
          clearInterval(pollInterval);
          // Auto-hide success toast after 3.5 seconds
          setTimeout(() => {
            if (isMounted) setDismissed(true);
          }, 3500);
        }
      } catch (err) {
        // Still waking up
      }
    };

    // Initial check
    checkHealth();
    pollInterval = setInterval(checkHealth, 3000);

    return () => {
      isMounted = false;
      clearInterval(timer);
      clearInterval(pollInterval);
    };
  }, []);

  if (dismissed || status === 'idle' || (status === 'probing' && secondsElapsed < 3)) {
    return null;
  }

  return (
    <aside aria-label="Backend status notice" className="fixed bottom-5 right-5 z-50 max-w-md animate-slide-up">
      {status === 'connected' ? (
        <div className="bg-emerald-950/90 text-emerald-100 border border-emerald-500/30 backdrop-blur-md px-4 py-3 rounded-2xl shadow-xl flex items-center gap-3 text-xs">
          <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <div className="flex-1">
            <p className="font-semibold text-emerald-200">Backend Connected</p>
            <p className="text-[11px] text-emerald-300/80">Live Aegis-RTO FastAPI engine is operational.</p>
          </div>
          <button
            onClick={() => setDismissed(true)}
            className="p-1 hover:bg-emerald-800/40 rounded-lg text-emerald-300 transition"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ) : (
        <div className="bg-slate-900/95 text-slate-100 border border-indigo-500/30 backdrop-blur-md p-4 rounded-2xl shadow-2xl space-y-2 text-xs">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-400 shrink-0">
                <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
              </div>
              <div>
                <p className="font-bold text-slate-100 flex items-center gap-2">
                  <span>Fetching Live Data</span>
                  <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-indigo-900/60 text-indigo-300 border border-indigo-700/40">
                    {secondsElapsed}s
                  </span>
                </p>
                <p className="text-[11px] text-slate-400">
                  {status === 'slow'
                    ? 'Render.com container is completing cold-start wake-up.'
                    : 'Connecting to Aegis-RTO FastAPI backend...'}
                </p>
              </div>
            </div>
            <button
              onClick={() => setDismissed(true)}
              className="text-slate-400 hover:text-slate-200 p-1 rounded-lg hover:bg-slate-800 transition"
              title="Dismiss notice"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <p className="text-[11px] text-slate-300 leading-relaxed bg-slate-800/80 p-2.5 rounded-xl border border-slate-700/50">
            Render.com spins down free-tier instances when idle. First load can take <strong>30–50 seconds</strong> to awaken. Verified live metrics will populate as soon as the container responds.
          </p>
        </div>
      )}
    </aside>
  );
}
