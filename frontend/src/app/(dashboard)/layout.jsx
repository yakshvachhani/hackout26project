'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, Activity, CloudSun, Sun,
  Battery, BatteryCharging, DollarSign, BarChart3,
  Settings, Bell, AlertTriangle, Menu, User, Map, FileText, ChevronRight,
  CloudRain, Users, Wind, Layers, Cpu, Zap } from
'lucide-react';
import { cn } from '@/lib/utils'; // We need a simple utils file for clsx

const NAV_ITEMS = [
{ name: 'System Overview', href: '/', icon: LayoutDashboard },
{ name: 'Live Dispatch', href: '/dispatch', icon: Activity },
{ name: 'Renewable Forecasts', href: '/forecast', icon: CloudSun },
{ name: 'AI Grid Optimizer', href: '/optimizer', icon: Cpu },
{ name: 'Energy Assets', href: '/assets', icon: Layers },
{ name: 'BESS Storage', href: '/battery', icon: BatteryCharging },
{ name: 'Community Demand', href: '/demand', icon: Users },
{ name: 'Weather Intelligence', href: '/weather', icon: Wind },
{ name: 'Economics & Carbon', href: '/cost', icon: DollarSign },
{ name: 'Historical Analytics', href: '/analytics', icon: BarChart3 },
{ name: 'System Alerts', href: '/alerts', icon: Bell },
{ name: 'Crisis Scenarios', href: '/scenarios', icon: AlertTriangle },
{ name: 'Operational Reports', href: '/reports', icon: FileText },
{ name: 'System Settings', href: '/settings', icon: Settings }];


import { SettingsProvider, useSettings } from '@/contexts/SettingsContext';

function LocationSelector() {
  const settings = useSettings();
  return (
    <select
      value={settings.locationId || 'dhordo'}
      onChange={(e) => settings.setSettings({ locationId: e.target.value })}
      className="bg-transparent font-medium text-sm text-on-background focus:outline-none appearance-none cursor-pointer">
      
      <option value="dhordo" className="bg-surface text-on-surface">Kutch Rural Microgrid (Dhordo, Gujarat)</option>
      <option value="spiti" className="bg-surface text-on-surface">Spiti Valley Microgrid (Himachal Pradesh)</option>
      <option value="sundarbans" className="bg-surface text-on-surface">Sundarbans Island Grid (West Bengal)</option>
      <option value="mawlynnong" className="bg-surface text-on-surface">Mawlynnong Eco-Grid (Meghalaya)</option>
      <option value="jaisalmer" className="bg-surface text-on-surface">Jaisalmer Desert Hub (Rajasthan)</option>
    </select>);

}

function LiveWeatherWidget() {
  const { locationId } = useSettings();
  const [weather, setWeather] = useState(null);

  React.useEffect(() => {
    let solarScale = 1.0;
    let tempOffset = 0;

    if (locationId === 'spiti') {solarScale = 0.6;tempOffset = -15;} else
    if (locationId === 'jaisalmer') {solarScale = 1.5;tempOffset = 12;} else
    if (locationId === 'sundarbans') {solarScale = 1.2;tempOffset = 4;} else
    if (locationId === 'mawlynnong') {solarScale = 0.8;tempOffset = -5;}

    fetch('http://localhost:8000/api/weather').
    then((res) => res.json()).
    then((data) => {
      if (data) {
        let rad = data.current_solar_radiation;
        let temp = data.current_temperature;

        if (rad === undefined && data.data?.current_solar_radiation !== undefined) {
          rad = data.data.current_solar_radiation;
          temp = data.data.current_temperature;
        }

        if (rad === undefined && data.date && data.solar_radiation && data.date.length > 0) {
          const now = new Date();
          const currentHour = now.getHours();
          let idx = data.date.findIndex((dStr) => new Date(dStr).getHours() === currentHour);
          if (idx === -1) idx = 0;
          rad = data.solar_radiation[idx];
          temp = data.temperature ? data.temperature[idx] : 25;
        }

        const finalRad = typeof rad === 'number' ? rad : 162.6;
        const finalTemp = typeof temp === 'number' ? temp : 28.6;

        setWeather({
          temp: finalTemp + tempOffset,
          rad: finalRad * solarScale
        });
      }
    }).
    catch((err) => {
      console.error("Weather fetch failed", err);
      setWeather({ temp: 28.6 + tempOffset, rad: 450 * solarScale });
    });
  }, [locationId]);

  if (!weather) return null;

  return (
    <div className="flex items-center gap-3 text-sm text-on-surface-variant mr-2 font-medium">
      <div className="flex items-center gap-1">
        <Sun size={14} className="text-amber-500" />
        <span>{weather.temp.toFixed(1)}°C</span>
      </div>
      <div className="flex items-center gap-1">
        <CloudRain size={14} className="text-secondary" />
        <span>{weather.rad.toFixed(0)} W/m²</span>
      </div>
    </div>);

}

function AlertsBell() {
  const { locationId, mode, simScenario } = useSettings();
  const [activeCount, setActiveCount] = useState(2);

  useEffect(() => {
    const query = new URLSearchParams({
      location_id: locationId,
      mode: mode,
      scenario: simScenario
    }).toString();

    fetch(`http://localhost:8000/api/alerts?${query}`).
    then((res) => res.json()).
    then((data) => {
      if (Array.isArray(data)) {
        const active = data.filter((a) => a.status !== 'resolved').length;
        setActiveCount(active);
      }
    }).
    catch(() => {
      let count = 2;
      if (mode === 'SIMULATION' && simScenario !== 'nominal') count += 1;
      setActiveCount(count);
    });
  }, [locationId, mode, simScenario]);

  return (
    <Link
      href="/alerts"
      className="relative text-on-surface-variant hover:text-on-surface hidden sm:block transition-colors"
      title={`${activeCount} active alerts`}>
      
      <Bell size={20} />
      {activeCount > 0 &&
      <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-error text-[9px] font-bold text-on-error shadow-sm animate-pulse">
          {activeCount}
        </span>
      }
    </Link>);

}

export default function DashboardLayout({ children }) {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [mode, setMode] = useState('LIVE');
  const pathname = usePathname();

  return (
    <SettingsProvider>
      <div className="flex h-screen w-full bg-background text-on-background overflow-hidden">
        {/* Sidebar */}
        <aside className={cn(
          "flex flex-col border-r border-outline-variant bg-surface transition-all duration-300 print:hidden",
          isSidebarOpen ? "w-64" : "w-16"
        )}>
          <div className="flex h-14 items-center justify-between px-4 border-b border-outline-variant">
            {isSidebarOpen &&
            <div className="flex items-center gap-2">
                <Zap size={18} className="text-emerald-400 fill-emerald-400/20" />
                <span className="font-bold tracking-tight text-emerald-400 text-base">ENERFLUX</span>
              </div>
            }
            <button onClick={() => setSidebarOpen(!isSidebarOpen)} className="p-1 hover:bg-surface-container rounded">
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
                      isActive ? "bg-primary-container text-on-primary-container font-semibold" : "text-on-surface-variant hover:bg-surface-container hover:text-on-surface font-medium"
                    )}
                    title={!isSidebarOpen ? item.name : undefined}>
                    
                    <Icon size={18} />
                    {isSidebarOpen && <span>{item.name}</span>}
                  </Link>);

              })}
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <div className="flex flex-col flex-1 min-w-0">
          {/* Top Header */}
          <header className="flex h-14 items-center justify-between border-b border-outline-variant bg-surface/50 px-4 lg:px-6 print:hidden">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 bg-surface-container px-3 py-1.5 rounded-md border border-outline/50">
                <Map size={14} className="text-emerald-400" />
                <LocationSelector />
              </div>
              <div className="flex items-center gap-2 bg-emerald-500/20 px-3 py-1.5 rounded-full border border-emerald-500/20">
                <span className="flex h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span>
                <span className="text-xs text-emerald-400 font-bold">OPTIMIZED</span>
                <span className="text-xs text-outline border-l border-outline pl-2 ml-1">4s ago</span>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <LiveWeatherWidget />
              <div className="flex items-center bg-surface-container rounded-lg p-1 border border-outline-variant">
                <button
                  className={cn("px-3 py-1 text-xs font-semibold rounded-md transition-all", mode === 'SIMULATION' ? "bg-surface text-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface")}
                  onClick={() => setMode('SIMULATION')}>
                  
                  Sim Mode
                </button>
                <button
                  className={cn("px-3 py-1 text-xs font-semibold rounded-md transition-all", mode === 'LIVE' ? "bg-surface text-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface")}
                  onClick={() => setMode('LIVE')}>
                  
                  Live SCADA
                </button>
              </div>
              <AlertsBell />
              <Link href="/settings" className="h-8 w-8 rounded-full bg-surface-container border border-outline-variant text-on-surface-variant flex items-center justify-center hover:bg-outline-variant hover:text-on-surface transition-colors">
                <User size={16} />
              </Link>
            </div>
          </header>

          {/* Page Content */}
          <main className="flex-1 overflow-y-auto bg-background p-6">
            {children}
          </main>
        </div>
      </div>
    </SettingsProvider>);

}