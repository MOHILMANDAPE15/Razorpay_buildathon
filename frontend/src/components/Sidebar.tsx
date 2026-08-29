'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  ShieldCheck,
  GitBranch,
  Activity,
  Radio,
  Users,
  LayoutDashboard,
  Scale,
  FlaskConical,
} from 'lucide-react';
import clsx from 'clsx';

const navItems = [
  {
    href: '/',
    label: 'Overview',
    icon: LayoutDashboard,
    description: 'System dashboard & live metrics',
  },
  {
    href: '/lineage',
    label: 'Knowledge Graph',
    icon: GitBranch,
    description: 'Rule evolution lineage DAG',
  },
  {
    href: '/mining',
    label: 'Residual Mining',
    icon: Activity,
    description: 'Mature false negative mining & cooldowns',
  },
  {
    href: '/shadow-control',
    label: 'Ablation Matrix',
    icon: Scale,
    description: 'Mechanism proof & model comparison',
  },
  {
    href: '/playground',
    label: 'Playground',
    icon: FlaskConical,
    description: 'Interactive test case generator & explain agent',
  },
  {
    href: '/monitor',
    label: 'Spike Monitor',
    icon: Radio,
    description: 'Live fraud detection telemetry',
  },
  {
    href: '/review',
    label: 'Human Review',
    icon: Users,
    description: 'Analyst adjudication queue',
  },
];


export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 shrink-0 h-screen sticky top-0 flex flex-col bg-white border-r border-slate-200 shadow-xs z-40">
      {/* Brand */}
      <Link href="/" className="flex items-center gap-3 px-5 py-5 border-b border-slate-100 group">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-600 via-indigo-700 to-emerald-600 p-0.5 shadow-sm shadow-indigo-500/20 group-hover:scale-105 transition duration-200 shrink-0">
          <div className="w-full h-full bg-white rounded-[10px] flex items-center justify-center">
            <ShieldCheck className="w-4 h-4 text-indigo-600" />
          </div>
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-1.5">
            <span className="font-extrabold text-base tracking-tight text-slate-900 leading-none">
              Aegis-RTO
            </span>
            <span className="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">
              Live
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium mt-0.5 truncate">
            COD Fraud Defense
          </p>
        </div>
      </Link>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-2 pb-2">
          Navigation
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            pathname === item.href ||
            (item.href !== '/' && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150 group',
                isActive
                  ? 'bg-indigo-50 text-indigo-700 border border-indigo-200/80 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-transparent'
              )}
            >
              <div
                className={clsx(
                  'w-7 h-7 rounded-lg flex items-center justify-center shrink-0 transition-colors',
                  isActive
                    ? 'bg-indigo-100 text-indigo-600'
                    : 'bg-slate-100 text-slate-400 group-hover:bg-slate-200 group-hover:text-slate-600'
                )}
              >
                <Icon className="w-3.5 h-3.5" />
              </div>
              <span className="leading-none">{item.label}</span>
              {isActive && (
                <span className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Live Engine Status */}
      <div className="px-4 py-4 border-t border-slate-100">
        <div className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl bg-emerald-50 border border-emerald-200">
          <span className="relative flex h-2 w-2 shrink-0">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600" />
          </span>
          <div className="min-w-0">
            <p className="text-[11px] font-bold text-emerald-800 leading-none">Engine Active</p>
            <p className="text-[10px] text-emerald-600 mt-0.5 truncate font-mono">
              Autonomous · Self-Evolving
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
