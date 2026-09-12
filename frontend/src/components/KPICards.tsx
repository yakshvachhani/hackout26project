import { useMemo } from 'react';
import { Leaf, DollarSign, Clock } from 'lucide-react';
import { DispatchRecord } from '../types';

interface KPICardsProps {
  dispatchData: DispatchRecord[];
}

export default function KPICards({ dispatchData }: KPICardsProps) {
  const kpis = useMemo(() => {
    if (!dispatchData.length) return { dieselHoursAvoided: 0, costSaved: 0, co2Reduced: 0 };

    let dieselHoursAvoided = 0;
    let renewableKwhUsed = 0;

    dispatchData.forEach(d => {
      // If there was load to meet, but we didn't use diesel, that's an hour avoided
      const totalDemandMet = d.solar_used_kw + d.wind_used_kw + Math.max(0, d.battery_kw) + d.diesel_kw;
      if (totalDemandMet > 0 && d.diesel_kw === 0) {
        dieselHoursAvoided++;
      }
      
      // Calculate renewable energy directly consumed or dispatched from battery
      // (Simplified: assuming battery discharge comes from stored renewables)
      renewableKwhUsed += d.solar_used_kw + d.wind_used_kw + Math.max(0, d.battery_kw);
    });

    // Simple baseline assumptions for the demo
    const CO2_PER_KWH_DIESEL = 0.8; // kg
    const COST_PER_KWH_DIESEL = 0.35; // $

    return {
      dieselHoursAvoided,
      costSaved: renewableKwhUsed * COST_PER_KWH_DIESEL,
      co2Reduced: renewableKwhUsed * CO2_PER_KWH_DIESEL,
    };
  }, [dispatchData]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10">
          <Clock className="w-16 h-16 text-slate-100" />
        </div>
        <h3 className="text-slate-400 text-sm font-medium mb-1">Diesel Hours Avoided</h3>
        <div className="text-3xl font-bold text-slate-100">{kpis.dieselHoursAvoided} <span className="text-lg font-normal text-slate-500">hrs</span></div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10">
          <DollarSign className="w-16 h-16 text-slate-100" />
        </div>
        <h3 className="text-slate-400 text-sm font-medium mb-1">Est. Cost Saved</h3>
        <div className="text-3xl font-bold text-battery">${kpis.costSaved.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10">
          <Leaf className="w-16 h-16 text-slate-100" />
        </div>
        <h3 className="text-slate-400 text-sm font-medium mb-1">CO₂ Reduced</h3>
        <div className="text-3xl font-bold text-wind">{kpis.co2Reduced.toLocaleString(undefined, { maximumFractionDigits: 0 })} <span className="text-lg font-normal text-slate-500">kg</span></div>
      </div>
    </div>
  );
}
