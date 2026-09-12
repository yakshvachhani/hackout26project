'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  LineChart, Line, ComposedChart, Bar, Legend
} from 'recharts';

export default function DispatchPage() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/dispatch')
      .then(res => res.json())
      .then(d => setData(d))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Live Dispatch</h2>
        <p className="text-slate-400">Detailed view of power mix and load balancing over time.</p>
      </div>

      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle>Real-Time Power Mix (kW)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorSolar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#facc15" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#facc15" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="time" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Legend />
                <Area type="monotone" dataKey="solar" stackId="1" stroke="#facc15" fill="url(#colorSolar)" name="Solar" />
                <Area type="monotone" dataKey="wind" stackId="1" stroke="#60a5fa" fill="#60a5fa" name="Wind" />
                <Area type="monotone" dataKey="batteryDischarge" stackId="1" stroke="#818cf8" fill="#818cf8" name="Battery (Discharging)" />
                <Area type="monotone" dataKey="diesel" stackId="1" stroke="#f87171" fill="#f87171" name="Diesel Backup" />
                
                {/* Charging goes below 0 */}
                <Area type="monotone" dataKey="batteryCharge" stackId="2" stroke="#4f46e5" fill="#4f46e5" name="Battery (Charging)" />
                
                {/* Demand Line overlay */}
                <Line type="stepAfter" dataKey="demand" stroke="#10b981" strokeWidth={3} dot={false} name="Total Demand" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle>Load vs Generation Deficit</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="time" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <RechartsTooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
                  <Legend />
                  <Bar dataKey="demand" fill="#334155" name="Load Demand" />
                  <Line type="monotone" dataKey="solar" stroke="#facc15" strokeWidth={2} name="Renewable Gen" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle>Dispatch Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
               {data.filter((_, i) => i % 4 === 0).map((row, i) => (
                 <div key={i} className="flex items-center gap-4 border-b border-slate-800 pb-2 last:border-0">
                   <div className="text-sm font-mono text-slate-400 w-16">{row.time}</div>
                   <div className="flex-1 flex gap-2">
                     {row.solar > 0 && <span className="px-2 py-1 bg-yellow-500/20 text-yellow-500 text-xs rounded border border-yellow-500/30">Solar</span>}
                     {row.wind > 0 && <span className="px-2 py-1 bg-blue-500/20 text-blue-500 text-xs rounded border border-blue-500/30">Wind</span>}
                     {row.batteryDischarge > 0 && <span className="px-2 py-1 bg-indigo-500/20 text-indigo-500 text-xs rounded border border-indigo-500/30">Battery</span>}
                     {row.diesel > 0 && <span className="px-2 py-1 bg-red-500/20 text-red-500 text-xs rounded border border-red-500/30">Diesel</span>}
                   </div>
                   <div className="text-sm text-emerald-400 font-mono">{row.demand} kW</div>
                 </div>
               ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
