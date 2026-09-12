import { useMemo } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { ForecastRecord } from '../../types';

interface ForecastChartProps {
  data: ForecastRecord[];
}

export default function ForecastChart({ data }: ForecastChartProps) {
  const formattedData = useMemo(() => {
    return data.map(d => ({
      ...d,
      time: new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }));
  }, [data]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-lg font-bold text-slate-100">Generation Forecast & Demand</h2>
          <p className="text-sm text-slate-400">48-hour outlook based on weather models</p>
        </div>
      </div>
      
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={formattedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorSolar" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#fbbf24" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#fbbf24" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorWind" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#22d3ee" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} minTickGap={30} />
            <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }}
              itemStyle={{ color: '#f1f5f9' }}
            />
            <Legend wrapperStyle={{ paddingTop: '10px' }} />
            
            <Area 
              type="monotone" 
              dataKey="demand_kw" 
              name="Demand (kW)"
              stroke="#cbd5e1" 
              fill="transparent" 
              strokeWidth={2}
              strokeDasharray="5 5"
            />
            <Area 
              type="monotone" 
              dataKey="wind_kw" 
              name="Wind (kW)"
              stroke="#06b6d4" 
              fillOpacity={1} 
              fill="url(#colorWind)" 
              stackId="1"
            />
            <Area 
              type="monotone" 
              dataKey="solar_kw" 
              name="Solar (kW)"
              stroke="#d97706" 
              fillOpacity={1} 
              fill="url(#colorSolar)" 
              stackId="1"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
