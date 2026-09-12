'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Leaf, Droplet, Zap, Battery, CircleDollarSign, Wind, Sun, CloudRain, ArrowRight, Activity, TrendingUp, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useSettings } from '@/contexts/SettingsContext';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Legend } from 'recharts';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

// Flow Diagram Component with SVG lines
function EnergyFlowDiagram({ data, formatPower }: { data: any, formatPower: any }) {
  if (!data) return <div className="h-64 flex items-center justify-center text-slate-500">Loading flow...</div>;

  const solar = data.solar || 0;
  const wind = data.wind || 0;
  const battery = data.battery || 0;
  const diesel = data.diesel || 0;
  const load = data.load || 0;
  
  return (
    <div className="relative h-[500px] w-full rounded-xl bg-slate-900 border border-slate-800 overflow-hidden flex flex-col items-center justify-center p-8">
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
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-slate-800 px-6 py-4 rounded-xl border-2 border-emerald-500 z-10 font-bold text-emerald-400 text-center shadow-[0_0_15px_rgba(16,185,129,0.2)]">
        <div className="text-[10px] tracking-widest text-slate-400 uppercase mb-1">Microgrid Bus</div>
        <div className="text-sm">3-Phase 415V</div>
        <div className="mt-2 bg-emerald-900/50 px-2 py-1 rounded border border-emerald-500/30 text-white">
          Net: {formatPower(load)}
        </div>
      </div>

      {/* Solar */}
      <div className="absolute top-8 left-1/2 -translate-x-1/2 flex flex-col items-center z-10 w-40">
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-700 w-full text-center shadow-lg">
          <div className="flex items-center justify-center gap-2 text-yellow-400 font-bold text-xs tracking-wider mb-2">
            <Sun size={14} /> SOLAR ARRAY
          </div>
          <div className="text-lg font-mono font-bold text-white">{formatPower(solar)}</div>
          <div className="text-[10px] text-emerald-400 mt-1 flex items-center justify-center gap-1">
            <div className={`w-1.5 h-1.5 rounded-full ${solar > 0 ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`}></div>
            {solar > 0 ? 'Producing' : 'Standby'}
          </div>
        </div>
      </div>
      
      {/* Wind */}
      <div className="absolute top-1/2 left-[15%] -translate-y-1/2 flex flex-col items-center z-10 w-40">
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-700 w-full text-center shadow-lg">
          <div className="flex items-center justify-center gap-2 text-blue-400 font-bold text-xs tracking-wider mb-2">
            <Wind size={14} /> WIND MAST
          </div>
          <div className="text-lg font-mono font-bold text-white">{formatPower(wind)}</div>
          <div className="text-[10px] text-emerald-400 mt-1 flex items-center justify-center gap-1">
            <div className={`w-1.5 h-1.5 rounded-full ${wind > 0 ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`}></div>
            {wind > 0 ? 'Generating' : 'Calm'}
          </div>
        </div>
      </div>

      {/* Battery */}
      <div className="absolute top-1/2 right-[15%] -translate-y-1/2 flex flex-col items-center z-10 w-40">
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-700 w-full text-center shadow-lg">
          <div className="flex items-center justify-center gap-2 text-indigo-400 font-bold text-xs tracking-wider mb-2">
            <Battery size={14} /> BATTERY BESS
          </div>
          <div className="text-lg font-mono font-bold text-white">
            {battery > 0 ? '+' : ''}{formatPower(battery)}
          </div>
          <div className="text-[10px] text-slate-300 mt-1">
            SOC: 66.2% <span className={battery > 0 ? "text-emerald-400" : (battery < 0 ? "text-indigo-400" : "")}>
              ({battery > 0 ? 'Discharging' : (battery < 0 ? 'Charging' : 'Idle')})
            </span>
          </div>
        </div>
      </div>

      {/* Diesel */}
      <div className="absolute bottom-8 left-[30%] -translate-x-1/2 flex flex-col items-center z-10 w-40">
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-700 w-full text-center shadow-lg">
          <div className="flex items-center justify-center gap-2 text-red-400 font-bold text-xs tracking-wider mb-2">
            <Droplet size={14} /> DIESEL GENSET
          </div>
          <div className="text-lg font-mono font-bold text-white">{formatPower(diesel)}</div>
          <div className="text-[10px] text-slate-400 mt-1 flex items-center justify-center gap-1">
            <div className={`w-1.5 h-1.5 rounded-full ${diesel > 0 ? 'bg-red-500 animate-pulse' : 'bg-slate-600'}`}></div>
            {diesel > 0 ? 'Running' : 'Standby Reserve'}
          </div>
        </div>
      </div>

      {/* Load */}
      <div className="absolute bottom-[10%] right-[30%] translate-x-1/2 flex flex-col items-center z-10 w-48">
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-700 w-full text-center shadow-lg border-b-2 border-b-emerald-500">
          <div className="flex items-center justify-center gap-2 text-purple-400 font-bold text-xs tracking-wider mb-2">
            <Zap size={14} /> COMMUNITY DEMAND
          </div>
          <div className="text-lg font-mono font-bold text-white">{formatPower(load)}</div>
          <div className="text-[10px] text-slate-400 mt-1">
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
    <Card className="bg-slate-900/80 border-slate-800 hover:bg-slate-800/80 transition-colors">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-xs font-bold text-slate-400 tracking-wider uppercase">{title}</CardTitle>
        <Icon className={cn("h-4 w-4", colorClass)} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-white">{value}</div>
        <p className={cn("text-[11px] mt-1 font-medium", highlight ? "text-emerald-400" : "text-slate-500")}>
          {highlight && <TrendingUp size={10} className="inline mr-1" />}
          {subValue}
        </p>
      </CardContent>
    </Card>
  );
}

export default function OverviewPage() {
  const router = useRouter();
  const { currency, powerScale, formatCurrency, formatPower } = useSettings();
  
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
        Solar: Math.max(0, s),
        Wind: w,
        Diesel: s + w < l ? Math.min(20, l - (s + w)) : 0, // Very little diesel
      });
    }
    setGraphData(initial);

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
  }, []);

  return (
    <div className="space-y-6 pb-12">
      
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
            Executive Overview 
            <span className="text-[10px] font-bold bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/30 uppercase tracking-wider">
              Kutch Rural Microgrid
            </span>
          </h2>
          <p className="text-slate-400 text-sm mt-1">Real-time renewable dispatch, battery storage state of charge, and avoided diesel emissions</p>
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
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold text-xs rounded-md transition-all flex items-center gap-2"
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
      <Card className="bg-slate-900/50 border-slate-800">
        <CardHeader className="flex flex-row items-center justify-between pb-2 border-b border-slate-800/50">
          <div>
            <CardTitle className="text-sm font-bold text-white flex items-center gap-2">
              Live Microgrid Bus & Power Flow
              <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded border border-emerald-500/20 tracking-wider">
                SYNCED 50.02 Hz
              </span>
            </CardTitle>
            <p className="text-[11px] text-slate-500 mt-1">Dynamic SVG power transmission animated by real-time telemetry magnitude and flow direction</p>
          </div>
          <div className="text-xs text-slate-400">
            <span className="font-bold text-emerald-400 mr-2">Renewable: 36.1%</span> | <span className="ml-2 font-mono">Bus: 404.5 V</span>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          <EnergyFlowDiagram data={liveData} formatPower={formatPower} />
          
          <div className="flex justify-between items-center mt-4">
            <div className="flex items-center gap-4 text-[10px] text-slate-400 font-medium tracking-wide">
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
        <Card className="col-span-2 bg-slate-900/50 border-slate-800">
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-bold text-white">Dispatch Trajectory (Today's Profile)</CardTitle>
              <Link href="/dispatch" className="text-xs text-emerald-400 hover:text-emerald-300 font-bold">Full Dispatch →</Link>
            </div>
            <p className="text-[11px] text-slate-500">Hourly multi-source power balance: Solar, Wind, BESS, Diesel vs Demand</p>
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
                <XAxis dataKey="time" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', fontSize: '12px' }}
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
        <Card className="col-span-1 bg-slate-900/50 border-slate-800 flex flex-col">
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-bold text-emerald-400 flex items-center gap-2">
                <Activity size={16} /> AI Energy Intelligence
              </CardTitle>
              <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">Gemini 2.0</span>
            </div>
          </CardHeader>
          <CardContent className="pt-4 flex-1 flex flex-col justify-between text-sm text-slate-300">
            <div className="space-y-4">
              <p className="leading-relaxed">
                Operating in high-efficiency renewable mode. Solar and wind are presently meeting <span className="text-white font-bold">40.9%</span> of community load. The battery is functioning within its healthy 20-95% lifecycle envelope. Keep diesel in automated standby.
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
              className="mt-6 w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-emerald-400 text-xs font-bold rounded-lg border border-slate-700 transition-colors"
            >
              Review LP Mathematical Formulation →
            </button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
