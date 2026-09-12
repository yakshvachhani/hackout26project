import { DispatchRecord } from '../types';
import { X, Zap, Info, Battery, Wind, Sun, Fuel } from 'lucide-react';
import { cn } from '../lib/utils';

interface ExplainabilityPanelProps {
  isOpen: boolean;
  onClose: () => void;
  record: DispatchRecord | null;
}

export default function ExplainabilityPanel({ isOpen, onClose, record }: ExplainabilityPanelProps) {
  if (!record) return null;

  const time = new Date(record.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div 
      className={cn(
        "fixed inset-y-0 right-0 w-96 bg-slate-900 border-l border-slate-700 shadow-2xl transform transition-transform duration-300 ease-in-out z-50 flex flex-col",
        isOpen ? "translate-x-0" : "translate-x-full"
      )}
    >
      <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber-400" />
          Decision Log
        </h2>
        <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="p-6 flex-1 overflow-y-auto">
        <div className="mb-6">
          <div className="text-sm text-slate-400 mb-1">Time Period</div>
          <div className="text-lg font-medium">{time}</div>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-5 mb-6 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-slate-200 mb-2">AI Reasoning</h3>
              <p className="text-sm text-slate-300 leading-relaxed">
                {record.decision_reason}
              </p>
            </div>
          </div>
        </div>

        <h3 className="font-semibold text-slate-300 mb-4 uppercase tracking-wider text-xs">Dispatch Mix Breakdown</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30 border border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-solar/10 rounded-md text-solar"><Sun className="w-4 h-4" /></div>
              <span className="font-medium text-slate-300">Solar Used</span>
            </div>
            <span className="font-bold">{record.solar_used_kw.toFixed(1)} kW</span>
          </div>
          
          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30 border border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-wind/10 rounded-md text-wind"><Wind className="w-4 h-4" /></div>
              <span className="font-medium text-slate-300">Wind Used</span>
            </div>
            <span className="font-bold">{record.wind_used_kw.toFixed(1)} kW</span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30 border border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-battery/10 rounded-md text-battery"><Battery className="w-4 h-4" /></div>
              <span className="font-medium text-slate-300">Battery Action</span>
            </div>
            <div className="text-right">
              <div className={cn("font-bold", record.battery_kw > 0 ? "text-battery" : record.battery_kw < 0 ? "text-blue-400" : "")}>
                {record.battery_kw > 0 ? `Discharged ${record.battery_kw.toFixed(1)} kW` : 
                 record.battery_kw < 0 ? `Charged ${Math.abs(record.battery_kw).toFixed(1)} kW` : 
                 'Idle (0 kW)'}
              </div>
              <div className="text-xs text-slate-500 mt-1">SOC: {record.battery_soc_percent.toFixed(1)}%</div>
            </div>
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30 border border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-diesel/10 rounded-md text-diesel"><Fuel className="w-4 h-4" /></div>
              <span className="font-medium text-slate-300">Diesel Gen</span>
            </div>
            <span className={cn("font-bold", record.diesel_kw > 0 ? "text-diesel" : "text-slate-500")}>
              {record.diesel_kw.toFixed(1)} kW
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
