import { useMemo } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine
} from 'recharts';
import { DispatchRecord } from '../../types';

interface DispatchChartProps {
  data: DispatchRecord[];
  onBarClick?: (record: DispatchRecord) => void;
}

export default function DispatchChart({ data, onBarClick }: DispatchChartProps) {
  const formattedData = useMemo(() => {
    return data.map(d => ({
      ...d,
      time: new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      // For charting, we want to split battery into charging (negative) and discharging (positive)
      battery_discharge: d.battery_kw > 0 ? d.battery_kw : 0,
      battery_charge: d.battery_kw < 0 ? d.battery_kw : 0,
    }));
  }, [data]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-lg font-bold text-slate-100">AI Dispatch Schedule</h2>
        <p className="text-sm text-slate-400">Optimized source mix (Click a bar for AI reasoning)</p>
      </div>
      
      <div className="flex-1 w-full min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={formattedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} minTickGap={30} />
            <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip 
              cursor={{ fill: '#334155', opacity: 0.4 }}
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }}
            />
            <Legend wrapperStyle={{ paddingTop: '10px' }} />
            <ReferenceLine y={0} stroke="#475569" />
            
            <Bar dataKey="solar_used_kw" name="Solar" stackId="a" fill="#fbbf24" onClick={(data) => onBarClick?.(data.payload)} cursor="pointer" />
            <Bar dataKey="wind_used_kw" name="Wind" stackId="a" fill="#22d3ee" onClick={(data) => onBarClick?.(data.payload)} cursor="pointer" />
            <Bar dataKey="battery_discharge" name="Battery (Discharge)" stackId="a" fill="#4ade80" onClick={(data) => onBarClick?.(data.payload)} cursor="pointer" />
            <Bar dataKey="diesel_kw" name="Diesel" stackId="a" fill="#f87171" onClick={(data) => onBarClick?.(data.payload)} cursor="pointer" />
            <Bar dataKey="unmet_demand_kw" name="Unmet Demand" stackId="a" fill="#7f1d1d" onClick={(data) => onBarClick?.(data.payload)} cursor="pointer" />
            
            <Bar dataKey="battery_charge" name="Battery (Charge)" stackId="a" fill="#22c55e" fillOpacity={0.6} onClick={(data) => onBarClick?.(data.payload)} cursor="pointer" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
