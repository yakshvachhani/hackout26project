import { useState } from 'react';
import { simulateDispatch, fetchForecast } from '../api/client';
import { ForecastRecord, DispatchRecord, SimulationRequest } from '../types';
import ForecastChart from './charts/ForecastChart';
import DispatchChart from './charts/DispatchChart';
import ExplainabilityPanel from './ExplainabilityPanel';
import { Play, Settings2, Loader2, Info } from 'lucide-react';
import KPICards from './KPICards';

export default function Simulator() {
  const [params, setParams] = useState<SimulationRequest>({
    solar_capacity_kw: 100,
    wind_capacity_kw: 100,
    battery_capacity_kwh: 200,
    diesel_capacity_kw: 50,
    demand_multiplier: 1.0,
    weather_scenario: 'normal'
  });

  const [forecast, setForecast] = useState<ForecastRecord[] | null>(null);
  const [dispatch, setDispatch] = useState<DispatchRecord[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<DispatchRecord | null>(null);

  const handleSimulate = async () => {
    try {
      setLoading(true);
      setError(null);
      // We also need to fetch the mock forecast generated for this scenario to show the before/after charts properly
      // We pass the same params to a hypothetical /forecast endpoint that accepts them, 
      // but our backend /simulate generates the forecast internally.
      // For the demo, we'll just run the simulation which returns dispatch, 
      // and we will rely on a new /forecast endpoint with params, OR we can just show the dispatch.
      // Wait, the backend /forecast doesn't take scenario params. It does! 
      // Oh wait, in main.py `get_forecast` only takes `hours`. 
      // To get the updated forecast, we might just look at the dispatch record's utilized values, 
      // but that's not the full forecast. We will just show the dispatch chart for the simulation.
      
      const dData = await simulateDispatch(params);
      setDispatch(dData);
    } catch (err) {
      setError("Simulation failed. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto pb-12 flex flex-col lg:flex-row gap-8">
      {/* Controls Sidebar */}
      <div className="w-full lg:w-80 flex flex-col gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-6 border-b border-slate-800 pb-4">
            <Settings2 className="w-5 h-5 text-slate-300" />
            <h2 className="text-lg font-bold text-slate-100">Parameters</h2>
          </div>

          <div className="space-y-6">
            <div>
              <label className="flex justify-between text-sm font-medium text-slate-300 mb-2">
                Solar Capacity
                <span className="text-solar">{params.solar_capacity_kw} kW</span>
              </label>
              <input 
                type="range" min="0" max="500" step="10" 
                value={params.solar_capacity_kw}
                onChange={e => setParams({...params, solar_capacity_kw: Number(e.target.value)})}
                className="w-full accent-solar"
              />
            </div>

            <div>
              <label className="flex justify-between text-sm font-medium text-slate-300 mb-2">
                Wind Capacity
                <span className="text-wind">{params.wind_capacity_kw} kW</span>
              </label>
              <input 
                type="range" min="0" max="500" step="10" 
                value={params.wind_capacity_kw}
                onChange={e => setParams({...params, wind_capacity_kw: Number(e.target.value)})}
                className="w-full accent-wind"
              />
            </div>

            <div>
              <label className="flex justify-between text-sm font-medium text-slate-300 mb-2">
                Battery Storage
                <span className="text-battery">{params.battery_capacity_kwh} kWh</span>
              </label>
              <input 
                type="range" min="0" max="1000" step="50" 
                value={params.battery_capacity_kwh}
                onChange={e => setParams({...params, battery_capacity_kwh: Number(e.target.value)})}
                className="w-full accent-battery"
              />
            </div>
            
            <div>
              <label className="flex justify-between text-sm font-medium text-slate-300 mb-2">
                Demand Multiplier
                <span className="text-slate-200">{params.demand_multiplier}x</span>
              </label>
              <input 
                type="range" min="0.5" max="3.0" step="0.1" 
                value={params.demand_multiplier}
                onChange={e => setParams({...params, demand_multiplier: Number(e.target.value)})}
                className="w-full accent-slate-400"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Weather Scenario
              </label>
              <select 
                value={params.weather_scenario}
                onChange={e => setParams({...params, weather_scenario: e.target.value})}
                className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-lg p-2.5 text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              >
                <option value="normal">Normal Day</option>
                <option value="cloudy">Cloudy (Low Solar)</option>
                <option value="storm">Storm (No Solar, High Wind)</option>
              </select>
            </div>

            <button 
              onClick={handleSimulate}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-4 shadow-lg shadow-blue-900/20"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
              {loading ? 'Simulating...' : 'Run Simulation'}
            </button>
          </div>
        </div>
      </div>

      {/* Results Area */}
      <div className="flex-1">
        {!dispatch && !loading && (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-xl p-12 text-center">
            <Settings2 className="w-16 h-16 mb-4 opacity-20" />
            <h3 className="text-xl font-medium text-slate-300 mb-2">Digital Twin Simulator</h3>
            <p className="max-w-md">Adjust the parameters on the left and run a simulation to see how the AI dispatch adapts to different grid configurations and weather events.</p>
          </div>
        )}

        {error && (
          <div className="bg-red-900/20 border border-red-900/50 p-4 rounded-xl text-red-400 mb-6">
            {error}
          </div>
        )}

        {dispatch && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center gap-2 bg-blue-900/20 border border-blue-900/50 p-4 rounded-xl text-blue-200 mb-2">
              <Info className="w-5 h-5 flex-shrink-0" />
              <p className="text-sm">Showing simulated 48-hour dispatch based on your parameters. Watch how the AI adapts its battery usage and diesel fallback.</p>
            </div>
            
            <KPICards dispatchData={dispatch} />
            <DispatchChart data={dispatch} onBarClick={setSelectedRecord} />
          </div>
        )}
      </div>

      <ExplainabilityPanel 
        isOpen={!!selectedRecord} 
        onClose={() => setSelectedRecord(null)} 
        record={selectedRecord} 
      />
    </div>
  );
}
