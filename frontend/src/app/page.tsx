'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  ShieldCheck, 
  GitBranch, 
  Sparkles, 
  TrendingUp, 
  Radio, 
  Users, 
  ArrowRight, 
  Layers, 
  ShieldAlert, 
  CheckCircle2, 
  AlertCircle, 
  ChevronRight, 
  Coins, 
  HelpCircle, 
  FileCode, 
  Cpu, 
  Compass, 
  Sliders, 
  Check, 
  Lock, 
  Terminal, 
  Database, 
  FileCheck 
} from 'lucide-react';
import { fetchBenchmarkSummary, BenchmarkSummaryResponse } from '@/lib/api';
import ArchitectureDiagram from '@/components/ArchitectureDiagram';

export default function HomePage() {
  const [summary, setSummary] = useState<BenchmarkSummaryResponse | null>(null);
  const [activeStoryStep, setActiveStoryStep] = useState<number>(0);
  const [lossPoolSplit, setLossPoolSplit] = useState<'test' | 'full'>('test');

  useEffect(() => {
    fetchBenchmarkSummary()
      .then((data) => setSummary(data))
      .catch((err) => console.error('Failed to load benchmark summary:', err));
  }, []);

  const headline = summary?.production_headline_metrics;

  const storySteps = [
    {
      step: 1,
      title: 'Genesis Baseline',
      period: 'Days 0–55 · Pre-Drift Training',
      badge: 'Rounds 1–3 · Initial Genesis',
      summary: 'Cold-start evolution loop on pre-drift historical training data synthesizes the frozen v1 baseline ensemble.',
      financialMetric: '₹24,312.15',
      financialLabel: 'Initial Training Net Savings',
      details: 'The Generator & Reflector agents analyzed early baseline fraud patterns (simple device reuse and low-value impulse orders) to create a verified 3-rule ensemble without seeing any future drift.',
      statusColor: 'indigo',
    },
    {
      step: 2,
      title: 'The Concept Drift Shock',
      period: 'Days 56–75 · Adversarial Shift',
      badge: 'Static Decay · Distribution Shift',
      summary: 'Fraud syndicates shifted tactics to new vectors (promo velocity stacking & throwaway account high-ticket COD).',
      financialMetric: '₹6,567.62',
      financialLabel: 'Post-Drift Validation Savings (-72.99% Drop)',
      details: 'Because the frozen v1 rules only checked pre-drift heuristics, the model missed hundreds of emerging RTOs on validation traffic, demonstrating how static rule-based systems decay in production.',
      statusColor: 'rose',
    },
    {
      step: 3,
      title: 'Targeted Adaptation & Residual Mining',
      period: 'Days 56–75 · Validation Feedback',
      badge: 'Rounds 4–5 · Drift Feedback',
      summary: 'Engine ran targeted evolution rounds informed by mature false-negative residual clusters (p < 0.05).',
      financialMetric: '₹22,734.77',
      financialLabel: 'Validation Savings Rebound',
      details: 'The re-evolved ensemble reached ₹22,734.77 in validation savings (up from ₹6,567.62 on frozen baseline). Statistical Attribution Notice: As reported in our paired bootstrap test (B=2,000 resamples) on /shadow-control, at production threshold T=0.70 this recovery cannot be statistically distinguished from additional optimization rounds alone (p = 0.1510, 95% CI crosses zero). Clear separation (+15.95% precision lift, 70.00% vs 54.05%) is observed directionally under conservative thresholding at T=0.75.',
      statusColor: 'amber',
      links: [
        { label: 'Explore Residual Clusters', href: '/residual-mining' },
        { label: 'View Paired Bootstrap CI', href: '/shadow-control' }
      ]
    },
    {
      step: 4,
      title: 'Held-Out Test Set Proof',
      period: 'Days 76–89 · Single-Touch Evaluation',
      badge: 'Gate 2 Passed · Production Frozen',
      summary: 'Evaluated strictly single-touch on the never-before-seen held-out test split (2,641 orders).',
      financialMetric: '+₹2,458.91',
      financialLabel: 'Auto Net Savings (T=0.70)',
      details: 'Operates with 97.99% automated decision rate and 37.25% precision (exceeding the 22.26% break-even hurdle), while enriching human review queue risk concentration to 47.17% (1.52x risk lift over random).',
      statusColor: 'emerald',
    },
  ];

  return (
    <div className="space-y-10 animate-fade-in pb-12">
      {/* 1. Hero Section */}
      <div className="relative rounded-3xl overflow-hidden bg-gradient-to-br from-white via-indigo-50/40 to-slate-50 p-8 sm:p-12 border border-slate-200/80 shadow-sm">
        <div className="max-w-3xl space-y-5">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-50 border border-indigo-200/80 text-indigo-700 text-xs font-bold">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            Track 2: Return-Risk Scorer & Adaptive Defense
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
            Autonomous, Self-Evolving <br />
            <span className="bg-gradient-to-r from-indigo-600 via-indigo-700 to-emerald-600 bg-clip-text text-transparent">
              RTO & COD Fraud Defense
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-600 leading-relaxed font-normal">
            Aegis-RTO closes the adversarial loop: discovering, mutating, and deploying verified Python AST fraud rules in response to shifting attack dynamics, without manual rule authoring or static ML decay.
          </p>

          <div className="flex flex-wrap items-center gap-3.5 pt-2">
            <Link
              href="/lineage"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm transition shadow-sm hover:shadow-md hover:-translate-y-0.5"
            >
              <GitBranch className="w-4 h-4" />
              Explore Knowledge Graph DAG
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/shadow-control"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white hover:bg-slate-50 text-slate-700 font-semibold text-sm transition border border-slate-300 shadow-xs hover:text-slate-900"
            >
              <TrendingUp className="w-4 h-4 text-indigo-600" />
              Scientific Ablation Matrix
            </Link>
          </div>
        </div>

        {/* Floating Production KPI Summary */}
        <div className="mt-8 pt-6 border-t border-slate-200/80 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div>
            <span className="text-slate-500 block font-medium">Test Dataset (Held-Out)</span>
            <strong className="text-slate-900 font-mono text-sm">
              {headline ? `${headline.total_test_orders.toLocaleString()} Orders` : '2,641 Orders'}
            </strong>
          </div>
          <div>
            <span className="text-slate-500 block font-medium">Auto Net Savings (T=0.70)</span>
            <strong className="text-emerald-600 font-mono text-sm">
              {headline ? `+₹${headline.auto_decided_net_savings_inr.toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : '+₹2,458.91'}
            </strong>
          </div>
          <div>
            <span className="text-slate-500 block font-medium">Review Queue Risk</span>
            <strong className="text-amber-600 font-mono text-sm">
              {headline ? `${(headline.review_queue_rto_concentration * 100).toFixed(1)}% (${headline.review_queue_risk_multiplier}x)` : '47.17% (1.52x)'}
            </strong>
          </div>
          <div>
            <span className="text-slate-500 block font-medium">Auto-Decision Rate</span>
            <strong className="text-indigo-600 font-mono text-sm">
              {headline ? `${headline.auto_decided_pct}% Volume` : '97.99% Volume'}
            </strong>
          </div>
        </div>
      </div>

      {/* 2. Interactive System Architecture Diagram Component */}
      <ArchitectureDiagram />

      {/* 3. Data Rigor & Leakage Protection Safeguards (Clean, Highlighted Points) */}
      <div className="p-6 sm:p-8 rounded-3xl border border-slate-200 bg-white shadow-xs space-y-5">
        <div className="flex items-center gap-2 border-b border-slate-100 pb-4">
          <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
            System Integrity & Rigor
          </span>
          <h2 className="text-lg font-bold text-slate-900">
            Data Protection & Leakage Safeguards
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
          {/* Safeguard 1: Physical SQL Table Isolation */}
          <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/60 space-y-2">
            <div className="flex items-center gap-2 font-bold text-slate-900">
              <Database className="w-4 h-4 text-indigo-600" />
              Physical Table Segregation
            </div>
            <p className="text-slate-600 leading-relaxed">
              `orders_train` (Days 0–55), `orders_validation` (Days 56–75), and `orders_held_out_test` (Days 76–89) reside in physically isolated SQL tables to prevent data leakage during rule evolution.
            </p>
          </div>

          {/* Safeguard 2: Sandboxed AST Execution */}
          <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/60 space-y-2">
            <div className="flex items-center gap-2 font-bold text-slate-900">
              <Terminal className="w-4 h-4 text-purple-600" />
              Sandboxed AST Execution
            </div>
            <p className="text-slate-600 leading-relaxed">
              All candidate rules execute in a restricted Python Abstract Syntax Tree (AST) evaluator without filesystem, network, `eval()`, or `exec()` access, guaranteeing zero arbitrary code execution.
            </p>
          </div>

          {/* Safeguard 3: Single-Touch Held-Out Test Set */}
          <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/60 space-y-2">
            <div className="flex items-center gap-2 font-bold text-slate-900">
              <Lock className="w-4 h-4 text-emerald-600" />
              Locked Single-Touch Test Split
            </div>
            <p className="text-slate-600 leading-relaxed">
              The 2,641 held-out test orders (Days 76–89) are evaluated exactly once at Gate 2 verification. No training iteration, feedback reflector, or hyperparameter search ever accesses test data.
            </p>
          </div>

          {/* Safeguard 4: Circularity & Decoy Column Guard */}
          <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/60 space-y-2">
            <div className="flex items-center gap-2 font-bold text-slate-900">
              <ShieldAlert className="w-4 h-4 text-amber-600" />
              Decoy Features Audit
            </div>
            <p className="text-slate-600 leading-relaxed">
              Random decoy columns (`device_model_name`, `app_theme_color`) with zero causal link are injected into training. Gate audits immediately reject any rule referencing decoys.
            </p>
          </div>

          {/* Safeguard 5: Asymmetric Margin Cost Gate */}
          <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/60 space-y-2">
            <div className="flex items-center gap-2 font-bold text-slate-900">
              <FileCheck className="w-4 h-4 text-sky-600" />
              22.26% Break-Even Hurdle
            </div>
            <p className="text-slate-600 leading-relaxed">
              Every rule must exceed the mathematical break-even precision hurdle (₹250 logistics vs 15% customer insult cost = 22.26% minimum precision) to ensure positive merchant unit economics.
            </p>
          </div>

          {/* Safeguard 6: 3-Round Residual Cooldown */}
          <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/60 space-y-2">
            <div className="flex items-center gap-2 font-bold text-slate-900">
              <CheckCircle2 className="w-4 h-4 text-teal-600" />
              3-Round Mining Cooldown
            </div>
            <p className="text-slate-600 leading-relaxed">
              Residual mining clusters enforce a mandatory 3-round cooldown per feature combination to avoid cycling or over-mutating on transient single-day false-negative spikes.
            </p>
          </div>
        </div>
      </div>

      {/* 4. Interactive Evolution Storyline (The 4-Step Narrative) */}
      <div className="p-6 sm:p-8 rounded-3xl border border-slate-200 bg-white shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-5">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                Storyline & Lifecycle
              </span>
              <h2 className="text-lg font-bold text-slate-900">
                How Aegis Evolved: Genesis to Production Proof
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Click through the 4 phases below to trace how the engine adapted to concept drift and verified its performance.
            </p>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl">
            {storySteps.map((s, idx) => (
              <button
                key={idx}
                onClick={() => setActiveStoryStep(idx)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  activeStoryStep === idx
                    ? 'bg-white text-indigo-700 shadow-xs font-mono'
                    : 'text-slate-600 hover:text-slate-900 font-mono'
                }`}
              >
                Step {s.step}
              </button>
            ))}
          </div>
        </div>

        {/* Stepper Progress Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {storySteps.map((s, idx) => {
            const isActive = activeStoryStep === idx;
            return (
              <button
                key={idx}
                onClick={() => setActiveStoryStep(idx)}
                className={`p-3.5 rounded-2xl border text-left transition-all relative overflow-hidden ${
                  isActive 
                    ? 'border-indigo-400 bg-indigo-50/50 shadow-xs ring-2 ring-indigo-500/20' 
                    : 'border-slate-200 bg-slate-50 hover:bg-slate-100/80'
                }`}
              >
                <div className="flex items-center justify-between text-[11px] font-mono mb-1">
                  <span className="font-bold text-slate-500">Step 0{s.step}</span>
                  {isActive && <CheckCircle2 className="w-3.5 h-3.5 text-indigo-600" />}
                </div>
                <div className="text-xs font-bold text-slate-900 truncate">
                  {s.title}
                </div>
                <div className="text-[10px] text-slate-500 mt-0.5 truncate">
                  {s.period}
                </div>
              </button>
            );
          })}
        </div>

        {/* Active Step Showcase Card */}
        {storySteps[activeStoryStep] && (
          <div className="p-6 rounded-2xl border border-slate-200 bg-slate-50/60 space-y-4 animate-fade-in">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 pb-3">
              <div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-800 border border-indigo-200 font-semibold mr-2">
                  {storySteps[activeStoryStep].badge}
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  {storySteps[activeStoryStep].period}
                </span>
                <h3 className="text-base font-bold text-slate-900 mt-1">
                  {storySteps[activeStoryStep].title}
                </h3>
              </div>

              <div className="text-left sm:text-right">
                <div className="text-lg font-black text-slate-900 font-mono">
                  {storySteps[activeStoryStep].financialMetric}
                </div>
                <div className="text-[11px] text-slate-500">
                  {storySteps[activeStoryStep].financialLabel}
                </div>
              </div>
            </div>

            <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
              {storySteps[activeStoryStep].details}
            </p>

            {storySteps[activeStoryStep].links && (
              <div className="flex flex-wrap items-center gap-3 pt-2">
                {storySteps[activeStoryStep].links.map((lnk, lIdx) => (
                  <Link
                    key={lIdx}
                    href={lnk.href}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-indigo-600 hover:text-indigo-800 hover:underline"
                  >
                    {lnk.label} <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* 5. Interactive Macro Loss Pool & Unit Economics Visualizer */}
      <div className="p-6 sm:p-8 rounded-3xl border border-slate-200 bg-white shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-5">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                Macro Economics
              </span>
              <h2 className="text-lg font-bold text-slate-900">
                The Preventable Loss Pool vs. Realized Savings
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Why aggressive 100% recall models go negative on net profit, and how Aegis captures verified financial value.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setLossPoolSplit('test')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
                lossPoolSplit === 'test'
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:text-slate-900'
              }`}
            >
              Held-Out Test Set (2,641 Orders)
            </button>
            <button
              onClick={() => setLossPoolSplit('full')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
                lossPoolSplit === 'full'
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:text-slate-900'
              }`}
            >
              Entire Dataset (17,333 Orders)
            </button>
          </div>
        </div>

        {/* Dynamic Metric Cards based on Selected Split */}
        {lossPoolSplit === 'test' ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="p-5 rounded-2xl border border-slate-200 bg-slate-50 space-y-2">
              <span className="text-xs text-slate-500 font-mono font-bold uppercase tracking-wider">
                1. Preventable Loss Pool
              </span>
              <div className="text-2xl font-black text-slate-900 font-mono">
                ₹2,04,750.00
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Maximum theoretical ceiling from 819 genuine RTO orders (at ₹250 logistics cost / order).
              </p>
            </div>

            <div className="p-5 rounded-2xl border border-emerald-200 bg-emerald-50/40 space-y-2">
              <span className="text-xs text-emerald-800 font-mono font-bold uppercase tracking-wider">
                2. Automated Net Profit (T=0.70)
              </span>
              <div className="text-2xl font-black text-emerald-700 font-mono">
                +₹2,458.91
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Captured across 51 auto-blocked orders (37.25% precision) after deducting all 15% margin false-positive costs.
              </p>
            </div>

            <div className="p-5 rounded-2xl border border-indigo-200 bg-indigo-50/40 space-y-2">
              <span className="text-xs text-indigo-800 font-mono font-bold uppercase tracking-wider">
                3. Total Realized (Machine + Human)
              </span>
              <div className="text-2xl font-black text-indigo-700 font-mono">
                ₹10,208.91
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Combines instant automated profit + ₹7,750 assisted recovery from 37 genuine RTOs in the human review queue (~5.0% capture).
              </p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="p-5 rounded-2xl border border-slate-200 bg-slate-50 space-y-2">
              <span className="text-xs text-slate-500 font-mono font-bold uppercase tracking-wider">
                1. Preventable Loss Pool
              </span>
              <div className="text-2xl font-black text-slate-900 font-mono">
                ₹11,28,750.00
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Maximum theoretical ceiling from 4,515 genuine RTO orders across all 90 days (at ₹250 / return). Total RTO GMV: ₹68.81 Lakhs.
              </p>
            </div>

            <div className="p-5 rounded-2xl border border-emerald-200 bg-emerald-50/40 space-y-2">
              <span className="text-xs text-emerald-800 font-mono font-bold uppercase tracking-wider">
                2. Automated Net Profit (T=0.70)
              </span>
              <div className="text-2xl font-black text-emerald-700 font-mono">
                +₹18,421.16
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Captured across 487 auto-blocks (31.42% precision) with 96.19% traffic resolved with zero human labor.
              </p>
            </div>

            <div className="p-5 rounded-2xl border border-indigo-200 bg-indigo-50/40 space-y-2">
              <span className="text-xs text-indigo-800 font-mono font-bold uppercase tracking-wider">
                3. Total Realized (Machine + Human)
              </span>
              <div className="text-2xl font-black text-indigo-700 font-mono">
                ₹65,171.16
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Combines instant automated profit + ₹46,750 assisted recovery from 220 genuine RTOs routed to human review (5.77% capture).
              </p>
            </div>
          </div>
        )}

        {/* Why 100% Recall Causes Losses Explanatory Card */}
        <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-2">
          <div className="font-bold text-slate-900 flex items-center gap-1.5 text-xs">
            <AlertCircle className="w-4 h-4 text-amber-600" />
            The 100% Recall Economic Trap in Indian E-Commerce:
          </div>
          <p className="leading-relaxed">
            In COD fraud, blocking an RTO saves ₹250, but wrongly blocking a legitimate customer destroys 15% of their gross order value in lost profit margin (averaging ₹126 to ₹296 per order). Chasing 100% recall with an unconstrained model flags hundreds of borderline customers, causing false-positive margin penalties to wipe out logistics savings (resulting in negative net savings like LightGBM&#39;s -₹3,941.66 under drift). Aegis uses a conservative two-tier design: auto-blocking only high-confidence fraud (T &ge; 0.70) to guarantee profit, and routing borderline cases (0.35 to 0.70 score) to human review.
          </p>
        </div>
      </div>

      {/* 6. Subsystem Navigation Hub (6 Core Modules) */}
      <div className="space-y-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider font-mono">
            Core Subsystem Modules
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Directly inspect and test individual components of the fraud defense engine.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {/* Card 1: Knowledge Graph */}
          <Link
            href="/lineage"
            className="bg-white p-6 rounded-2xl border border-slate-200 hover:border-indigo-500/50 transition group hover:shadow-card-hover flex flex-col justify-between shadow-xs"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center mb-3 text-indigo-600 group-hover:scale-105 transition">
                <GitBranch className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 group-hover:text-indigo-600 transition">
                Knowledge Graph Lineage
              </h4>
              <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                Interactive DAG of hypothesis rules across 5 rounds, Reflector mutation lineages, and Python AST code.
              </p>
            </div>
            <div className="pt-3 flex items-center text-xs font-semibold text-indigo-600 group-hover:text-indigo-700 border-t border-slate-100 mt-3">
              Open Interactive DAG <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
            </div>
          </Link>

          {/* Card 2: Residual Mining */}
          <Link
            href="/residual-mining"
            className="bg-white p-6 rounded-2xl border border-slate-200 hover:border-purple-500/50 transition group hover:shadow-card-hover flex flex-col justify-between shadow-xs"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-purple-50 border border-purple-100 flex items-center justify-center mb-3 text-purple-600 group-hover:scale-105 transition">
                <Compass className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 group-hover:text-purple-600 transition">
                Residual Mining & Discovery
              </h4>
              <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                Scans 5-day mature orders for missed RTOs, clusters patterns (p &lt; 0.05), and enforces cooldowns.
              </p>
            </div>
            <div className="pt-3 flex items-center text-xs font-semibold text-purple-600 group-hover:text-purple-700 border-t border-slate-100 mt-3">
              Inspect Residual Clusters <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
            </div>
          </Link>

          {/* Card 3: Ablation Matrix */}
          <Link
            href="/shadow-control"
            className="bg-white p-6 rounded-2xl border border-slate-200 hover:border-emerald-500/50 transition group hover:shadow-card-hover flex flex-col justify-between shadow-xs"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center mb-3 text-emerald-600 group-hover:scale-105 transition">
                <TrendingUp className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 group-hover:text-emerald-600 transition">
                Scientific Ablation Matrix
              </h4>
              <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                3-way neutral comparison (Models A, C, B) with 2,000 paired bootstrap CIs and Section 4.8 GBDT baseline.
              </p>
            </div>
            <div className="pt-3 flex items-center text-xs font-semibold text-emerald-600 group-hover:text-emerald-700 border-t border-slate-100 mt-3">
              View Significance Test <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
            </div>
          </Link>

          {/* Card 4: Interactive Playground */}
          <Link
            href="/playground"
            className="bg-white p-6 rounded-2xl border border-slate-200 hover:border-amber-500/50 transition group hover:shadow-card-hover flex flex-col justify-between shadow-xs"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-amber-50 border border-amber-100 flex items-center justify-center mb-3 text-amber-600 group-hover:scale-105 transition">
                <Sliders className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 group-hover:text-amber-600 transition">
                Interactive Playground
              </h4>
              <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                Simulate synthetic transactions across Easy, Medium, and Hard tiers with live rule execution rationales.
              </p>
            </div>
            <div className="pt-3 flex items-center text-xs font-semibold text-amber-600 group-hover:text-amber-700 border-t border-slate-100 mt-3">
              Launch Test Simulator <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
            </div>
          </Link>

          {/* Card 5: Real-Time Spike Monitor */}
          <Link
            href="/monitor"
            className="bg-white p-6 rounded-2xl border border-slate-200 hover:border-sky-500/50 transition group hover:shadow-card-hover flex flex-col justify-between shadow-xs"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-sky-50 border border-sky-100 flex items-center justify-center mb-3 text-sky-600 group-hover:scale-105 transition">
                <Radio className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 group-hover:text-sky-600 transition">
                Real-Time Spike Monitor
              </h4>
              <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                Sliding-window binomial Z-scores and CUSUM change-points tracking live scoring events with zero label lag.
              </p>
            </div>
            <div className="pt-3 flex items-center text-xs font-semibold text-sky-600 group-hover:text-sky-700 border-t border-slate-100 mt-3">
              Open Telemetry Stream <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
            </div>
          </Link>

          {/* Card 6: Human Review Queue */}
          <Link
            href="/review"
            className="bg-white p-6 rounded-2xl border border-slate-200 hover:border-indigo-500/50 transition group hover:shadow-card-hover flex flex-col justify-between shadow-xs"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center mb-3 text-indigo-600 group-hover:scale-105 transition">
                <Users className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 group-hover:text-indigo-600 transition">
                Analyst Review Queue
              </h4>
              <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                Triage queue for borderline risk orders (0.35–0.70 score), enriched with 47.17% RTO risk concentration.
              </p>
            </div>
            <div className="pt-3 flex items-center text-xs font-semibold text-indigo-600 group-hover:text-indigo-700 border-t border-slate-100 mt-3">
              Inspect Review Queue <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
