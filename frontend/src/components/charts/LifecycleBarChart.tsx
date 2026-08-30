'use client';

import React, { useState } from 'react';
import { TrendingUp, DollarSign, Percent, ShieldCheck } from 'lucide-react';
import clsx from 'clsx';

export interface LifecycleDataPoint {
  stage: string;
  stageSubtitle: string;
  splitInfo: string;
  totalOrders: number;
  netSavingsInr: number;
  savingsPer1kOrders: number;
  roiMultiplier: number;
  precisionPct: number;
  recallPct: number;
  colorClass: string;
  bgGradient: string;
  borderColor: string;
  highlightBadge?: string;
}

interface LifecycleBarChartProps {
  data?: LifecycleDataPoint[];
}

export function LifecycleBarChart({ data }: LifecycleBarChartProps) {
  const [metricMode, setMetricMode] = useState<'savings_per_1k' | 'roi' | 'total_savings'>('savings_per_1k');

  const defaultData: LifecycleDataPoint[] = [
    {
      stage: 'Stage 1: Genesis Baseline',
      stageSubtitle: 'Pre-Drift Foundation (Rounds 1–3)',
      splitInfo: 'Days 0–55 (10,807 orders)',
      totalOrders: 10807,
      netSavingsInr: 24312.15,
      savingsPer1kOrders: 2249.67,
      roiMultiplier: 1.64,
      precisionPct: 29.50,
      recallPct: 9.63,
      colorClass: 'text-sky-600',
      bgGradient: 'from-sky-500/15 via-sky-500/10 to-sky-500/5',
      borderColor: 'border-sky-300',
    },
    {
      stage: 'Stage 2: Drift Shock',
      stageSubtitle: 'Static Freeze Collapse (-73%)',
      splitInfo: 'Days 56–75 (3,885 orders, Unadapted)',
      totalOrders: 3885,
      netSavingsInr: 6567.62,
      savingsPer1kOrders: 1690.51,
      roiMultiplier: 1.12,
      precisionPct: 42.86,
      recallPct: 3.79,
      colorClass: 'text-amber-600',
      bgGradient: 'from-amber-500/15 via-amber-500/10 to-amber-500/5',
      borderColor: 'border-amber-300',
      highlightBadge: 'Static Failure',
    },
    {
      stage: 'Stage 3: Evolved Champion',
      stageSubtitle: 'Residual Miner Adaptation (+246%)',
      splitInfo: 'Days 56–75 (3,885 orders, Adapted)',
      totalOrders: 3885,
      netSavingsInr: 22734.77,
      savingsPer1kOrders: 5851.94,
      roiMultiplier: 2.67,
      precisionPct: 39.36,
      recallPct: 21.19,
      colorClass: 'text-emerald-600',
      bgGradient: 'from-emerald-500/20 via-emerald-500/10 to-emerald-500/5',
      borderColor: 'border-emerald-400',
      highlightBadge: '+246% Lift',
    },
    {
      stage: 'Verified Test Benchmark',
      stageSubtitle: 'Single-Touch Production T=0.70',
      splitInfo: 'Days 76–89 (2,641 orders)',
      totalOrders: 2641,
      netSavingsInr: 2458.91,
      savingsPer1kOrders: 931.05,
      roiMultiplier: 1.60,
      precisionPct: 37.25,
      recallPct: 2.39,
      colorClass: 'text-indigo-600',
      bgGradient: 'from-indigo-500/20 via-indigo-500/10 to-indigo-500/5',
      borderColor: 'border-indigo-400',
      highlightBadge: 'Locked Production',
    },
  ];

  const items = data || defaultData;

  const maxSavingsPer1k = Math.max(...items.map((i) => i.savingsPer1kOrders));
  const maxRoi = Math.max(...items.map((i) => i.roiMultiplier));
  const maxTotalSavings = Math.max(...items.map((i) => i.netSavingsInr));

  return (
    <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-6">
      {/* Header & Metric View Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-indigo-600" />
              3-Stage Evolutionary Lifecycle & Financial Impact
            </h3>
            <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
              Normalized ROI
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Tracking performance across the chronological journey from Genesis Baseline to Drift Collapse to Autonomous Evolved Recovery.
          </p>
        </div>

        {/* View Toggle */}
        <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-semibold self-start sm:self-auto shrink-0">
          <button
            onClick={() => setMetricMode('savings_per_1k')}
            className={clsx(
              'px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 font-mono',
              metricMode === 'savings_per_1k'
                ? 'bg-white text-indigo-900 shadow-xs font-bold'
                : 'text-slate-600 hover:text-slate-900'
            )}
          >
            <DollarSign className="w-3.5 h-3.5" />
            ₹ / 1k Orders
          </button>
          <button
            onClick={() => setMetricMode('roi')}
            className={clsx(
              'px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 font-mono',
              metricMode === 'roi'
                ? 'bg-white text-indigo-900 shadow-xs font-bold'
                : 'text-slate-600 hover:text-slate-900'
            )}
          >
            <Percent className="w-3.5 h-3.5" />
            ROI Multiplier
          </button>
          <button
            onClick={() => setMetricMode('total_savings')}
            className={clsx(
              'px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 font-mono',
              metricMode === 'total_savings'
                ? 'bg-white text-indigo-900 shadow-xs font-bold'
                : 'text-slate-600 hover:text-slate-900'
            )}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            Total Net ₹
          </button>
        </div>
      </div>

      {/* Grouped Visual Progress Bars */}
      <div className="space-y-4">
        {items.map((item, idx) => {
          let barPercentage = 0;
          let mainDisplayValue = '';
          let secondaryLabel = '';

          if (metricMode === 'savings_per_1k') {
            barPercentage = Math.max(8, (item.savingsPer1kOrders / maxSavingsPer1k) * 100);
            mainDisplayValue = `₹${item.savingsPer1kOrders.toLocaleString('en-IN', { maximumFractionDigits: 0 })} / 1k orders`;
            secondaryLabel = `Total Net: ₹${item.netSavingsInr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
          } else if (metricMode === 'roi') {
            barPercentage = Math.max(8, (item.roiMultiplier / maxRoi) * 100);
            mainDisplayValue = `${item.roiMultiplier.toFixed(2)}× ROI Ratio`;
            secondaryLabel = `Logistics saved per ₹1 margin cost`;
          } else {
            barPercentage = Math.max(8, (item.netSavingsInr / maxTotalSavings) * 100);
            mainDisplayValue = `₹${item.netSavingsInr.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
            secondaryLabel = `Sample: ${item.totalOrders.toLocaleString()} orders`;
          }

          return (
            <div
              key={idx}
              className={clsx(
                'p-4 rounded-xl border transition-all duration-200 hover:shadow-xs space-y-2',
                item.borderColor,
                `bg-gradient-to-r ${item.bgGradient}`
              )}
            >
              {/* Stage Title and Badges */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-900 font-mono text-[13px]">{item.stage}</span>
                  <span className="text-slate-500 text-[11px] hidden md:inline">({item.stageSubtitle})</span>
                  {item.highlightBadge && (
                    <span
                      className={clsx(
                        'px-2 py-0.5 rounded-full text-[10px] font-extrabold font-mono border',
                        item.stage.includes('Evolved') || item.stage.includes('Test')
                          ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                          : 'bg-amber-100 text-amber-800 border-amber-300'
                      )}
                    >
                      {item.highlightBadge}
                    </span>
                  )}
                </div>
                <span className="font-mono text-[11px] text-slate-500 font-semibold">{item.splitInfo}</span>
              </div>

              {/* Progress Bar with Gradient */}
              <div className="space-y-1.5">
                <div className="w-full bg-slate-200/80 rounded-full h-4 overflow-hidden p-0.5 border border-slate-300/50">
                  <div
                    className={clsx(
                      'h-full rounded-full transition-all duration-700 ease-out flex items-center justify-end pr-2',
                      idx === 2 ? 'bg-gradient-to-r from-emerald-500 to-teal-500 shadow-xs' : idx === 1 ? 'bg-gradient-to-r from-amber-400 to-orange-500' : 'bg-gradient-to-r from-indigo-500 to-sky-500'
                    )}
                    style={{ width: `${barPercentage}%` }}
                  />
                </div>

                {/* Sub-Metrics Summary Row */}
                <div className="flex flex-wrap items-center justify-between text-xs font-mono pt-0.5">
                  <div className="flex items-center gap-4">
                    <span className="font-extrabold text-slate-900 text-sm">{mainDisplayValue}</span>
                    <span className="text-slate-500 text-[11px]">{secondaryLabel}</span>
                  </div>
                  <div className="flex items-center gap-3 text-[11px] text-slate-600">
                    <span>Precision: <strong className="text-slate-900">{item.precisionPct.toFixed(2)}%</strong></span>
                    <span>Recall: <strong className="text-slate-900">{item.recallPct.toFixed(2)}%</strong></span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Explanatory Takeaway Card */}
      <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 flex items-start gap-2.5">
        <div className="w-5 h-5 rounded-md bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-[11px] shrink-0 mt-0.5">
          i
        </div>
        <p className="leading-relaxed text-[11.5px]">
          <strong>Apples-to-Apples Normalization:</strong> Because dataset sample sizes vary across phases (10.8k training vs. 3.9k validation vs. 2.6k test), normalized metrics (<strong>₹ / 1,000 orders</strong> and <strong>ROI Multiplier</strong>) provide uniform unit-economic comparison. Stage 3 (Evolved Champion) delivered a <strong>+246% lift in savings rate (₹5,851 / 1k orders)</strong> over the static baseline during drift.
        </p>
      </div>
    </div>
  );
}
