'use client';

import { useSettings } from '@/contexts/SettingsContext';
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { Fuel, AlertTriangle, CloudRain, TrendingUp, Zap, Sparkles } from 'lucide-react';

// Scenario Database
const SCENARIOS = [
  {
    id: 1,
    title: "Diesel Fuel Shock (+30% Price)",
    riskLevel: "Low Risk",
    riskColor: "text-blue-400",
    icon: Fuel,
    themeColor: "#f59e0b",
    description: "Diesel price spikes to {currency}120/L due to supply bottlenecks in remote terrain.",
    costChange: "+28.5%",
    costChangeColor: "text-red-500",
    chartData: [
      { metric: 'Operating Cost (x10 {currency})', base: 324, scenario: 416 },
      { metric: 'Diesel Cons. (L)', base: 52, scenario: 45 },
      { metric: 'Carbon (kg)', base: 126, scenario: 118 },
    ],
    mitigation: "Accelerate scheduled water pumping into 11:00-14:00 solar hours to avert costly evening generator dispatch.",
    assessment: "Healthcare clinic (12 {powerScale}) and drinking water pump circuit are fully protected with isolated battery bus priority under this scenario."
  },
  {
    id: 2,
    title: "Generator Mechanical Failure",
    riskLevel: "Moderate Risk",
    riskColor: "text-yellow-500",
    icon: AlertTriangle,
    themeColor: "#ef4444",
    description: "Diesel genset suffers alternator trip: system must run 100% on Solar + Wind + Battery.",
    costChange: "-38.2%",
    costChangeColor: "text-emerald-500",
    chartData: [
      { metric: 'Operating Cost (x10 {currency})', base: 324, scenario: 200 },
      { metric: 'Diesel Cons. (L)', base: 52, scenario: 0 },
      { metric: 'Carbon (kg)', base: 126, scenario: 0 },
    ],
    mitigation: "Strict load shedding enacted for non-essential residential sectors between 18:00-22:00. Battery reserves strictly conserved for critical loads.",
    assessment: "WARNING: Zero backup redundancy. Any concurrent solar or battery failure will result in total system blackout."
  },
  {
    id: 3,
    title: "3-Day Monsoonal Low Solar (-60% PV)",
    riskLevel: "Moderate Risk",
    riskColor: "text-yellow-500",
    icon: CloudRain,
    themeColor: "#3b82f6",
    description: "Heavy overcast monsoon conditions reduce solar output from 220 {powerScale} to 85 {powerScale} peak.",
    costChange: "+42.0%",
    costChangeColor: "text-red-500",
    chartData: [
      { metric: 'Operating Cost (x10 {currency})', base: 324, scenario: 460 },
      { metric: 'Diesel Cons. (L)', base: 52, scenario: 115 },
      { metric: 'Carbon (kg)', base: 126, scenario: 285 },
    ],
    mitigation: "Pre-charge battery to 100% using diesel generator during off-peak night hours when generator thermal efficiency is highest.",
    assessment: "Critical loads secure. 15% probability of residential load shedding if wind speeds also drop below 4 m/s during this period."
  },
  {
    id: 4,
    title: "Community Demand Growth (+25%)",
    riskLevel: "Moderate Risk",
    riskColor: "text-yellow-500",
    icon: TrendingUp,
    themeColor: "#8b5cf6",
    description: "New agricultural cold-storage facility and 30 new household connections installed.",
    costChange: "+31.0%",
    costChangeColor: "text-red-500",
    chartData: [
      { metric: 'Operating Cost (x10 {currency})', base: 324, scenario: 424 },
      { metric: 'Diesel Cons. (L)', base: 52, scenario: 85 },
      { metric: 'Carbon (kg)', base: 126, scenario: 195 },
    ],
    mitigation: "Optimal dispatch algorithms modified to cycle agricultural pumps exclusively during peak midday solar curtailment hours.",
    assessment: "Base capacity sufficient. However, battery cycle degradation will accelerate by 14% annually under this new continuous load profile."
  },
  {
    id: 5,
    title: "Double Storage Capacity (1 MWh)",
    riskLevel: "None Risk",
    riskColor: "text-emerald-500",
    icon: Zap,
    themeColor: "#10b981",
    description: "Container expansion doubling battery storage from 500 kWh to 1,000 kWh.",
    costChange: "-24.6%",
    costChangeColor: "text-emerald-500",
    chartData: [
      { metric: 'Operating Cost (x10 {currency})', base: 324, scenario: 244 },
      { metric: 'Diesel Cons. (L)', base: 52, scenario: 15 },
      { metric: 'Carbon (kg)', base: 126, scenario: 40 },
    ],
    mitigation: "Excess midday solar previously curtailed is now perfectly captured. Generator set points adjusted to rarely fire unless SOC drops below 15%.",
    assessment: "Resilience vastly improved. System can autonomously support the entire community for 18 hours without any solar or diesel inputs."
  }
];

const CustomTooltip = ({ active, payload, label }: any) => {
  const { currency, formatCurrency, formatPower } = useSettings();
  if (active && payload && payload.length) {
    return (
      <div className="bg-surface border border-outline p-3 rounded-xl shadow-xl min-w-[200px]">
        <p className="text-on-surface-variant font-bold mb-2">{label.replace(` (x10 ${currency})`, '')}</p>
        {payload.map((entry: any, index: number) => {
          let val = entry.value;
          let unit = "";
          let prefix = "";
          if (label.includes('Cost')) {
            val = val * 10;
            prefix = currency;
          } else if (label.includes('Diesel')) {
            unit = " L";
          } else if (label.includes('Carbon')) {
            unit = " kg";
          }
          return (
            <div key={index} className="flex items-center justify-between text-sm mt-1">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }}></div>
                <span className="text-outline">{entry.name}:</span>
              </div>
              <span className="text-on-surface font-bold">{prefix}{val.toLocaleString()}{unit}</span>
            </div>
          );
        })}
      </div>
    );
  }
  return null;
};

export default function ScenariosPage() {
  const { currency, powerScale, formatCurrency, formatPower } = useSettings();
  const [activeId, setActiveId] = useState(1);
  const activeScenario = SCENARIOS.find(s => s.id === activeId) || SCENARIOS[0];

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-3">
          <h2 className="text-2xl font-bold tracking-tight text-on-surface">What-If Scenario Simulator & Stress Testing</h2>
          <span className="px-2 py-1 bg-amber-500/20 text-amber-500 text-[10px] font-bold rounded uppercase tracking-wider border border-amber-500/30">
            Monte Carlo Stress Suite
          </span>
        </div>
        <p className="text-outline text-sm">Simulate volatile fuel shocks, severe weather depressions, asset trips, and community load expansions</p>
      </div>

      {/* Scenario Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-5 gap-4">
        {SCENARIOS.map((scenario) => {
          const isActive = scenario.id === activeId;
          const Icon = scenario.icon;
          return (
            <div 
              key={scenario.id}
              onClick={() => setActiveId(scenario.id)}
              className={`p-4 rounded-xl border cursor-pointer transition-all duration-200 flex flex-col justify-between min-h-[160px]
                ${isActive ? 'bg-surface border-2 shadow-lg scale-[1.02]' : 'bg-surface/50 border-outline-variant hover:bg-surface-container/80'}`}
              style={{ borderColor: isActive ? scenario.themeColor : undefined }}
            >
              <div>
                <div className="flex justify-between items-start mb-3">
                  <div className={`p-2 rounded-xl ${isActive ? '' : 'bg-surface-container'}`} style={{ backgroundColor: isActive ? `${scenario.themeColor}33` : undefined }}>
                    <Icon size={16} className={isActive ? '' : 'text-outline'} style={{ color: isActive ? scenario.themeColor : undefined }} />
                  </div>
                  <span className={`text-xs font-bold ${scenario.riskColor}`}>{scenario.riskLevel}</span>
                </div>
                <h3 className="font-bold text-on-background text-sm mb-2">{scenario.title}</h3>
                <p className="text-xs text-outline line-clamp-3">{scenario.description.replace(/\{currency\}([\d,]+)/g, (m, num) => formatCurrency(parseFloat(num.replace(/,/g,'')))).replace(/([\d,]+)\s*\{powerScale\}/g, (m, num) => formatPower(parseFloat(num.replace(/,/g,''))))}</p>
              </div>
              <div className="mt-4 flex justify-between items-end">
                <span className="text-xs text-on-surface">Cost:</span>
                <span className={`text-xs font-bold ${scenario.costChangeColor}`}>{scenario.costChange}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts & Assessment Section */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* Bar Chart */}
        <Card className="bg-surface border-outline-variant xl:col-span-2 flex flex-col">
          <CardHeader className="flex flex-row items-start justify-between pb-2 border-b border-outline-variant">
            <div>
              <CardTitle className="text-base text-on-surface">Baseline vs. {activeScenario.title}</CardTitle>
              <p className="text-xs text-on-surface font-normal mt-1">Side-by-side financial, fuel, and ecological variance</p>
            </div>
            <div className="text-sm font-bold">
              <span className="text-outline font-normal">Risk: </span>
              <span className={activeScenario.riskColor}>{activeScenario.riskLevel.split(' ')[0]}</span>
            </div>
          </CardHeader>
          <CardContent className="pt-6 flex-1 min-h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={activeScenario.chartData} margin={{ top: 20, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" vertical={false} opacity={0.4} />
                <XAxis dataKey="metric" stroke="#94a3b8" tick={{fontSize: 12}} tickMargin={10} axisLine={false} tickLine={false} />
                <YAxis stroke="#94a3b8" tick={{fontSize: 12}} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} cursor={{fill: '#e2e8f0', opacity: 0.4}} />
                <Legend iconType="square" wrapperStyle={{ paddingTop: '20px' }} />
                <Bar dataKey="base" name="Base Case" fill="#64748b" radius={[4, 4, 0, 0]} maxBarSize={60} />
                <Bar dataKey="scenario" name={activeScenario.title} fill={activeScenario.themeColor} radius={[4, 4, 0, 0]} maxBarSize={60} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Text Panel */}
        <Card className="bg-surface border-outline-variant flex flex-col">
          <CardHeader className="border-b border-outline-variant pb-4">
            <CardTitle className="text-base text-on-surface flex items-center gap-2">
              <Sparkles size={18} className="text-amber-400" /> Strategic Optimization Response
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6 flex-1 flex flex-col justify-between">
            <div className="space-y-6">
              
              <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl">
                <h4 className="text-amber-500 font-bold text-sm mb-2">Active Mitigation Protocol:</h4>
                <p className="text-sm text-on-surface-variant leading-relaxed">
                  {activeScenario.mitigation}
                </p>
              </div>

              <div>
                <h4 className="text-on-surface font-bold text-sm mb-2">Critical Load Security Assessment:</h4>
                <p className="text-sm text-outline leading-relaxed">
                  {activeScenario.assessment.replace(/\{currency\}([\d,]+)/g, (m, num) => formatCurrency(parseFloat(num.replace(/,/g,'')))).replace(/([\d,]+)\s*\{powerScale\}/g, (m, num) => formatPower(parseFloat(num.replace(/,/g,''))))}
                </p>
              </div>

            </div>

            <div className="mt-8 pt-4 border-t border-outline-variant flex justify-between items-center text-xs">
              <span className="text-on-surface">Simulation engine: Mixed-Integer Heuristic</span>
              <span className="text-emerald-500 font-bold">Stable Solution</span>
            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}

