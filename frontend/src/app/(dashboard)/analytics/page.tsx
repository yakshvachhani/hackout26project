'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, ShieldCheck, Sun, Zap } from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area
} from 'recharts';

export default function AnalyticsPage() {
  const [range, setRange] = useState('30d');

  const [historyData, setHistoryData] = useState<any[]>([]);

  React.useEffect(() => {
    fetch('http://localhost:8000/api/analytics')
      .then(res => res.json())
      .then(data => setHistoryData(data))
      .catch(err => console.error(err));
  }, []);

  // Calculate dynamic KPIs from DB
  const avgUptime = historyData.length ? (historyData.reduce((acc, curr) => acc + curr.uptime, 0) / historyData.length).toFixed(1) : "0.0";
  const avgRenewable = historyData.length ? (historyData.reduce((acc, curr) => acc + curr.renewablePenetration, 0) / historyData.length).toFixed(1) : "0.0";
  const avgDiesel = historyData.length ? (historyData.reduce((acc, curr) => acc + curr.dieselDependency, 0) / historyData.length).toFixed(1) : "0.0";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Historical Analytics</h2>
          <p className="text-slate-400">Performance, reliability, and uptime metrics over time.</p>
        </div>
        <div className="flex bg-slate-800 rounded-md p-1">
          {['7d', '30d', '90d'].map((r) => (
            <button 
              key={r}
              onClick={() => setRange(r)}
              className={`px-3 py-1 text-sm font-medium rounded ${range === r ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-slate-200'}`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-400">System Uptime</CardTitle>
            <ShieldCheck className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-50">{avgUptime}%</div>
            <p className="text-xs text-slate-500 mt-1">Over 30 days</p>
          </CardContent>
        </Card>
        
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-400">Avg. Renewable Share</CardTitle>
            <Sun className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-50">{avgRenewable}%</div>
            <p className="text-xs text-slate-500 mt-1">Target &gt; 80%</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-400">Avg. Diesel Dependency</CardTitle>
            <Activity className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-50">{avgDiesel}%</div>
            <p className="text-xs text-slate-500 mt-1">Decreased from 18% last month</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-400">Unserved Energy</CardTitle>
            <Zap className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-50">42 kWh</div>
            <p className="text-xs text-slate-500 mt-1">0 critical load drops</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Renewable Penetration Chart */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle>Renewable Penetration & Diesel Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={historyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="day" stroke="#94a3b8" tick={{fontSize: 10}} interval={4} />
                  <YAxis stroke="#94a3b8" tick={{fontSize: 12}} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }} />
                  <Legend />
                  <Line type="monotone" dataKey="renewablePenetration" stroke="#10b981" strokeWidth={2} dot={false} name="Renewable %" />
                  <Line type="monotone" dataKey="dieselDependency" stroke="#f87171" strokeWidth={2} dot={false} name="Diesel %" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Uptime / Outage Chart */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle>System Uptime & Outage Events</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={historyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="day" stroke="#94a3b8" tick={{fontSize: 10}} interval={4} />
                  <YAxis stroke="#94a3b8" domain={[90, 100]} tick={{fontSize: 12}} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }} />
                  <Legend />
                  <Area type="monotone" dataKey="uptime" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} name="Uptime %" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}
