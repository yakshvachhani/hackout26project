'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { AlertTriangle, Home, HeartPulse, Droplet, Store, GraduationCap, Lightbulb, SlidersHorizontal } from 'lucide-react';

export default function DemandPage() {
  // State for interactive circuit configuration
  const [counts, setCounts] = useState({
    homes: 120,
    clinic: 1,
    pumps: 4,
    shops: 18,
    schools: 5,
    lighting: 88
  });
  
  const [spikeActive, setSpikeActive] = useState(false);

  // Peak Load Multipliers (kW per unit)
  const multipliers = {
    homes: 0.45,
    clinic: 12.0,
    pumps: 7.5,
    shops: 1.77,
    schools: 6.6,
    lighting: 0.15
  };

  // Calculated Peaks
  const peaks = {
    homes: Math.round(counts.homes * multipliers.homes),
    clinic: Math.round(counts.clinic * multipliers.clinic),
    pumps: Math.round(counts.pumps * multipliers.pumps),
    shops: Math.round(counts.shops * multipliers.shops),
    schools: Math.round(counts.schools * multipliers.schools),
    lighting: Math.round(counts.lighting * multipliers.lighting),
  };

  const totalPeakLoad = Object.values(peaks).reduce((a, b) => a + b, 0);

  // Generate 24h Demand Curve
  const data = [];
  for (let i = 0; i < 24; i++) {
    const time = `${i.toString().padStart(2, '0')}:00`;
    
    // Usage factors based on time of day
    let hFactor = (i > 5 && i < 9) ? 0.7 : (i > 17 && i < 23) ? 1.0 : 0.3;
    let cFactor = 1.0; // Clinic always on
    let pFactor = (i > 6 && i < 16) ? 0.8 : 0.1;
    let sFactor = (i > 8 && i < 20) ? 0.9 : 0.1;
    let scFactor = (i > 7 && i < 15) ? 1.0 : 0.05;
    let lFactor = (i < 6 || i > 18) ? 1.0 : 0.0;

    // Apply simulation spike at 18:00
    if (spikeActive && i === 18) {
      hFactor = 1.8;
      sFactor = 1.5;
    }

    const critical = peaks.clinic * cFactor;
    const total = critical + 
      (peaks.homes * hFactor) + 
      (peaks.pumps * pFactor) + 
      (peaks.shops * sFactor) + 
      (peaks.schools * scFactor) + 
      (peaks.lighting * lFactor);

    data.push({
      time,
      critical: Math.round(critical),
      total: Math.round(total)
    });
  }

  // Pie Chart Data
  const pieData = [
    { name: 'Residential', count: `${counts.homes} Homes`, value: peaks.homes, color: '#a855f7' },
    { name: 'Agricultural Pumps', count: `${counts.pumps}x`, value: peaks.pumps, color: '#3b82f6' },
    { name: 'Primary Clinic', count: 'Critical', value: peaks.clinic, color: '#ef4444' },
    { name: 'Commercial Shops', count: `${counts.shops}x`, value: peaks.shops, color: '#eab308' },
    { name: 'Schools', count: `${counts.schools}x`, value: peaks.schools, color: '#10b981' },
    { name: 'Lighting', count: `${counts.lighting}x`, value: peaks.lighting, color: '#94a3b8' },
  ].filter(d => d.value > 0);

  const handleSlider = (key: keyof typeof counts, value: string) => {
    setCounts(prev => ({ ...prev, [key]: parseInt(value) || 0 }));
  };

  const triggerSpike = () => {
    setSpikeActive(true);
    setTimeout(() => setSpikeActive(false), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold tracking-tight text-white">Community Electricity Demand & Profiler</h2>
            <span className="px-2 py-1 bg-indigo-500/20 text-indigo-400 text-[10px] font-bold rounded uppercase tracking-wider border border-indigo-500/30">
              Bottom-Up Consumption Model
            </span>
          </div>
          <p className="text-slate-400 mt-1 text-sm">Configurable community circuits, critical healthcare load isolation, and demand surge stress testing</p>
        </div>
        <button 
          onClick={triggerSpike}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all text-sm
            ${spikeActive ? 'bg-red-500 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700'}`}
        >
          <AlertTriangle size={16} />
          Simulate 18:00 Demand Spike
        </button>
      </div>

      {/* Configuration Panel */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader className="pb-2 border-b border-slate-800">
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center gap-2 text-base text-slate-200">
              <SlidersHorizontal size={16} className="text-purple-400"/> Community Circuit Configuration
            </CardTitle>
            <div className="text-sm">
              <span className="text-slate-400">Total Peak Load: </span>
              <span className="font-bold text-white text-lg">{totalPeakLoad} kW</span>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            
            {/* Homes */}
            <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-2 text-purple-400 text-sm font-medium">
                  <Home size={14}/> Homes
                </div>
                <span className="font-bold text-white text-sm">{counts.homes}</span>
              </div>
              <input type="range" min="0" max="300" value={counts.homes} onChange={(e) => handleSlider('homes', e.target.value)} 
                className="w-full h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer" style={{ accentColor: '#a855f7' }}/>
              <div className="mt-3 text-[11px] text-slate-500">{peaks.homes} kW peak</div>
            </div>

            {/* Clinic */}
            <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-2 text-red-400 text-sm font-medium">
                  <HeartPulse size={14}/> Clinic
                </div>
                <span className="font-bold text-white text-sm">{counts.clinic}</span>
              </div>
              <input type="range" min="0" max="5" value={counts.clinic} onChange={(e) => handleSlider('clinic', e.target.value)} 
                className="w-full h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer" style={{ accentColor: '#ef4444' }}/>
              <div className="mt-3 text-[11px] text-red-500/80 font-bold">{peaks.clinic} kW (CRITICAL)</div>
            </div>

            {/* Pumps */}
            <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-2 text-blue-400 text-sm font-medium">
                  <Droplet size={14}/> Pumps
                </div>
                <span className="font-bold text-white text-sm">{counts.pumps}</span>
              </div>
              <input type="range" min="0" max="20" value={counts.pumps} onChange={(e) => handleSlider('pumps', e.target.value)} 
                className="w-full h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer" style={{ accentColor: '#3b82f6' }}/>
              <div className="mt-3 text-[11px] text-blue-400/80">{peaks.pumps} kW (Flexible)</div>
            </div>

            {/* Shops */}
            <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-2 text-yellow-400 text-sm font-medium">
                  <Store size={14}/> Shops
                </div>
                <span className="font-bold text-white text-sm">{counts.shops}</span>
              </div>
              <input type="range" min="0" max="50" value={counts.shops} onChange={(e) => handleSlider('shops', e.target.value)} 
                className="w-full h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer" style={{ accentColor: '#eab308' }}/>
              <div className="mt-3 text-[11px] text-slate-500">{peaks.shops} kW</div>
            </div>

            {/* Schools */}
            <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-2 text-emerald-400 text-sm font-medium">
                  <GraduationCap size={14}/> Schools
                </div>
                <span className="font-bold text-white text-sm">{counts.schools}</span>
              </div>
              <input type="range" min="0" max="10" value={counts.schools} onChange={(e) => handleSlider('schools', e.target.value)} 
                className="w-full h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer" style={{ accentColor: '#10b981' }}/>
              <div className="mt-3 text-[11px] text-slate-500">{peaks.schools} kW</div>
            </div>

            {/* Lighting */}
            <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-2 text-slate-300 text-sm font-medium">
                  <Lightbulb size={14}/> Lighting
                </div>
                <span className="font-bold text-white text-sm">{counts.lighting}</span>
              </div>
              <input type="range" min="0" max="200" value={counts.lighting} onChange={(e) => handleSlider('lighting', e.target.value)} 
                className="w-full h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer" style={{ accentColor: '#94a3b8' }}/>
              <div className="mt-3 text-[11px] text-slate-500">{peaks.lighting} kW</div>
            </div>

          </div>
        </CardContent>
      </Card>

      {/* Charts Section */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* Area Chart */}
        <Card className="bg-slate-900 border-slate-800 xl:col-span-2">
          <CardHeader>
            <CardTitle className="text-base text-slate-200">24-Hour Diurnal Demand Curve & Critical Base</CardTitle>
            <p className="text-xs text-slate-500 font-normal">Total community consumption vs protected critical circuits</p>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.0}/>
                    </linearGradient>
                    <linearGradient id="colorCritical" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.6}/>
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} opacity={0.5} />
                  <XAxis dataKey="time" stroke="#64748b" tick={{fontSize: 12}} tickMargin={10} />
                  <YAxis stroke="#64748b" tick={{fontSize: 12}} tickFormatter={(val) => `${val} kW`} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }}
                    itemStyle={{ color: '#f8fafc' }}
                  />
                  <Area type="monotone" dataKey="total" stroke="#8b5cf6" strokeWidth={3} fill="url(#colorTotal)" name="Total Community Load (kW)" />
                  <Area type="monotone" dataKey="critical" stroke="#ef4444" strokeWidth={2} fill="url(#colorCritical)" name="Critical Protected Load (kW)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center items-center gap-6 mt-4 text-xs">
              <div className="flex items-center gap-2 text-slate-400">
                <div className="w-3 h-3 rounded-full bg-red-500"></div> Critical Protected Load (kW)
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <div className="w-3 h-3 rounded-full bg-purple-500"></div> Total Community Load (kW)
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Pie Chart */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-base text-slate-200">Consumption by Sector</CardTitle>
            <p className="text-xs text-slate-500 font-normal">Proportionate power draw during peak hours</p>
          </CardHeader>
          <CardContent className="flex flex-col h-full">
            <div className="h-[200px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc', borderRadius: '8px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 flex-1">
              <div className="space-y-3">
                {pieData.map((item, i) => (
                  <div key={i} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }}></div>
                      <span className="text-slate-300">{item.name} <span className="text-slate-500">({item.count})</span></span>
                    </div>
                    <span className="font-bold text-white">{item.value} kW</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}
