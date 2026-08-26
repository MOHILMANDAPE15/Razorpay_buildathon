'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ShieldCheck, GitBranch, Activity, Radio, Users, Sparkles } from 'lucide-react';
import clsx from 'clsx';

export function Header() {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: 'Overview', icon: Activity },
    { href: '/lineage', label: 'Knowledge Graph', icon: GitBranch, badge: '5-Round DAG' },
    { href: '/shadow-control', label: 'Shadow Control', icon: ShieldCheck, badge: 'Sec 4.7' },
    { href: '/monitor', label: 'Spike Monitor', icon: Sparkles },
    { href: '/review', label: 'Human Review', icon: Users, badge: 'Sec 6.2' },
  ];

  return (
    <header className="sticky top-0 z-40 w-full bg-white/85 backdrop-blur-md border-b border-slate-200 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 via-indigo-700 to-emerald-600 p-0.5 shadow-sm shadow-indigo-500/20 group-hover:scale-105 transition duration-200">
            <div className="w-full h-full bg-white rounded-[10px] flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-indigo-600" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight text-slate-900">
                Aegis-RTO
              </span>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                Autonomous
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block font-medium">Adaptive RTO & COD Fraud Defense</p>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="flex items-center gap-1 sm:gap-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={clsx(
                  'flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-semibold transition-all duration-150',
                  isActive
                    ? 'bg-indigo-50 text-indigo-700 border border-indigo-200/80 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                )}
              >
                <Icon className={clsx('w-4 h-4', isActive ? 'text-indigo-600' : 'text-slate-400')} />
                <span>{item.label}</span>
                {item.badge && (
                  <span className={clsx(
                    'text-[9px] uppercase px-1.5 py-0.5 rounded font-bold hidden md:inline-block',
                    isActive ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-500 border border-slate-200'
                  )}>
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Live Engine Status */}
        <div className="hidden lg:flex items-center gap-2 text-xs bg-slate-50 px-3 py-1.5 rounded-full border border-slate-200">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
          </span>
          <span className="text-slate-600 font-mono font-medium">Engine: Live Active</span>
        </div>
      </div>
    </header>
  );
}
