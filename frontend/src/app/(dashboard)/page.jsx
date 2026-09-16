'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Leaf, Droplet, Zap, Battery, CircleDollarSign, Wind, Sun, CloudRain, ArrowRight, Activity, TrendingUp, CheckCircle2, FlaskConical } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useSettings, LOCATIONS } from '@/contexts/SettingsContext';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Legend } from 'recharts';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

// Flow Diagram Component with SVG lines
function EnergyFlowDiagram({ data, formatPower, mode, simScenario }) {
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
        <line x1="50%" y1="20%" x2="50%" y2="50%" stroke={solar > 0 ? mode === 'SIMULATION' && simScenario === 'solar_drop' ? "#f59e0b" : "#10b981" : "#334155"} strokeWidth="2" strokeDasharray={solar > 0 ? "5,5" : ""} className={solar > 0 ? "animate-[dash_1s_linear_infinite]" : ""} />
        {/* Wind to Bus */}
        <line x1="30%" y1="50%" x2="50%" y2="50%" stroke={wind > 0 ? "#10b981" : "#334155"} strokeWidth="2" strokeDasharray={wind > 0 ? "5,5" : ""} className={wind > 0 ? "animate-[dash_1s_linear_infinite]" : ""} />
        {/* Battery to Bus */}
        <line x1="70%" y1="50%" x2="50%" y2="50%" stroke={battery !== 0 ? battery > 0 ? "#10b981" : "#6366f1" : "#334155"} strokeWidth="2" strokeDasharray={battery !== 0 ? "5,5" : ""} className={battery !== 0 ? "animate-[dash_1s_linear_infinite]" : ""} />
        {/* Diesel to Bus */}
        <line x1="40%" y1="80%" x2="50%" y2="50%" stroke={diesel > 0 ? "#ef4444" : "#334155"} strokeWidth="2" strokeDasharray={diesel > 0 ? "5,5" : ""} className={diesel > 0 ? "animate-[dash_1s_linear_infinite]" : ""} />
        {/* Bus to Load */}
        <line x1="50%" y1="50%" x2="60%" y2="80%" stroke={mode === 'SIMULATION' && simScenario === 'demand_spike' ? "#f59e0b" : "#10b981"} strokeWidth="3" strokeDasharray="5,5" className="animate-[dash_1s_linear_infinite]" />
      </svg>

      {/* Central Bus */}
      <div className={cn(
        "absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-surface-container px-6 py-4 rounded-xl border-2 z-10 font-bold text-center transition-all",
        mode === 'SIMULATION' ?
        "border-amber-500 text-amber-300 shadow-[0_0_20px_rgba(245,158,11,0.25)]" :
        "border-emerald-500 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.2)]"
      )}>
        <div className="text-[10px] tracking-widest text-outline uppercase mb-1">
          {mode === 'SIMULATION' ? 'Testbed Bus' : 'Microgrid Bus'}
        </div>
        <div className="text-sm">3-Phase 415V</div>
        <div className={cn(
          "mt-2 px-2 py-1 rounded border text-on-surface",
          mode === 'SIMULATION' ? "bg-amber-950/60 border-amber-500/40 text-amber-200" : "bg-emerald-900/50 border-emerald-500/30"
        )}>
          Net: {formatPower(load)}
        </div>
      </div>

      {/* Solar */}
      <div className="absolute top-8 left-1/2 -translate-x-1/2 flex flex-col items-center z-10 w-44">
        <div className="bg-surface p-3 rounded-lg border border-outline w-full text-center shadow-lg">
          <div className="flex items-center justify-center gap-2 text-yellow-400 font-bold text-xs tracking-wider mb-2">
            <Sun size={14} /> SOLAR ARRAY
          </div>
          <div className="text-lg font-mono font-bold text-on-surface">{formatPower(solar)}</div>
          <div className="text-[10px] mt-1 flex items-center justify-center gap-1 font-medium">
            <div className={`w-1.5 h-1.5 rounded-full ${solar > 0 ? mode === 'SIMULATION' && simScenario === 'solar_drop' ? 'bg-amber-400 animate-pulse' : 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`}></div>
            <span className={mode === 'SIMULATION' && simScenario === 'solar_drop' ? "text-amber-400" : "text-emerald-400"}>
              {mode === 'SIMULATION' && simScenario === 'solar_drop' ? 'Cloud Attenuated (-60%)' : solar > 0 ? 'Producing' : 'Standby'}
            </span>
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
          <div className="text-[10px] text-emerald-400 mt-1 flex items-center justify-center gap-1 font-medium">
            <div className={`w-1.5 h-1.5 rounded-full ${wind > 0 ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`}></div>
            {wind > 0 ? 'Generating' : 'Calm'}
          </div>
        </div>
      </div>

      {/* Battery */}
      <div className="absolute top-1/2 left-[70%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center z-10 w-44">
        <div className="bg-surface p-3 rounded-lg border border-outline w-full text-center shadow-lg">
          <div className="flex items-center justify-center gap-2 text-indigo-400 font-bold text-xs tracking-wider mb-2">
            <Battery size={14} /> BATTERY BESS
          </div>
          <div className="text-lg font-mono font-bold text-on-surface">
            {battery > 0 ? '+' : ''}{formatPower(battery)}
          </div>
          <div className="text-[10px] text-on-surface-variant mt-1 font-medium">
            SOC: {mode === 'SIMULATION' && simScenario === 'solar_drop' ? '44.8%' : mode === 'SIMULATION' && simScenario === 'generator_failure' ? '38.6%' : '66.2%'}{' '}
            <span className={battery > 0 ? "text-emerald-400" : battery < 0 ? "text-indigo-400" : ""}>
              ({battery > 0 ? 'Discharging' : battery < 0 ? 'Charging' : 'Idle'})
            </span>
          </div>
        </div>
      </div>

      {/* Diesel */}
      <div className="absolute top-[80%] left-[40%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center z-10 w-44">
        <div className="bg-surface p-3 rounded-lg border border-outline w-full text-center shadow-lg">
          <div className="flex items-center justify-center gap-2 text-red-400 font-bold text-xs tracking-wider mb-2">
            <Droplet size={14} /> DIESEL GENSET
          </div>
          <div className="text-lg font-mono font-bold text-on-surface">{formatPower(diesel)}</div>
          <div className="text-[10px] text-outline mt-1 flex items-center justify-center gap-1 font-medium">
            <div className={`w-1.5 h-1.5 rounded-full ${diesel > 0 ? 'bg-red-500 animate-pulse' : mode === 'SIMULATION' && simScenario === 'generator_failure' ? 'bg-red-600' : 'bg-slate-600'}`}></div>
            <span className={mode === 'SIMULATION' && simScenario === 'generator_failure' ? "text-red-400 font-bold" : ""}>
              {mode === 'SIMULATION' && simScenario === 'generator_failure' ? 'TRIPPED / 0 kW' : diesel > 0 ? 'Running' : 'Standby Reserve'}
            </span>
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
          <div className="text-[10px] text-on-surface-variant mt-1 font-medium">
            {mode === 'SIMULATION' && simScenario === 'demand_spike' ?
            <span className="text-amber-400 font-bold">Surge Peak (+35%) Active</span> :

            'Village & Commercial load'
            }
          </div>
        </div>
      </div>
      
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes dash {
          to {
            stroke-dashoffset: -10;
          }
        }
      ` }} />
    </div>);

}

function KpiCard({ title, value, subValue, icon: Icon, colorClass, highlight }) {
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
    </Card>);

}

export default function OverviewPage() {
  const router = useRouter();
  const {
    currency, powerScale, formatCurrency, formatPower, locationId,
    mode, simScenario, setMode, setSimScenario
  } = useSettings();

  const currentLoc = LOCATIONS.find((l) => l.id === locationId);
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

  const [graphData, setGraphData] = useState([]);

  useEffect(() => {
    // Determine baseline numbers depending on mode and simScenario
    let baseSolar = 145.2;
    let baseWind = 84.4;
    let baseLoad = 194.0;
    let baseDiesel = 0;

    if (mode === 'SIMULATION') {
      if (simScenario === 'nominal') {
        baseSolar = 125.0;
        baseWind = 68.0;
        baseLoad = 175.0;
        baseDiesel = 0;
      } else if (simScenario === 'solar_drop') {
        baseSolar = 32.0; // severe drop
        baseWind = 42.0;
        baseLoad = 194.0;
        baseDiesel = 45.0; // diesel fired to cover gap
      } else if (simScenario === 'demand_spike') {
        baseSolar = 140.0;
        baseWind = 75.0;
        baseLoad = 275.0; // peak surge
        baseDiesel = 30.0;
      } else if (simScenario === 'generator_failure') {
        baseSolar = 110.0;
        baseWind = 35.0;
        baseLoad = 185.0;
        baseDiesel = 0; // generator tripped
      }
    }

    const sVal = baseSolar * locScale;
    const wVal = baseWind * locScale;
    const lVal = baseLoad * Math.max(0.7, locScale);
    const dVal = baseDiesel * locScale;
    const bVal = lVal - sVal - wVal - dVal; // net BESS flow

    // Generate initial 24h graph data
    const initial = [];
    const now = new Date();
    for (let i = 24; i >= 0; i--) {
      const d = new Date(now.getTime() - i * 60 * 60 * 1000);
      const hour = d.getHours();

      let s = 0;
      if (hour > 6 && hour < 19) {
        const peak = mode === 'SIMULATION' && simScenario === 'solar_drop' ? 45 : 150;
        s = Math.sin((hour - 6) / 13 * Math.PI) * peak;
      }

      const bLoad = mode === 'SIMULATION' && simScenario === 'demand_spike' ? 120 : 80;
      const morningPeak = hour >= 7 && hour <= 10 ? 40 : 0;
      const eveningPeak = hour >= 18 && hour <= 22 ? mode === 'SIMULATION' && simScenario === 'demand_spike' ? 95 : 60 : 0;
      const l = bLoad + morningPeak + eveningPeak + Math.random() * 10;
      const w = 20 + Math.random() * 30;

      const dieselOut = mode === 'SIMULATION' && simScenario === 'generator_failure' ? 0 : s + w < l ? Math.min(30, l - (s + w)) : 0;

      initial.push({
        time: `${hour.toString().padStart(2, '0')}:00`,
        Solar: Math.max(0, s) * locScale,
        Wind: w * locScale,
        Diesel: dieselOut * (2 - locScale)
      });
    }
    setGraphData(initial);

    // Reset base live data instantly to match settings and simulation
    setLiveData({
      solar: Math.round(sVal * 10) / 10,
      wind: Math.round(wVal * 10) / 10,
      battery: Math.round(bVal * 10) / 10,
      diesel: Math.round(dVal * 10) / 10,
      load: Math.round(lVal * 10) / 10
    });

    // Live ticker
    const interval = setInterval(() => {
      setLiveData((prev) => {
        const jitterWind = Math.random() * 6 - 3;
        const jitterLoad = Math.random() * 6 - 3;
        const newWind = Math.max(0, prev.wind + jitterWind);
        const newLoad = Math.max(50, prev.load + jitterLoad);
        let newDiesel = prev.diesel;
        if (mode === 'SIMULATION' && simScenario === 'generator_failure') {
          newDiesel = 0;
        }
        const newBatt = newLoad - newWind - prev.solar - newDiesel;

        return {
          ...prev,
          wind: Math.round(newWind * 10) / 10,
          load: Math.round(newLoad * 10) / 10,
          diesel: newDiesel,
          battery: Math.round(newBatt * 10) / 10
        };
      });

      setGraphData((current) => {
        const newArr = [...current];
        const last = { ...newArr[newArr.length - 1] };
        last.Wind = liveData.wind;
        newArr[newArr.length - 1] = last;
        return newArr;
      });

    }, 2500);

    return () => clearInterval(interval);
  }, [locScale, mode, simScenario]);

  // Compute reactive KPI figures
  const renShare = mode === 'SIMULATION' && simScenario === 'solar_drop' ?
  '38.2%' :
  mode === 'SIMULATION' && simScenario === 'generator_failure' ? '100.0%' : '76.4%';
  const dieselDep = mode === 'SIMULATION' && simScenario === 'solar_drop' ?
  '23.2%' :
  mode === 'SIMULATION' && simScenario === 'demand_spike' ? '10.9%' : '0%';
  const battSoc = mode === 'SIMULATION' && simScenario === 'solar_drop' ?
  '44.8%' :
  mode === 'SIMULATION' && simScenario === 'generator_failure' ? '38.6%' : '66.2%';

  return (
    <div className="space-y-6 pb-12">
      
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-on-surface flex items-center gap-3">
            Executive Overview 
            <span className={cn(
              "text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider",
              mode === 'SIMULATION' ?
              "bg-amber-500/20 text-amber-300 border-amber-500/30" :
              "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
            )}>
              {locName} • {mode === 'SIMULATION' ? 'SIMULATION' : 'LIVE SCADA'}
            </span>
          </h2>
          <p className="text-outline text-sm mt-1">Real-time renewable dispatch, battery storage state of charge, and avoided diesel emissions</p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push('/optimizer')}
            className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs rounded-md shadow-lg shadow-emerald-500/20 transition-all flex items-center gap-2">
            
            <Activity size={14} /> Launch Optimizer
          </button>
          <button
            onClick={() => router.push('/demand')}
            className="px-4 py-2 bg-surface-container hover:bg-slate-700 text-on-surface border border-outline font-bold text-xs rounded-md transition-all flex items-center gap-2">
            
            <Zap size={14} /> Fuel & Demand
          </button>
        </div>
      </div>

      {/* Simulation Notice Banner */}
      {mode === 'SIMULATION' &&
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3.5 flex items-center justify-between text-xs text-amber-200 animate-in fade-in">
          <div className="flex items-center gap-2.5">
            <FlaskConical size={18} className="text-amber-400 shrink-0 animate-pulse" />
            <div>
              <span className="font-bold text-amber-300">Simulation Testbed Active: </span>
              <span>
                {simScenario === 'nominal' && "Baseline synthetic simulation running without physical relay lockouts."}
                {simScenario === 'solar_drop' && "Heavy cloud transient (-60% PV). Solar irradiance depleted; BESS inverter and diesel generator ramped up."}
                {simScenario === 'demand_spike' && "Evening village & commercial demand surge (+35%). Spinning reserves dynamically engaged."}
                {simScenario === 'generator_failure' && "Diesel genset alternator trip (0 kW). Isolated grid surviving solely on Solar + Wind + BESS."}
              </span>
            </div>
          </div>
          <button
          onClick={() => setMode('LIVE')}
          className="px-2.5 py-1 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 rounded text-amber-300 font-semibold shrink-0 ml-4 transition-colors">
          
            Restore Live SCADA
          </button>
        </div>
      }

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <KpiCard
          title="Renewable Share"
          value={renShare}
          subValue={mode === 'SIMULATION' ? "Simulated Mix" : "+4.2% vs yesterday"}
          icon={Leaf}
          colorClass={mode === 'SIMULATION' && simScenario === 'solar_drop' ? "text-amber-400" : "text-emerald-500"}
          highlight={mode === 'LIVE'} />
        
        <KpiCard
          title="Diesel Dependency"
          value={dieselDep}
          subValue={mode === 'SIMULATION' && simScenario === 'solar_drop' ? "Reserve Fired (+23%)" : mode === 'SIMULATION' && simScenario === 'generator_failure' ? "Genset Tripped" : "-8.1% vs baseline"}
          icon={Droplet}
          colorClass={dieselDep === '0%' ? "text-emerald-500" : "text-red-500"}
          highlight={dieselDep === '0%'} />
        
        <KpiCard title="Current Load" value={formatPower(liveData.load)} subValue={`Peak: ${formatPower(mode === 'SIMULATION' && simScenario === 'demand_spike' ? 285 : 184)}`} icon={Zap} colorClass="text-yellow-500" />
        <KpiCard title="Battery SOC" value={battSoc} subValue={mode === 'SIMULATION' && (simScenario === 'solar_drop' || simScenario === 'generator_failure') ? "Rapid Discharging" : "330.9 kWh avail"} icon={Battery} colorClass="text-indigo-500" />
        <KpiCard title="Operating Cost" value={formatCurrency(mode === 'SIMULATION' && simScenario === 'solar_drop' ? 124000 : 88459)} subValue={mode === 'SIMULATION' ? "Scenario Rate" : `Save ${formatCurrency(29310)}`} icon={CircleDollarSign} colorClass="text-emerald-500" highlight={mode === 'LIVE'} />
        <KpiCard title="CO₂ Avoided" value={mode === 'SIMULATION' && simScenario === 'solar_drop' ? "1820.0 kg" : "3522.1 kg"} subValue={mode === 'SIMULATION' ? "Simulated Offset" : "-63% vs diesel-only"} icon={CloudRain} colorClass="text-blue-400" highlight={true} />
      </div>

      {/* Main Flow Diagram */}
      <Card className="bg-surface/50 border-outline-variant">
        <CardHeader className="flex flex-row items-center justify-between pb-2 border-b border-outline-variant">
          <div>
            <CardTitle className="text-sm font-bold text-on-surface flex items-center gap-2">
              {mode === 'SIMULATION' ? 'Simulation Bus Telemetry' : 'Live Microgrid Bus & Power Flow'}
              <span className={cn(
                "text-[10px] px-1.5 py-0.5 rounded border tracking-wider uppercase font-semibold",
                mode === 'SIMULATION' ?
                "bg-amber-500/15 text-amber-300 border-amber-500/30" :
                "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
              )}>
                {mode === 'SIMULATION' ? `TESTBED • ${simScenario.toUpperCase()}` : 'SYNCED 50.02 Hz'}
              </span>
            </CardTitle>
            <p className="text-[11px] text-outline mt-1">Dynamic SVG power transmission animated by real-time telemetry magnitude and flow direction</p>
          </div>
          <div className="text-xs text-outline">
            <span className={cn("font-bold mr-2", mode === 'SIMULATION' && simScenario === 'solar_drop' ? "text-amber-400" : "text-emerald-400")}>
              Renewable: {renShare}
            </span> | <span className="ml-2 font-mono">Bus: 404.5 V</span>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          <EnergyFlowDiagram data={liveData} formatPower={formatPower} mode={mode} simScenario={simScenario} />
          
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
                    <stop offset="5%" stopColor="#fbbf24" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#fbbf24" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorWind" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#60a5fa" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#60a5fa" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorDiesel" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f87171" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#f87171" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => formatPower(val)} />
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <RechartsTooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', fontSize: '12px' }}
                  itemStyle={{ fontWeight: 'bold' }} />
                
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
              className="mt-6 w-full py-2.5 bg-surface-container hover:bg-slate-700 text-emerald-400 text-xs font-bold rounded-lg border border-outline transition-colors">
              
              Review LP Mathematical Formulation →
            </button>
          </CardContent>
        </Card>
      </div>
    </div>);

}