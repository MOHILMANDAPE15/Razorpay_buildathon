import Link from 'next/link';
import { ShieldCheck, GitBranch, Sparkles, TrendingUp, Radio, Users, ArrowRight, Layers, ShieldAlert, CheckCircle2 } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="space-y-10 animate-fade-in">
      {/* Hero Section */}
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
            Aegis-RTO closes the adversarial loop: discovering, mutating, and deploying executable Python fraud rules in response to shifting attack dynamics, without manual rule authoring or static ML decay.
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
              href="/review"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white hover:bg-slate-50 text-slate-700 font-semibold text-sm transition border border-slate-300 shadow-xs hover:text-slate-900"
            >
              <Users className="w-4 h-4 text-indigo-600" />
              Analyst Review Queue
            </Link>
          </div>
        </div>

        {/* Floating Verified Badge */}
        <div className="mt-8 pt-6 border-t border-slate-200/80 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div>
            <span className="text-slate-500 block font-medium">Test Dataset</span>
            <strong className="text-slate-900 font-mono text-sm">2,641 Orders</strong>
          </div>
          <div>
            <span className="text-slate-500 block font-medium">Net Savings</span>
            <strong className="text-emerald-600 font-mono text-sm">+₹8,072.21</strong>
          </div>
          <div>
            <span className="text-slate-500 block font-medium">Review Queue Risk</span>
            <strong className="text-amber-600 font-mono text-sm">47.17% (1.52x)</strong>
          </div>
          <div>
            <span className="text-slate-500 block font-medium">Auto-Decision Rate</span>
            <strong className="text-indigo-600 font-mono text-sm">97.99% Volume</strong>
          </div>
        </div>
      </div>

      {/* Feature Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Knowledge Graph Card */}
        <Link
          href="/lineage"
          className="bg-white p-6 rounded-2xl border border-slate-200/90 hover:border-indigo-500/50 transition group hover:shadow-card-hover flex flex-col justify-between"
        >
          <div>
            <div className="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center mb-4 text-indigo-600 group-hover:scale-105 transition">
              <GitBranch className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-900 group-hover:text-indigo-600 transition">
              Knowledge Graph Lineage
            </h3>
            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
              Browse the multi-round directed graph of autonomous hypothesis generation, error diagnoses, and parent-to-child mutation trees.
            </p>
          </div>
          <div className="pt-4 flex items-center text-xs font-semibold text-indigo-600 group-hover:text-indigo-700">
            Open Interactive DAG <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
          </div>
        </Link>

        {/* Section 6.2 Review Dashboard */}
        <Link
          href="/review"
          className="bg-white p-6 rounded-2xl border border-slate-200/90 hover:border-amber-500/50 transition group hover:shadow-card-hover flex flex-col justify-between"
        >
          <div>
            <div className="w-12 h-12 rounded-xl bg-amber-50 border border-amber-100 flex items-center justify-center mb-4 text-amber-600 group-hover:scale-105 transition">
              <Users className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-900 group-hover:text-amber-600 transition">
              Analyst Review Queue
            </h3>
            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
              3-way decision routing isolating marginal risk orders into an analyst triage queue without cherry-picking or artificial precision inflation.
            </p>
          </div>
          <div className="pt-4 flex items-center text-xs font-semibold text-amber-600 group-hover:text-amber-700">
            Inspect Review Split <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
          </div>
        </Link>

        {/* Section 4.7 Shadow Control */}
        <Link
          href="/shadow-control"
          className="bg-white p-6 rounded-2xl border border-slate-200/90 hover:border-emerald-500/50 transition group hover:shadow-card-hover flex flex-col justify-between"
        >
          <div>
            <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center mb-4 text-emerald-600 group-hover:scale-105 transition">
              <TrendingUp className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-900 group-hover:text-emerald-600 transition">
              Ablation Matrix
            </h3>
            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
              Rigorous scientific ablation proving that static rules collapse by −61.5% under real adversarial concept drift, isolating feedback-guided recovery.
            </p>
          </div>
          <div className="pt-4 flex items-center text-xs font-semibold text-emerald-600 group-hover:text-emerald-700">
            View 3-Way Matrix <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
          </div>
        </Link>

        {/* Spike Monitor Card */}
        <Link
          href="/monitor"
          className="bg-white p-6 rounded-2xl border border-slate-200/90 hover:border-sky-500/50 transition group hover:shadow-card-hover flex flex-col justify-between"
        >
          <div>
            <div className="w-12 h-12 rounded-xl bg-sky-50 border border-sky-100 flex items-center justify-center mb-4 text-sky-600 group-hover:scale-105 transition">
              <Radio className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-900 group-hover:text-sky-600 transition">
              Real-Time Spike Monitor
            </h3>
            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
              Sliding-window binomial Z-scores and CUSUM change-point detector tracking live scoring telemetry to catch coordinated fraud bursts with zero label lag.
            </p>
          </div>
          <div className="pt-4 flex items-center text-xs font-semibold text-sky-600 group-hover:text-sky-700">
            Open Telemetry Stream <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition" />
          </div>
        </Link>
      </div>
    </div>
  );
}
