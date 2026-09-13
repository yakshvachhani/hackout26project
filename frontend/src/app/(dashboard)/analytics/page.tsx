'use client';

import { useSettings } from '@/contexts/SettingsContext';
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, ShieldCheck, Sun, Zap } from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area
} from 'recharts';

export default function AnalyticsPage() {
  const { currency, powerScale } = useSettings();
  const [range, setRange] = useState('30d');

  const [historyData, setHistoryData] = useState<any[]>([]);

  React.useEffect(() => {
    const days = parseInt(range.replace('d', '')) || 30;
    fetch(`http://localhost:8000/api/analytics?days=${days}`)
      .then(res => res.json())
      .then(data => setHistoryData(data))
      .catch(err => console.error(err));
  }, [range]);

  // Calculate dynamic KPIs from DB
  const avgUptime = historyData.length ? (historyData.reduce((acc, curr) => acc + curr.uptime, 0) / historyData.length).toFixed(1) : "0.0";
  const avgRenewable = historyData.length ? (historyData.reduce((acc, curr) => acc + curr.renewablePenetration, 0) / historyData.length).toFixed(1) : "0.0";
  const avgDiesel = historyData.length ? (historyData.reduce((acc, curr) => acc + curr.dieselDependency, 0) / historyData.length).toFixed(1) : "0.0";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Historical Analytics</h2>
          <p className="text-outline">Performance, reliability, and uptime metrics over time.</p>
        </div>
        <div className="flex items-center bg-surface-container rounded-lg p-1 border border-outline-variant">
          {['7d', '30d', '90d'].map((r) => (
            <button 
              key={r}
              onClick={() => setRange(r)}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${range === r ? 'bg-surface text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'}`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-surface border-outline-variant rounded-xl overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-outline">System Uptime</CardTitle>
            <ShieldCheck className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-on-surface">{avgUptime}%</div>
            <p className="text-xs text-on-surface mt-1">Over 30 days</p>
          </CardContent>
        </Card>
        
        <Card className="bg-surface border-outline-variant rounded-xl overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-outline">Avg. Renewable Share</CardTitle>
            <Sun className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-on-surface">{avgRenewable}%</div>
            <p className="text-xs text-on-surface mt-1">Target &gt; 80%</p>
          </CardContent>
        </Card>

        <Card className="bg-surface border-outline-variant rounded-xl overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-outline">Avg. Diesel Dependency</CardTitle>
            <Activity className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-on-surface">{avgDiesel}%</div>
            <p className="text-xs text-on-surface mt-1">Decreased from 18% last month</p>
          </CardContent>
        </Card>

        <Card className="bg-surface border-outline-variant rounded-xl overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-outline">Unserved Energy</CardTitle>
            <Zap className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-on-surface">42 kWh</div>
            <p className="text-xs text-on-surface mt-1">0 critical load drops</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Renewable Penetration Chart */}
        <Card className="bg-surface border-outline-variant rounded-xl overflow-hidden">
          <CardHeader>
            <CardTitle>Renewable Penetration & Diesel Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={historyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" vertical={false} />
                  <XAxis dataKey="day" stroke="#94a3b8" tick={{fontSize: 10}} interval={4} />
                  <YAxis stroke="#94a3b8" tick={{fontSize: 12}} />
                  <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', color: '#0f172a' }} />
                  <Legend />
                  <Line type="monotone" dataKey="renewablePenetration" stroke="#10b981" strokeWidth={2} dot={false} name="Renewable %" />
                  <Line type="monotone" dataKey="dieselDependency" stroke="#f87171" strokeWidth={2} dot={false} name="Diesel %" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Uptime / Outage Chart */}
        <Card className="bg-surface border-outline-variant rounded-xl overflow-hidden">
          <CardHeader>
            <CardTitle>System Uptime & Outage Events</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={historyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" vertical={false} />
                  <XAxis dataKey="day" stroke="#94a3b8" tick={{fontSize: 10}} interval={4} />
                  <YAxis stroke="#94a3b8" domain={[90, 100]} tick={{fontSize: 12}} />
                  <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', color: '#0f172a' }} />
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

