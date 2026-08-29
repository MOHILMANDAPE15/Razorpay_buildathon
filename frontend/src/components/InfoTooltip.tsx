'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Info, Shield } from 'lucide-react';
import { GLOSSARY, GlossaryEntry } from '@/lib/glossary';

interface InfoTooltipProps {
  glossaryKey: string;
  children?: React.ReactNode;
  showIcon?: boolean;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

export default function InfoTooltip({
  glossaryKey,
  children,
  showIcon = true,
  position = 'top',
  className = '',
}: InfoTooltipProps) {
  const [isOpen, setIsOpen] = useState(false);
  const entry: GlossaryEntry | undefined = GLOSSARY[glossaryKey];
  const triggerRef = useRef<HTMLDivElement>(null);

  if (!entry) {
    return <>{children}</>;
  }

  const categoryColors: Record<string, string> = {
    pipeline: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40',
    agent: 'bg-purple-500/20 text-purple-300 border-purple-500/40',
    gate: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
    trigger: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
    routing: 'bg-sky-500/20 text-sky-300 border-sky-500/40',
    security: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
  };

  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2.5',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2.5',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2.5',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2.5',
  };

  return (
    <div 
      ref={triggerRef}
      className={`relative inline-flex items-center group cursor-pointer ${className}`}
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
      onClick={(e) => {
        e.stopPropagation();
        setIsOpen(!isOpen);
      }}
    >
      {children}
      {showIcon && (
        <Info className="w-3.5 h-3.5 ml-1 text-slate-400 group-hover:text-indigo-600 transition-colors inline-block flex-shrink-0" />
      )}

      {isOpen && (
        <div
          className={`absolute z-[99999] w-72 p-3.5 rounded-2xl bg-slate-950/95 backdrop-blur-xl text-white text-left shadow-2xl border border-slate-700/80 pointer-events-none animate-fade-in ${positionClasses[position]}`}
          style={{ maxWidth: '85vw' }}
        >
          <div className="flex items-center justify-between gap-2 mb-1.5 pb-1.5 border-b border-slate-800">
            <span className="font-bold text-xs text-white flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5 text-indigo-400" />
              {entry.term}
            </span>
            <span className={`text-[9px] font-mono uppercase px-1.5 py-0.5 rounded-md border font-semibold ${categoryColors[entry.category] || 'bg-slate-800 text-slate-300'}`}>
              {entry.category}
            </span>
          </div>

          <p className="text-[11px] text-slate-300 leading-relaxed font-normal">
            {entry.fullDesc || entry.shortDesc}
          </p>

          {entry.metricOrFormula && (
            <div className="mt-2 pt-1.5 border-t border-slate-800 text-[10px] font-mono text-emerald-400 bg-slate-900/80 px-2 py-1 rounded-lg">
              {entry.metricOrFormula}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
