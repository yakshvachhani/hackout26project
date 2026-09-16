'use client';

import { useSettings } from '@/contexts/SettingsContext';
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  LineChart, Line, ComposedChart, Bar, Legend
} from 'recharts';
import { Activity, Sun, Wind, Battery, Droplet, Zap, ShieldAlert } from 'lucide-react';

export default function DispatchPage() {
  const { currency, powerScale, formatPower, mode, simScenario } = useSettings();
  const [data, setData] = useState<any[]>([]);
  const [liveData, setLiveData] = useState({
    solar: 1800,
    wind: 31800,
    battery: 62400,
    diesel: 0,
    demand: 96000,
    reserve: 212400
  });

  const [timeRange, setTimeRange] = useState(24);

  useEffect(() => {
    // Generate initial 24h data based on mode and scenario
    const initial = [];
    const now = new Date();
    for(let i = 24; i >= 0; i--) {
      const d = new Date(now.getTime() - i * 60 * 60 * 1000);
      const hour = d.getHours();
      
      let solarPeak = 180;
      if (mode === 'SIMULATION' && simScenario === 'solar_drop') {
        solarPeak = 55; // attenuated
      }
      let s = (hour > 6 && hour < 19) ? Math.sin((hour - 6) / 13 * Math.PI) * solarPeak : 0;
      let baseLoad = 80;
      if (mode === 'SIMULATION' && simScenario === 'demand_spike') {
        baseLoad = 115; // surge
      }
      const morningPeak = hour >= 7 && hour <= 10 ? 40 : 0;
      const eveningPeak = hour >= 18 && hour <= 22 ? (mode === 'SIMULATION' && simScenario === 'demand_spike' ? 85 : 60) : 0;
      const demand = baseLoad + morningPeak + eveningPeak + Math.random() * 10;
      const w = 20 + Math.random() * 30;
      
      let batteryDischarge = 0;
      let batteryCharge = 0;
      let diesel = 0;
      
      const gen = s + w;
      if (gen > demand) {
        batteryCharge = Math.min(gen - demand, 50); // cap charging
      } else if (gen < demand) {
        const deficit = demand - gen;
        if (mode === 'SIMULATION' && simScenario === 'generator_failure') {
          // Generator tripped: BESS takes full deficit
          batteryDischarge = Math.min(deficit, 100);
          diesel = 0;
        } else {
          batteryDischarge = Math.min(deficit, 60);
          if (deficit > 60) {
            diesel = deficit - 60;
          }
        }
      }

      initial.push({
        time: `${hour.toString().padStart(2, '0')}:00`,
        solar: s * 1000,
        wind: w * 1000,
        batteryDischarge: batteryDischarge * 1000,
        batteryCharge: -batteryCharge * 1000,
        diesel: diesel * 1000,
        demand: demand * 1000,
        reserveMargin: Math.max(0, (250 + 100 + 500) * 1000 - (demand * 1000)),
        availableSolar: (s + 20) * 1000,
        curtailedEnergy: batteryCharge === 50 ? (gen - demand - 50) * 1000 : 0,
        curtailmentRate: batteryCharge === 50 ? 5 : 0
      });
    }
    setData(initial);

    const interval = setInterval(() => {
      setLiveData(prev => {
        const newWind = Math.max(0, prev.wind + (Math.random() * 1000 - 500));
        const newDemand = Math.max(50000, prev.demand + (Math.random() * 2000 - 1000));
        return {
          ...prev,
          wind: newWind,
          demand: newDemand
        };
      });

      setData(current => {
        const newArr = [...current];
        const last = { ...newArr[newArr.length - 1] };
        
        last.wind = liveData.wind;
        last.demand = liveData.demand;
        // recalculate balances
        const gen = (last.solar || 0) + (last.wind || 0);
        if (gen > last.demand) {
          last.batteryCharge = -Math.min(gen - last.demand, 50000);
          last.batteryDischarge = 0;
          last.diesel = 0;
        } else {
          last.batteryCharge = 0;
          const deficit = last.demand - gen;
          if (mode === 'SIMULATION' && simScenario === 'generator_failure') {
            last.batteryDischarge = Math.min(deficit, 100000);
            last.diesel = 0;
          } else {
            last.batteryDischarge = Math.min(deficit, 60000);
            last.diesel = deficit > 60000 ? deficit - 60000 : 0;
          }
        }
        
        newArr[newArr.length - 1] = last;
        return newArr;
      });
    }, 3000);

    return () => clearInterval(interval);
  }, [mode, simScenario]);

  const displayData = data.slice(-(timeRange + 1));

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-outline-variant pb-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-on-surface flex items-center gap-3">
            Live Dispatch & Power Balance
            {mode === 'SIMULATION' ? (
              <span className="text-[10px] font-bold bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded border border-amber-500/30 uppercase tracking-wider flex items-center gap-1 animate-pulse">
                <ShieldAlert size={10} /> SCADA: SIMULATION INJECTION ({simScenario.toUpperCase()})
              </span>
            ) : (
              <span className="text-[10px] font-bold bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/30 uppercase tracking-wider flex items-center gap-1">
                <Activity size={10} /> SCADA: SYNC
              </span>
            )}
          </h2>
          <p className="text-outline text-sm mt-1">Real-time multi-interval generation matching, spinning reserve verification, and curtailment tracking</p>
        </div>
        
        <div className="flex bg-surface rounded-md border border-outline p-1">
          {[1, 6, 12, 24].map(hours => (
            <button 
              key={hours}
              onClick={() => setTimeRange(hours)}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${timeRange === hours ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-outline hover:text-on-surface border border-transparent'}`}
            >
              {hours}h
            </button>
          ))}
        </div>
      </div>

      {/* Matrix */}
      <Card className="bg-surface/50 border-outline-variant">
        <CardHeader className="pb-3 border-b border-outline-variant">
          <CardTitle className="text-sm font-bold flex items-center gap-2 text-on-surface">
            <Activity size={16} className="text-emerald-500" />
            Real-Time Power Balance Matrix (Instantaneous Telemetry)
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="space-y-1">
            <div className="text-[10px] font-bold text-yellow-500 uppercase flex items-center gap-1"><Sun size={10}/> Solar Array</div>
            <div className="text-xl font-bold text-on-surface">{formatPower(liveData.solar)}</div>
            <div className="text-[10px] text-outline">Cap: {formatPower(250000)}</div>
          </div>
          <div className="space-y-1 border-l border-outline-variant pl-4">
            <div className="text-[10px] font-bold text-blue-500 uppercase flex items-center gap-1"><Wind size={10}/> Wind Turbine</div>
            <div className="text-xl font-bold text-on-surface">{formatPower(liveData.wind)}</div>
            <div className="text-[10px] text-outline">Cap: {formatPower(100000)}</div>
          </div>
          <div className="space-y-1 border-l border-outline-variant pl-4">
            <div className="text-[10px] font-bold text-indigo-400 uppercase flex items-center gap-1"><Battery size={10}/> BESS Power</div>
            <div className="text-xl font-bold text-emerald-400">+{formatPower(liveData.battery)}</div>
            <div className="text-[10px] text-outline">Discharging</div>
          </div>
          <div className="space-y-1 border-l border-outline-variant pl-4">
            <div className="text-[10px] font-bold text-red-500 uppercase flex items-center gap-1"><Droplet size={10}/> Diesel Genset</div>
            <div className="text-xl font-bold text-on-surface">{formatPower(liveData.diesel)}</div>
            <div className="text-[10px] text-outline">Cap: {formatPower(750000)}</div>
          </div>
          <div className="space-y-1 border-l border-outline-variant pl-4">
            <div className="text-[10px] font-bold text-purple-400 uppercase flex items-center gap-1"><Zap size={10}/> Total Demand</div>
            <div className="text-xl font-bold text-on-surface">{formatPower(liveData.demand)}</div>
            <div className="text-[10px] text-emerald-500">Deficit: 0 {powerScale}</div>
          </div>
          <div className="space-y-1 border-l border-outline-variant pl-4">
            <div className="text-[10px] font-bold text-emerald-500 uppercase flex items-center gap-1"><ShieldAlert size={10}/> Spinning Reserve</div>
            <div className="text-xl font-bold text-emerald-400">{formatPower(liveData.reserve)}</div>
            <div className="text-[10px] text-outline">N-1 Compliant</div>
          </div>
        </CardContent>
      </Card>

      {/* Graph 1 */}
      <Card className="bg-surface border-outline-variant">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle className="text-sm font-bold text-on-surface">Graph 1: Power Mix by Source (24h Interval)</CardTitle>
            <p className="text-[10px] text-outline mt-1">Stacked generation (Solar, Wind, Diesel, Battery) vs Community Load Demand curve</p>
          </div>
          <div className="text-[10px] bg-surface-container px-2 py-1 rounded text-emerald-400 font-mono">Panel Yield Opt: 99%</div>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={displayData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorSolar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#d97706" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#d97706" stopOpacity={0.1}/>
                  </linearGradient>
                  <linearGradient id="colorWind" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0891b2" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#0891b2" stopOpacity={0.1}/>
                  </linearGradient>
                  <linearGradient id="colorBatt" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#4f46e5" stopOpacity={0.1}/>
                  </linearGradient>
                  <linearGradient id="colorDiesel" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#be123c" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#be123c" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="time" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(val) => `${(val/1000).toFixed(0)} kW`} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', fontSize: '12px' }}
                  itemStyle={{ fontWeight: 'bold' }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                
                <Area type="monotone" dataKey="batteryDischarge" stackId="1" stroke="#4f46e5" fill="url(#colorBatt)" name="Battery Discharge" />
                <Area type="monotone" dataKey="diesel" stackId="1" stroke="#be123c" fill="url(#colorDiesel)" name="Diesel Genset" />
                <Area type="monotone" dataKey="solar" stackId="1" stroke="#d97706" fill="url(#colorSolar)" name="Solar" />
                <Area type="monotone" dataKey="wind" stackId="1" stroke="#0891b2" fill="url(#colorWind)" name="Wind" />
                
                <Line type="monotone" dataKey="demand" stroke="#10b981" strokeWidth={2} dot={false} name="Community Demand" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Graph 2 */}
        <Card className="bg-surface border-outline-variant">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle className="text-sm font-bold text-on-surface">Graph 2: Load vs Generation Imbalance</CardTitle>
              <p className="text-[10px] text-outline mt-1">Demand matched vs spinning reserves & unserved energy</p>
            </div>
            <div className="text-[10px] bg-emerald-500/20 px-2 py-1 rounded text-emerald-400 font-mono flex items-center gap-1">
              <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full"></div> 16x Reserved
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[200px] w-full mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={displayData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                  <XAxis dataKey="time" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(val) => `${(val/1000).toFixed(0)} kW`} />
                  <RechartsTooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', fontSize: '11px' }} />
                  <Legend iconType="plainline" wrapperStyle={{ fontSize: '11px' }} />
                  <Line type="monotone" dataKey="demand" stroke="#8b5cf6" strokeWidth={2} dot={false} name="Demand" />
                  <Line type="monotone" dataKey="reserveMargin" stroke="#10b981" strokeWidth={1} strokeDasharray="5 5" dot={false} name="Reserve Margin" />
                  <Line type="monotone" dataKey="solar" stroke="#eab308" strokeWidth={1.5} dot={false} name="Solar" />
                  <Line type="monotone" dataKey="wind" stroke="#3b82f6" strokeWidth={1.5} dot={false} name="Wind" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Graph 4 */}
        <Card className="bg-surface border-outline-variant">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle className="text-sm font-bold text-on-surface">Graph 4: Renewable Curtailment Analysis</CardTitle>
              <p className="text-[10px] text-outline mt-1">Potential vs Absorbed Energy (BESS charging limits)</p>
            </div>
            <div className="text-[10px] text-outline font-mono">Curtailment Rate</div>
          </CardHeader>
          <CardContent>
            <div className="h-[200px] w-full mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={displayData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                  <XAxis dataKey="time" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(val) => `${(val/1000).toFixed(0)} kW`} />
                  <RechartsTooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', fontSize: '11px' }} />
                  <Legend wrapperStyle={{ fontSize: '11px' }} />
                  <Bar dataKey="availableSolar" fill="#ca8a04" barSize={10} name="Available Solar" />
                  <Bar dataKey="curtailedEnergy" fill="#be123c" barSize={10} name="Curtailed Energy" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Do NOT change Dispatch Timeline */}
      <Card className="bg-surface border-outline-variant">
        <CardHeader>
          <CardTitle className="text-sm font-bold text-on-surface">Graph 2: Dispatch Interval Timeline</CardTitle>
          <p className="text-[10px] text-outline mt-1">Dominant power supplier sequence determined by merit-order LP optimizer</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
             {displayData.filter((_, i) => i % Math.max(1, Math.floor(timeRange / 6)) === 0).map((row, i) => (
               <div key={i} className="flex items-center gap-4 border-b border-outline-variant pb-2 last:border-0">
                 <div className="text-sm font-mono text-outline w-16">{row.time}</div>
                 <div className="flex-1 flex gap-2">
                   {row.solar > 0 && <span className="px-2 py-1 bg-yellow-500/20 text-yellow-500 text-xs rounded border border-yellow-500/30">Solar</span>}
                   {row.wind > 0 && <span className="px-2 py-1 bg-blue-500/20 text-blue-500 text-xs rounded border border-blue-500/30">Wind</span>}
                   {row.batteryDischarge > 0 && <span className="px-2 py-1 bg-indigo-500/20 text-indigo-500 text-xs rounded border border-indigo-500/30">Battery</span>}
                   {row.diesel > 0 && <span className="px-2 py-1 bg-red-500/20 text-red-500 text-xs rounded border border-red-500/30">Diesel</span>}
                 </div>
                 <div className="text-sm text-emerald-400 font-mono">{formatPower(row.demand)}</div>
               </div>
             ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

