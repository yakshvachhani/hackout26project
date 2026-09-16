'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Leaf, Droplet, Zap, Battery, CircleDollarSign, Wind, Sun, CloudRain, ArrowRight, Activity, TrendingUp, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useSettings, LOCATIONS } from '@/contexts/SettingsContext';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Legend } from 'recharts';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

// Flow Diagram Component with SVG lines
function EnergyFlowDiagram({ data, formatPower }: { data: any, formatPower: any }) {
  if (!data) return <div className="h-64 flex items-center justify-center text-outline">Loading flow...</div>;

  const solar = data.solar || 0;
  const wind = data.wind || 0;
  const battery = data.battery || 0;
  const diesel = data.diesel || 0;
  const load = data.load || 0;
  
  return (
    <div className="relative h-[500px] w-full rounded-xl bg-surface border border-outline-variant overflow-hidden flex flex-col items-center justify-center p-8">
      {/* SVG Connecting Lines */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
        {/* Solar to Bus */}
        <line x1="50%" y1="20%" x2="50%" y2="50%" stroke={solar > 0 ? "#10b981" : "#334155"} strokeWidth="2" strokeDasharray={solar > 0 ? "5,5" : ""} className={solar > 0 ? "animate-[dash_1s_linear_infinite]" : ""} />
        {/* Wind to Bus */}
        <line x1="30%" y1="50%" x2="50%" y2="50%" stroke={wind > 0 ? "#10b981" : "#334155"} strokeWidth="2" strokeDasharray={wind > 0 ? "5,5" : ""} className={wind > 0 ? "animate-[dash_1s_linear_infinite]" : ""} />
        {/* Battery to Bus */}
        <line x1="70%" y1="50%" x2="50%" y2="50%" stroke={battery !== 0 ? (battery > 0 ? "#10b981" : "#6366f1") : "#334155"} strokeWidth="2" strokeDasharray={battery !== 0 ? "5,5" : ""} className={battery !== 0 ? "animate-[dash_1s_linear_infinite]" : ""} />
        {/* Diesel to Bus */}
        <line x1="40%" y1="80%" x2="50%" y2="50%" stroke={diesel > 0 ? "#ef4444" : "#334155"} strokeWidth="2" strokeDasharray={diesel > 0 ? "5,5" : ""} className={diesel > 0 ? "animate-[dash_1s_linear_infinite]" : ""} />
        {/* Bus to Load */}
        <line x1="50%" y1="50%" x2="60%" y2="80%" stroke="#10b981" strokeWidth="3" strokeDasharray="5,5" className="animate-[dash_1s_linear_infinite]" />
      </svg>

      {/* Central Bus */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-surface-container px-6 py-4 rounded-xl border-2 border-emerald-500 z-10 font-bold text-emerald-400 text-center shadow-[0_0_15px_rgba(16,185,129,0.2)]">
        <div className="text-[10px] tracking-widest text-outline uppercase mb-1">Microgrid Bus</div>
        <div className="text-sm">3-Phase 415V</div>
        <div className="mt-2 bg-emerald-900/50 px-2 py-1 rounded border border-emerald-500/30 text-on-surface">
          Net: {formatPower(load)}
        </div>
      </div>

      {/* Solar */}
      <div className="absolute top-8 left-1/2 -translate-x-1/2 flex flex-col items-center z-10 w-40">
        <div className="bg-surface p-3 rounded-lg border border-outline w-full text-center shadow-lg">
          <div className="flex items-center justify-center gap-2 text-yellow-400 font-bold text-xs tracking-wider mb-2">
            <Sun size={14} /> SOLAR ARRAY
          </div>
          <div className="text-lg font-mono font-bold text-on-surface">{formatPower(solar)}</div>
          <div className="text-[10px] text-emerald-400 mt-1 flex items-center justify-center gap-1">
            <div className={`w-1.5 h-1.5 rounded-full ${solar > 0 ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`}></div>
            {solar > 0 ? 'Producing' : 'Standby'}
          </div>
        </div>
      </div>
      
      {/* Wind */}
      <div className="absolute top-1/2 left-[30%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center z-10 w-40">
        <div className="bg-surface p-3 rounded-lg border border-outline w-full text-center shadow-lg">
          <div className="flex items-center justify-center gap-2 text-blue-400 font-bold text-xs tracking-wider mb-2">
            <Wind size={14} /> WIND MAST
          </div>
          <div className="text-lg font-mono font-bold text-on-surface">{formatPower(wind)}</div>
          <div className="text-[10px] text-emerald-400 mt-1 flex items-center justify-center gap-1">
            <div className={`w-1.5 h-1.5 rounded-full ${wind > 0 ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`}></div>
            {wind > 0 ? 'Generating' : 'Calm'}
          </div>
        </div>
      </div>

      {/* Battery */}
      <div className="absolute top-1/2 left-[70%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center z-10 w-40">
        <div className="bg-surface p-3 rounded-lg border border-outline w-full text-center shadow-lg">
          <div className="flex items-center justify-center gap-2 text-indigo-400 font-bold text-xs tracking-wider mb-2">
            <Battery size={14} /> BATTERY BESS
          </div>
          <div className="text-lg font-mono font-bold text-on-surface">
            {battery > 0 ? '+' : ''}{formatPower(battery)}
          </div>
          <div className="text-[10px] text-on-surface-variant mt-1">
            SOC: 66.2% <span className={battery > 0 ? "text-emerald-400" : (battery < 0 ? "text-indigo-400" : "")}>
              ({battery > 0 ? 'Discharging' : (battery < 0 ? 'Charging' : 'Idle')})
            </span>
          </div>
        </div>
      </div>

      {/* Diesel */}
      <div className="absolute top-[80%] left-[40%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center z-10 w-40">
        <div className="bg-surface p-3 rounded-lg border border-outline w-full text-center shadow-lg">
          <div className="flex items-center justify-center gap-2 text-red-400 font-bold text-xs tracking-wider mb-2">
            <Droplet size={14} /> DIESEL GENSET
          </div>
          <div className="text-lg font-mono font-bold text-on-surface">{formatPower(diesel)}</div>
          <div className="text-[10px] text-outline mt-1 flex items-center justify-center gap-1">
            <div className={`w-1.5 h-1.5 rounded-full ${diesel > 0 ? 'bg-red-500 animate-pulse' : 'bg-slate-600'}`}></div>
            {diesel > 0 ? 'Running' : 'Standby Reserve'}
          </div>
        </div>
      </div>

      {/* Load */}
      <div className="absolute top-[80%] left-[60%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center z-10 w-48">
        <div className="bg-surface p-3 rounded-lg border border-outline w-full text-center shadow-lg border-b-2 border-b-emerald-500">
          <div className="flex items-center justify-center gap-2 text-purple-400 font-bold text-xs tracking-wider mb-2">
            <Zap size={14} /> COMMUNITY DEMAND
          </div>
          <div className="text-lg font-mono font-bold text-on-surface">{formatPower(load)}</div>
          <div className="text-[10px] text-outline mt-1">
            190 Homes • Clinic • Pumps
          </div>
        </div>
      </div>
      
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes dash {
          to {
            stroke-dashoffset: -10;
          }
        }
      `}} />
    </div>
  );
}

function KpiCard({ title, value, subValue, icon: Icon, colorClass, highlight }: any) {
  return (
    <Card className="bg-surface/80 border-outline-variant hover:bg-surface-container/80 transition-colors">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-xs font-bold text-outline tracking-wider uppercase">{title}</CardTitle>
        <Icon className={cn("h-4 w-4", colorClass)} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-on-surface">{value}</div>
        <p className={cn("text-[11px] mt-1 font-medium", highlight ? "text-emerald-400" : "text-outline")}>
          {highlight && <TrendingUp size={10} className="inline mr-1" />}
          {subValue}
        </p>
      </CardContent>
    </Card>
  );
}

export default function OverviewPage() {
  const router = useRouter();
  const { currency, powerScale, formatCurrency, formatPower, locationId } = useSettings();
  
  const currentLoc = LOCATIONS.find(l => l.id === locationId);
  const locScale = currentLoc ? currentLoc.scale : 1.0;
  const locName = currentLoc ? currentLoc.name.split(' (')[0] : 'Microgrid';

  // Real-time moving data
  const [liveData, setLiveData] = useState({
    solar: 145.2,
    wind: 84.4,
    battery: -35.6,
    diesel: 0,
    load: 194.0
  });

  const [graphData, setGraphData] = useState<any[]>([]);

  useEffect(() => {
    // Generate initial 24h graph data
    const initial = [];
    const now = new Date();
    for(let i = 24; i >= 0; i--) {
      const d = new Date(now.getTime() - i * 60 * 60 * 1000);
      const hour = d.getHours();
      
      // Simulate diurnal solar curve
      let s = 0;
      if (hour > 6 && hour < 19) {
        s = Math.sin((hour - 6) / 13 * Math.PI) * 150;
      }
      
      // Simulate demand curve (peaks in morning and evening)
      const baseLoad = 80;
      const morningPeak = hour >= 7 && hour <= 10 ? 40 : 0;
      const eveningPeak = hour >= 18 && hour <= 22 ? 60 : 0;
      const l = baseLoad + morningPeak + eveningPeak + Math.random() * 10;
      
      // Simulate wind
      const w = 20 + Math.random() * 30;
      
      initial.push({
        time: `${hour.toString().padStart(2, '0')}:00`,
        Solar: Math.max(0, s) * locScale,
        Wind: w * locScale,
        Diesel: (s + w < l ? Math.min(20, l - (s + w)) : 0) * (2 - locScale), // Very little diesel
      });
    }
    setGraphData(initial);

    // Reset base live data instantly to match the new location
    setLiveData({
      solar: 145.2 * locScale,
      wind: 84.4 * locScale,
      battery: -35.6 * locScale,
      diesel: 0,
      load: 194.0 * Math.max(0.7, locScale)
    });

    // Live ticker
    const interval = setInterval(() => {
      setLiveData(prev => {
        // slight variations
        const newWind = prev.wind + (Math.random() * 15 - 7.5);
        const newLoad = prev.load + (Math.random() * 10 - 5);
        const newBatt = newLoad - newWind - prev.solar - prev.diesel;
        
        return {
          ...prev,
          wind: Math.max(0, newWind),
          load: Math.max(50, newLoad),
          battery: newBatt
        };
      });
      
      // Also update the last point of the graph to simulate realtime
      setGraphData(current => {
        const newArr = [...current];
        const last = { ...newArr[newArr.length - 1] };
        last.Wind = liveData.wind;
        newArr[newArr.length - 1] = last;
        return newArr;
      });
      
    }, 3000);

    return () => clearInterval(interval);
  }, [locScale]);

  return (
    <div className="space-y-6 pb-12">
      
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-on-surface flex items-center gap-3">
            Executive Overview 
            <span className="text-[10px] font-bold bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/30 uppercase tracking-wider">
              {locName}
            </span>
          </h2>
          <p className="text-outline text-sm mt-1">Real-time renewable dispatch, battery storage state of charge, and avoided diesel emissions</p>
        </div>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={() => router.push('/optimizer')}
            className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs rounded-md shadow-lg shadow-emerald-500/20 transition-all flex items-center gap-2"
          >
            <Activity size={14} /> Launch Optimizer
          </button>
          <button 
            onClick={() => router.push('/demand')}
            className="px-4 py-2 bg-surface-container hover:bg-slate-700 text-on-surface border border-outline font-bold text-xs rounded-md transition-all flex items-center gap-2"
          >
            <Zap size={14} /> Fuel & Demand
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <KpiCard title="Renewable Share" value="36.1%" subValue="+4.2% vs yesterday" icon={Leaf} colorClass="text-emerald-500" highlight={true} />
        <KpiCard title="Diesel Dependency" value="0%" subValue="-8.1% vs baseline" icon={Droplet} colorClass="text-red-500" highlight={true} />
        <KpiCard title="Current Load" value={formatPower(liveData.load)} subValue={`Peak: ${formatPower(184)}`} icon={Zap} colorClass="text-yellow-500" />
        <KpiCard title="Battery SOC" value="66.2%" subValue="330.9 kWh avail" icon={Battery} colorClass="text-indigo-500" />
        <KpiCard title="Operating Cost" value={formatCurrency(88459)} subValue={`Save ${formatCurrency(29310)}`} icon={CircleDollarSign} colorClass="text-emerald-500" highlight={true} />
        <KpiCard title="CO₂ Avoided" value="3522.1 kg" subValue="-63% vs diesel-only" icon={CloudRain} colorClass="text-blue-400" highlight={true} />
      </div>

      {/* Main Flow Diagram */}
      <Card className="bg-surface/50 border-outline-variant">
        <CardHeader className="flex flex-row items-center justify-between pb-2 border-b border-outline-variant">
          <div>
            <CardTitle className="text-sm font-bold text-on-surface flex items-center gap-2">
              Live Microgrid Bus & Power Flow
              <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded border border-emerald-500/20 tracking-wider">
                SYNCED 50.02 Hz
              </span>
            </CardTitle>
            <p className="text-[11px] text-outline mt-1">Dynamic SVG power transmission animated by real-time telemetry magnitude and flow direction</p>
          </div>
          <div className="text-xs text-outline">
            <span className="font-bold text-emerald-400 mr-2">Renewable: 36.1%</span> | <span className="ml-2 font-mono">Bus: 404.5 V</span>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          <EnergyFlowDiagram data={liveData} formatPower={formatPower} />
          
          <div className="flex justify-between items-center mt-4">
            <div className="flex items-center gap-4 text-[10px] text-outline font-medium tracking-wide">
              <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-emerald-500"></div> Green: Renewable generation</span>
              <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-indigo-500"></div> Teal: BESS storage</span>
              <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-red-500"></div> Red: Diesel backup</span>
            </div>
            
            <Link href="/dispatch" className="text-xs text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1 transition-colors">
              Open Full Dispatch Telemetry <ArrowRight size={14} />
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Bottom Split */}
      <div className="grid gap-4 grid-cols-1 xl:grid-cols-3">
        
        {/* Left: Area Chart */}
        <Card className="col-span-2 bg-surface/50 border-outline-variant">
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-bold text-on-surface">Dispatch Trajectory (Today's Profile)</CardTitle>
              <Link href="/dispatch" className="text-xs text-emerald-400 hover:text-emerald-300 font-bold">Full Dispatch →</Link>
            </div>
            <p className="text-[11px] text-outline">Hourly multi-source power balance: Solar, Wind, BESS, Diesel vs Demand</p>
          </CardHeader>
          <CardContent className="pt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={graphData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorSolar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#fbbf24" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#fbbf24" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorWind" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#60a5fa" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#60a5fa" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorDiesel" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f87171" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#f87171" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => formatPower(val)} />
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', fontSize: '12px' }}
                  itemStyle={{ fontWeight: 'bold' }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '11px', fontWeight: 'bold' }} />
                <Area type="monotone" dataKey="Diesel" stroke="#f87171" fillOpacity={1} fill="url(#colorDiesel)" />
                <Area type="monotone" dataKey="Solar" stroke="#fbbf24" fillOpacity={1} fill="url(#colorSolar)" />
                <Area type="monotone" dataKey="Wind" stroke="#60a5fa" fillOpacity={1} fill="url(#colorWind)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        {/* Right: AI Energy Intelligence */}
        <Card className="col-span-1 bg-surface/50 border-outline-variant flex flex-col">
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-bold text-emerald-400 flex items-center gap-2">
                <Activity size={16} /> AI Energy Intelligence
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent className="pt-4 flex-1 flex flex-col justify-between text-sm text-on-surface-variant">
            <div className="space-y-4">
              <p className="leading-relaxed">
                Operating in high-efficiency renewable mode. Solar and wind are presently meeting <span className="text-on-surface font-bold">40.9%</span> of community load. The battery is functioning within its healthy 20-95% lifecycle envelope. Keep diesel in automated standby.
              </p>
              
              <ul className="space-y-2 mt-4">
                <li className="flex gap-2 items-start">
                  <CheckCircle2 size={14} className="text-emerald-500 mt-0.5 shrink-0" />
                  <span className="text-xs">Battery SOC safety reserve threshold maintained &gt;20%</span>
                </li>
                <li className="flex gap-2 items-start">
                  <CheckCircle2 size={14} className="text-emerald-500 mt-0.5 shrink-0" />
                  <span className="text-xs">Clinic & water pumping prioritized on primary feeder</span>
                </li>
                <li className="flex gap-2 items-start">
                  <CheckCircle2 size={14} className="text-yellow-500 mt-0.5 shrink-0" />
                  <span className="text-xs">Diesel lockouts active during predicted solar crest</span>
                </li>
              </ul>
            </div>

            <button 
              onClick={() => router.push('/optimizer')}
              className="mt-6 w-full py-2.5 bg-surface-container hover:bg-slate-700 text-emerald-400 text-xs font-bold rounded-lg border border-outline transition-colors"
            >
              Review LP Mathematical Formulation →
            </button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
