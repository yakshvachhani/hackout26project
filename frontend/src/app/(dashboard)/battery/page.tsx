'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Battery, Zap, ShieldCheck, RefreshCw, Thermometer } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip, ReferenceLine, LineChart, Line } from 'recharts';

export default function BatteryIntelligencePage() {
  // Real-time fluctuating states
  const [soc, setSoc] = useState(60.8);
  const [flow, setFlow] = useState(9.1);
  const [temp, setTemp] = useState(26.4);
  const [isDischarging, setIsDischarging] = useState(true);

  // API Data states
  const [socData, setSocData] = useState<any[]>([]);
  const [inverterData, setInverterData] = useState<any[]>([]);

  // Projected Degradation Data
  const degradationData = [
    { cycle: '0 cyc', retention: 100 },
    { cycle: '500 cyc', retention: 98.2 },
    { cycle: '1000 cyc', retention: 96.5 },
    { cycle: '1500 cyc', retention: 94.1 },
    { cycle: '2000 cyc', retention: 91.8 },
    { cycle: '2500 cyc', retention: 89.0 },
    { cycle: '3000 cyc', retention: 85.5 },
    { cycle: '3500 cyc', retention: 82.1 },
    { cycle: '4000 cyc', retention: 79.0 },
  ];

  useEffect(() => {
    // 1. Fetch API data
    const fetchData = async () => {
      try {
        const [battRes, dispRes] = await Promise.all([
          fetch('http://localhost:8000/api/battery'),
          fetch('http://localhost:8000/api/dispatch')
        ]);
        const battJson = await battRes.json();
        const dispJson = await dispRes.json();

        // Parse Battery SOC Curve
        if (Array.isArray(battJson)) {
          setSocData(battJson.map((d: any) => ({
            time: d.time,
            soc: d.soc
          })));
        }

        // Parse Dispatch Inverter Power (Positive = Discharge, Negative = Charge)
        if (Array.isArray(dispJson)) {
          setInverterData(dispJson.map((d: any) => {
            // Reversing the sign for charging so it plots below 0
            const discharge = d.batteryDischarge || 0;
            const charge = d.batteryCharge || 0; 
            // In API, batteryCharge is already negative, but let's ensure it.
            const netPower = discharge > 0 ? discharge : (charge < 0 ? charge : -charge);
            return {
              time: d.time,
              power: netPower
            };
          }));
        }
      } catch (err) {
        console.error("Failed to fetch battery data", err);
      }
    };
    
    fetchData();

    // 2. Real-time fluctuations simulator
    const interval = setInterval(() => {
      setSoc(prev => {
        const delta = isDischarging ? -0.01 : 0.01;
        return Number((prev + delta).toFixed(2));
      });
      
      setFlow(prev => {
        const jitter = (Math.random() - 0.5) * 0.4;
        return Number((prev + jitter).toFixed(1));
      });

      setTemp(prev => {
        const jitter = (Math.random() - 0.5) * 0.1;
        return Number((prev + jitter).toFixed(1));
      });
    }, 2500);

    return () => clearInterval(interval);
  }, [isDischarging]);

  // Custom tooltips
  const SocTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#0f172a] border border-slate-700 p-2 rounded shadow-xl text-xs">
          <span className="text-slate-400">{label}</span><br />
          <span className="text-emerald-500 font-bold">SOC: {payload[0].value}%</span>
        </div>
      );
    }
    return null;
  };

  const InverterTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const val = payload[0].value;
      return (
        <div className="bg-[#0f172a] border border-slate-700 p-2 rounded shadow-xl text-xs">
          <span className="text-slate-400">{label}</span><br />
          <span className={val >= 0 ? "text-emerald-500 font-bold" : "text-amber-400 font-bold"}>
            {val >= 0 ? `Discharging: ${val} kW` : `Charging: ${Math.abs(val)} kW`}
          </span>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6 pb-12 max-w-[1600px] mx-auto">
      
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h2 className="text-2xl font-bold tracking-tight text-white">Battery Energy Storage (BESS) Intelligence</h2>
            <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold rounded uppercase tracking-wider border border-emerald-500/20">
              LiFePO4 500 kWh
            </span>
          </div>
          <p className="text-slate-400 text-sm">Lithium Iron Phosphate storage cycling, degradation modeling, C-rate limits, and optimal absorption windows</p>
        </div>
        
        <div className="flex items-center gap-2 px-3 py-1.5 bg-[#0f172a] border border-slate-800/50 rounded-full">
          <Thermometer size={14} className="text-emerald-500" />
          <span className="text-xs text-slate-300 font-medium">Pack Temp: <span className="text-white font-bold">{temp.toFixed(1)}°C</span> (Nominal)</span>
        </div>
      </div>

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* SOC */}
        <Card className="bg-[#0f172a] border-slate-800/50 rounded-xl relative overflow-hidden">
          <CardContent className="p-5">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-bold text-slate-400">State of Charge (SOC)</span>
              <Battery size={16} className="text-emerald-500" />
            </div>
            <div className="text-3xl font-bold text-emerald-500 mb-3">{soc.toFixed(1)}%</div>
            
            {/* Progress Bar */}
            <div className="w-full h-1.5 bg-slate-800 rounded-full mb-2 overflow-hidden">
              <div className="h-full bg-emerald-500 rounded-full transition-all duration-500" style={{ width: `${soc}%` }}></div>
            </div>
            <p className="text-[10px] text-white0">{(soc * 5).toFixed(1)} kWh available</p>
          </CardContent>
        </Card>

        {/* Instantaneous Flow */}
        <Card className="bg-[#0f172a] border-slate-800/50 rounded-xl">
          <CardContent className="p-5">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-bold text-slate-400">Instantaneous Flow</span>
              <Zap size={16} className="text-emerald-500" />
            </div>
            <div className="text-3xl font-bold text-white mb-2 flex items-baseline gap-1">
              {flow > 0 ? '+' : ''}{flow.toFixed(1)} <span className="text-sm font-normal text-white0">kW</span>
            </div>
            <div className="flex items-center gap-1.5 mt-4">
              <div className={`w-1.5 h-1.5 rounded-full ${flow > 0 ? 'bg-emerald-500' : 'bg-amber-500'} animate-pulse`}></div>
              <p className={`text-[10px] font-bold ${flow > 0 ? 'text-emerald-500' : 'text-amber-500'}`}>
                {flow > 0 ? 'Discharging to Load' : 'Charging from Array'}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* SOH */}
        <Card className="bg-[#0f172a] border-slate-800/50 rounded-xl">
          <CardContent className="p-5">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-bold text-slate-400">State of Health (SOH)</span>
              <ShieldCheck size={16} className="text-emerald-500" />
            </div>
            <div className="text-3xl font-bold text-emerald-500 mb-4">97.4%</div>
            <p className="text-[10px] text-white0">842 Equivalent Full Cycles</p>
          </CardContent>
        </Card>

        {/* Efficiency */}
        <Card className="bg-[#0f172a] border-slate-800/50 rounded-xl">
          <CardContent className="p-5">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-bold text-slate-400">Roundtrip Efficiency</span>
              <RefreshCw size={16} className="text-blue-500" />
            </div>
            <div className="text-3xl font-bold text-blue-400 mb-4">91.8%</div>
            <p className="text-[10px] text-white0">Degradation cost: ₹1.40 / kWh</p>
          </CardContent>
        </Card>

      </div>

      {/* Middle Grid: 2 Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* SOC Profile Chart */}
        <Card className="bg-[#0f172a] border-slate-800/50 rounded-xl flex flex-col">
          <CardHeader className="pb-2">
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-sm font-bold text-white">Graph 1: Battery SOC Profile over 24h</CardTitle>
                <p className="text-xs text-slate-400 mt-1">Predicted state of charge respecting 20% reserve floor</p>
              </div>
              <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-wider">Safe: 20%-95%</span>
            </div>
          </CardHeader>
          <CardContent className="flex-1 min-h-[250px] pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={socData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 10}} dy={10} minTickGap={20} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 10}} domain={[0, 100]} tickFormatter={v => `${v}%`} />
                <Tooltip content={<SocTooltip />} cursor={{ stroke: '#334155', strokeWidth: 1, strokeDasharray: '4 4' }} />
                
                <ReferenceLine y={20} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'insideBottomRight', value: 'Reserve Floor (20%)', fill: '#ef4444', fontSize: 10 }} />
                
                <Area type="monotone" dataKey="soc" stroke="#10b981" fillOpacity={1} fill="url(#colorSoc)" strokeWidth={2} />
                
                <defs>
                  <linearGradient id="colorSoc" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Inverter Power Chart */}
        <Card className="bg-[#0f172a] border-slate-800/50 rounded-xl flex flex-col">
          <CardHeader className="pb-2">
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-sm font-bold text-white">Graph 2: Charge / Discharge Inverter Power</CardTitle>
                <p className="text-xs text-slate-400 mt-1">Positive = discharging to load. Negative = charging from solar</p>
              </div>
              <span className="text-[10px] font-bold text-white uppercase tracking-wider">Max: 120 kW</span>
            </div>
          </CardHeader>
          <CardContent className="flex-1 min-h-[250px] pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={inverterData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 10}} dy={10} minTickGap={20} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 10}} domain={[-60, 100]} tickFormatter={v => `${v} kW`} />
                <Tooltip content={<InverterTooltip />} cursor={{ stroke: '#334155', strokeWidth: 1, strokeDasharray: '4 4' }} />
                
                <ReferenceLine y={0} stroke="#475569" strokeOpacity={0.5} />
                
                <Area type="monotone" dataKey="power" stroke="#3b82f6" fillOpacity={1} fill="url(#colorPower)" strokeWidth={2} />
                
                <defs>
                  <linearGradient id="colorPower" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="50%" stopColor="#3b82f6" stopOpacity={0.0}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  </linearGradient>
                </defs>
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

      </div>

      {/* Bottom Grid: Degradation Chart + Text Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Degradation Chart */}
        <Card className="bg-[#0f172a] border-slate-800/50 rounded-xl flex flex-col">
          <CardHeader className="pb-2">
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-sm font-bold text-white">Graph 3: Projected Battery Degradation Curve</CardTitle>
                <p className="text-xs text-slate-400 mt-1">Capacity retention vs full equivalent cycles (LiFePO4 cell aging)</p>
              </div>
              <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-wider">6,000 Cycle Life</span>
            </div>
          </CardHeader>
          <CardContent className="flex-1 min-h-[250px] pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={degradationData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                <XAxis dataKey="cycle" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 10}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 10}} domain={[70, 100]} tickFormatter={v => `${v}%`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }}
                  itemStyle={{ color: '#10b981', fontWeight: 'bold' }}
                />
                
                <ReferenceLine y={80} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'insideBottomRight', value: '80% Warranty Floor', fill: '#ef4444', fontSize: 10 }} />
                
                <Line type="monotone" dataKey="retention" name="SOH" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Text Panel */}
        <Card className="bg-[#0f172a] border-slate-800/50 rounded-xl">
          <CardHeader className="pb-4">
            <CardTitle className="text-sm font-bold text-white flex items-center gap-2">
              <Zap size={16} className="text-emerald-500" /> Recommended Storage Strategy
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            
            <div className="p-4 bg-emerald-950/30 border border-emerald-900/50 rounded-xl">
              <h4 className="text-emerald-500 font-bold text-xs mb-1">Optimal Charging Window: 10:30 – 14:30</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Schedule full charging rate during peak irradiance to prevent curtailment and absorb 180 kWh of surplus PV power before 15:00.
              </p>
            </div>

            <div className="p-4 bg-emerald-950/30 border border-emerald-900/50 rounded-xl">
              <h4 className="text-emerald-500 font-bold text-xs mb-1">Peak Discharge Window: 18:30 – 21:30</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Discharge at up to 85 kW to bridge community lighting load without starting the diesel generator.
              </p>
            </div>

            <div className="p-4 bg-[#1e293b]/50 border border-slate-800/50 rounded-xl">
              <h4 className="text-slate-300 font-bold text-xs mb-1">Critical Emergency Reserve Floor: 20% (100 kWh)</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Preserve 100 kWh exclusively for primary healthcare clinic refrigerators and rural emergency communications.
              </p>
            </div>

          </CardContent>
        </Card>

      </div>

    </div>
  );
}
