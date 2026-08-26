'use client';

import { useState, useEffect } from 'react';
import { X, Copy, Check, Terminal, Sparkles, TrendingUp, GitMerge, ShieldCheck, AlertTriangle, ArrowRight } from 'lucide-react';
import { LineageNode, HypothesisDetails, fetchHypothesisDetails } from '@/lib/api';
import clsx from 'clsx';

interface RuleInspectorDrawerProps {
  node: LineageNode | null;
  onClose: () => void;
  onSelectNode: (nodeId: string) => void;
}

export function RuleInspectorDrawer({ node, onClose, onSelectNode }: RuleInspectorDrawerProps) {
  const [details, setDetails] = useState<HypothesisDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!node) {
      setDetails(null);
      return;
    }
    let isMounted = true;
    setLoading(true);
    fetchHypothesisDetails(node.id)
      .then((data) => {
        if (isMounted) setDetails(data);
      })
      .catch((err) => console.error('Failed to load hypothesis details:', err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [node]);

  if (!node) return null;

  const copyCode = () => {
    if (!node.rule_code) return;
    navigator.clipboard.writeText(node.rule_code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-xl bg-white border-l border-slate-200 shadow-2xl flex flex-col transition-all duration-300 animate-in slide-in-from-right">
      {/* Drawer Header */}
      <div className="px-6 py-5 border-b border-slate-200 flex items-center justify-between bg-slate-50/80">
        <div className="flex items-center gap-3">
          <div
            className={clsx(
              'w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs shadow-xs',
              node.is_champion
                ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                : node.parent_ids.length > 0
                ? 'bg-indigo-100 text-indigo-700 border border-indigo-200'
                : 'bg-slate-100 text-slate-700 border border-slate-200'
            )}
          >
            R{node.generation_round}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-slate-900 tracking-tight">{node.name}</h2>
              {node.is_champion && (
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 border border-emerald-200">
                  🏆 Champion
                </span>
              )}
            </div>
            <p className="text-xs font-mono text-slate-500">{node.id}</p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Drawer Body */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Performance Scorecard */}
        {node.metrics && (
          <div className="grid grid-cols-3 gap-3 p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div>
              <div className="text-[11px] uppercase tracking-wider text-slate-500 font-semibold flex items-center gap-1">
                <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
                Net Savings
              </div>
              <div
                className={clsx(
                  'text-lg font-bold font-mono mt-1',
                  node.metrics.net_financial_savings_inr >= 0 ? 'text-emerald-600' : 'text-rose-600'
                )}
              >
                ₹{node.metrics.net_financial_savings_inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
              </div>
            </div>
            <div>
              <div className="text-[11px] uppercase tracking-wider text-slate-500 font-semibold">Precision</div>
              <div className="text-lg font-bold font-mono text-slate-800 mt-1">
                {(node.metrics.precision * 100).toFixed(1)}%
              </div>
            </div>
            <div>
              <div className="text-[11px] uppercase tracking-wider text-slate-500 font-semibold">Recall</div>
              <div className="text-lg font-bold font-mono text-slate-800 mt-1">
                {(node.metrics.recall * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        )}

        {/* Hypothesis Rationale & Intent */}
        <div className="space-y-2">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Hypothesis Rationale & Attack Target
          </h3>
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 leading-relaxed">
            {node.description || node.rationale || 'Autonomous hypothesis synthesized targeting high-risk COD orders.'}
          </div>
        </div>

        {/* Vectorized Python Code Block */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
              <Terminal className="w-3.5 h-3.5 text-indigo-600" />
              Vectorized Rule Implementation
            </h3>
            <button
              onClick={copyCode}
              className="flex items-center gap-1 text-[11px] font-semibold text-indigo-600 hover:text-indigo-700 px-2 py-1 rounded hover:bg-indigo-50 transition"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Code'}</span>
            </button>
          </div>

          <div className="relative rounded-xl overflow-hidden bg-slate-900 border border-slate-800 text-slate-100 p-4 font-mono text-xs shadow-inner">
            <pre className="overflow-x-auto whitespace-pre-wrap">
              <code>{node.rule_code || '# Rule code representation unavailable.'}</code>
            </pre>
          </div>
        </div>

        {/* Parent & Child Lineage Connections */}
        <div className="space-y-3 pt-2 border-t border-slate-200">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
            <GitMerge className="w-3.5 h-3.5 text-indigo-600" />
            Evolutionary Lineage Connections
          </h3>

          {node.parent_ids && node.parent_ids.length > 0 ? (
            <div className="space-y-2">
              <span className="text-[11px] text-slate-500 block font-medium">Mutated From Parents:</span>
              <div className="flex flex-wrap gap-2">
                {node.parent_ids.map((pid) => (
                  <button
                    key={pid}
                    onClick={() => onSelectNode(pid)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 text-xs font-mono font-semibold transition"
                  >
                    <span>{pid}</span>
                    <ArrowRight className="w-3 h-3 text-indigo-500" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">Seed generation candidate (no parent dependencies).</p>
          )}
        </div>
      </div>
    </div>
  );
}
