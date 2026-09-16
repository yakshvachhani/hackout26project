'use client';

import React, { useState, useEffect } from 'react';
import { useSettings } from '@/contexts/SettingsContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CircleDollarSign, CloudRain, Droplet, Battery, TrendingDown, Leaf } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, LineChart, Line, AreaChart, Area, Cell } from
'recharts';

export default function CostPage() {
  const { currency, powerScale } = useSettings();
  const [weeklyData, setWeeklyData] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/cost').
    then((res) => res.json()).
    then((data) => setWeeklyData(data)).
    catch((err) => console.error(err));
  }, []);

  // Dynamic KPIs
  const todaysCost = weeklyData.length ? weeklyData[weeklyData.length - 1].optimizedCost : 0;
  const todaysBaseline = weeklyData.length ? weeklyData[weeklyData.length - 1].dieselOnlyCost : 0;
  const savingsPercent = todaysBaseline ? Math.round((todaysBaseline - todaysCost) / todaysBaseline * 100) : 0;
  const totalCO2 = weeklyData.reduce((acc, curr) => acc + curr.savedCO2, 0).toFixed(0);
  const totalSavings = weeklyData.reduce((acc, curr) => acc + (curr.dieselOnlyCost - curr.optimizedCost), 0).toFixed(0);

  const costBreakdown = [
  { name: 'Diesel Fuel', cost: 1840, fill: '#f87171' },
  { name: 'Battery Degradation', cost: 650, fill: '#818cf8' },
  { name: 'O&M Renewables', cost: 350, fill: '#10b981' },
  { name: 'Carbon Penalty', cost: 400, fill: '#94a3b8' }];


  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Cost & Emissions</h2>
        <p className="text-outline">Financial overview, carbon tracking, and baseline comparisons.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-surface border-outline-variant">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-outline">Today's Operating Cost</CardTitle>
            <CircleDollarSign className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-on-surface">{currency}{todaysCost.toLocaleString()}</div>
            <p className="text-xs text-emerald-500 flex items-center mt-1">
              <TrendingDown size={14} className="mr-1" /> {savingsPercent}% vs Diesel Baseline
            </p>
          </CardContent>
        </Card>
        
        <Card className="bg-surface border-outline-variant">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-outline">7-Day Emissions Avoided</CardTitle>
            <CloudRain className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-on-surface">{totalCO2} kg CO₂</div>
            <p className="text-xs text-on-surface mt-1">Total over last 7 days</p>
          </CardContent>
        </Card>

        <Card className="bg-surface border-outline-variant">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-outline">Diesel Consumption</CardTitle>
            <Droplet className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-on-surface">52 L</div>
            <p className="text-xs text-emerald-500 flex items-center mt-1">
              <TrendingDown size={14} className="mr-1" /> -39 L vs Yesterday
            </p>
          </CardContent>
        </Card>

        <Card className="bg-surface border-outline-variant">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-outline">7-Day Savings</CardTitle>
            <Leaf className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-on-surface">{currency}{Number(totalSavings).toLocaleString()}</div>
            <p className="text-xs text-on-surface mt-1">Cumulative cost reduction</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Cost Comparison Chart */}
        <Card className="bg-surface border-outline-variant">
          <CardHeader>
            <CardTitle>Optimized vs Diesel-Only Baseline Cost ({currency})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={weeklyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" vertical={false} />
                  <XAxis dataKey="day" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" tickFormatter={(val) => `${currency}${val}`} />
                  <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', color: '#0f172a' }} formatter={(val) => `${currency}${val}`} />
                  <Legend />
                  <Bar dataKey="dieselOnlyCost" fill="#cbd5e1" name="Diesel-Only Baseline" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="optimizedCost" fill="#10b981" name="Optimized Microgrid" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* CO2 Emissions Chart */}
        <Card className="bg-surface border-outline-variant">
          <CardHeader>
            <CardTitle>CO₂ Emissions Avoided (kg)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={weeklyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorCO2" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" vertical={false} />
                  <XAxis dataKey="day" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', color: '#0f172a' }} />
                  <Legend />
                  <Area type="monotone" dataKey="savedCO2" stroke="#3b82f6" fill="url(#colorCO2)" name="Avoided CO₂" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Cost Breakdown */}
        <Card className="bg-surface border-outline-variant">
          <CardHeader>
            <CardTitle>Today's Cost Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={costBreakdown} layout="vertical" margin={{ top: 10, right: 30, left: 40, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" horizontal={false} />
                  <XAxis type="number" stroke="#94a3b8" tickFormatter={(val) => `${currency}${val}`} />
                  <YAxis dataKey="name" type="category" stroke="#94a3b8" width={100} />
                  <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', color: '#0f172a' }} cursor={{ fill: '#e2e8f0' }} formatter={(val) => `${currency}${val}`} />
                  <Bar dataKey="cost" radius={[0, 4, 4, 0]}>
                    {
                    costBreakdown.map((entry, index) =>
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                    )
                    }
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

      </div>
    </div>);

}