'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, Activity, CloudRain, Sun, 
  Battery, Droplet, DollarSign, BarChart3, 
  Settings, Bell, AlertTriangle, Menu, User, Map, FileText, ChevronRight
} from 'lucide-react';
import { cn } from '@/lib/utils'; // We need a simple utils file for clsx

const NAV_ITEMS = [
  { name: 'Overview', href: '/', icon: LayoutDashboard },
  { name: 'Live Dispatch', href: '/dispatch', icon: Activity },
  { name: 'Forecasts', href: '/forecast', icon: CloudRain },
  { name: 'Optimizer', href: '/optimizer', icon: Sun },
  { name: 'Energy Assets', href: '/assets', icon: Battery },
  { name: 'Battery', href: '/battery', icon: Battery },
  { name: 'Demand', href: '/demand', icon: Droplet },
  { name: 'Weather', href: '/weather', icon: CloudRain },
  { name: 'Cost & Emissions', href: '/cost', icon: DollarSign },
  { name: 'Historical Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Alerts', href: '/alerts', icon: Bell },
  { name: 'Scenarios', href: '/scenarios', icon: AlertTriangle },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'Settings', href: '/settings', icon: Settings },
];

import { SettingsProvider } from '@/contexts/SettingsContext';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [mode, setMode] = useState('LIVE');
  const pathname = usePathname();
  const [weather, setWeather] = useState<{temp: number, rad: number} | null>(null);

  React.useEffect(() => {
    fetch('http://localhost:8000/api/weather')
      .then(res => res.json())
      .then(data => {
        if(data && data.date && data.date.length > 0) {
           setWeather({ temp: data.temperature[0], rad: data.solar_radiation[0] });
        }
      })
      .catch(err => console.error("Weather fetch failed", err));
  }, []);

  return (
    <SettingsProvider>
      <div className="flex h-screen w-full bg-slate-950 text-slate-100 overflow-hidden">
        {/* Sidebar */}
        <aside className={cn(
          "flex flex-col border-r border-slate-800 bg-slate-900 transition-all duration-300",
          isSidebarOpen ? "w-64" : "w-16"
        )}>
          <div className="flex h-14 items-center justify-between px-4 border-b border-slate-800">
            {isSidebarOpen && <span className="font-bold tracking-tight text-emerald-400">GRIDWISE</span>}
            <button onClick={() => setSidebarOpen(!isSidebarOpen)} className="p-1 hover:bg-slate-800 rounded">
              <Menu size={20} />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto py-4 scrollbar-thin">
            <nav className="space-y-1 px-2">
              {NAV_ITEMS.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                      isActive ? "bg-emerald-900/40 text-emerald-400" : "text-slate-400 hover:bg-slate-800 hover:text-slate-100"
                    )}
                    title={!isSidebarOpen ? item.name : undefined}
                  >
                    <Icon size={18} />
                    {isSidebarOpen && <span>{item.name}</span>}
                  </Link>
                );
              })}
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <div className="flex flex-col flex-1 min-w-0">
          {/* Top Header */}
          <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-900/50 px-4 lg:px-6">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 bg-slate-800/50 px-3 py-1.5 rounded-md border border-slate-700/50">
                <Map size={14} className="text-emerald-400" />
                <span className="font-medium text-sm text-slate-100">Kutch Rural Microgrid (Dhordo, Gujarat)</span>
              </div>
              <div className="flex items-center gap-2 bg-emerald-500/20 px-3 py-1.5 rounded-full border border-emerald-500/20">
                <span className="flex h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span>
                <span className="text-xs text-emerald-400 font-bold">OPTIMIZED</span>
                <span className="text-xs text-slate-500 border-l border-slate-700 pl-2 ml-1">4s ago</span>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {weather && (
                <div className="flex items-center gap-3 text-sm text-slate-300 mr-2">
                  <div className="flex items-center gap-1">
                    <Sun size={14} className="text-amber-500" />
                    <span>{weather.temp.toFixed(1)}°C</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <CloudRain size={14} className="text-blue-400" />
                    <span>{weather.rad.toFixed(0)} W/m²</span>
                  </div>
                </div>
              )}
              <div className="flex items-center bg-slate-800 rounded-lg p-1">
                <button 
                  className={cn("px-3 py-1 text-xs font-medium rounded-md", mode === 'SIMULATION' ? "bg-emerald-600 text-white" : "text-slate-400")}
                  onClick={() => setMode('SIMULATION')}
                >
                  Sim Mode
                </button>
                <button 
                  className={cn("px-3 py-1 text-xs font-medium rounded-md", mode === 'LIVE' ? "bg-slate-700 text-white" : "text-slate-400")}
                  onClick={() => setMode('LIVE')}
                >
                  Live SCADA
                </button>
              </div>
              <Link href="/alerts" className="relative text-slate-400 hover:text-slate-100 hidden sm:block">
                <Bell size={20} />
                <span className="absolute -top-1 -right-1 flex h-3 w-3 items-center justify-center rounded-full bg-red-500 text-[8px] font-bold text-white">2</span>
              </Link>
              <Link href="/settings" className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center hover:bg-slate-600 transition-colors">
                <User size={16} />
              </Link>
            </div>
          </header>

          {/* Page Content */}
          <main className="flex-1 overflow-y-auto bg-slate-950 p-6">
            {children}
          </main>
        </div>
      </div>
    </SettingsProvider>
  );
}
