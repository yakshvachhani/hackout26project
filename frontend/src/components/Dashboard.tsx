import { useState, useEffect } from 'react';
import { fetchForecast, fetchOptimize } from '../api/client';
import { ForecastRecord, DispatchRecord } from '../types';
import KPICards from './KPICards';
import ForecastChart from './charts/ForecastChart';
import DispatchChart from './charts/DispatchChart';
import ExplainabilityPanel from './ExplainabilityPanel';
import { AlertCircle, RefreshCw, Loader2 } from 'lucide-react';

export default function Dashboard() {
  const [forecast, setForecast] = useState<ForecastRecord[]>([]);
  const [dispatch, setDispatch] = useState<DispatchRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<DispatchRecord | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [fData, dData] = await Promise.all([
        fetchForecast(48),
        fetchOptimize(48)
      ]);
      setForecast(fData);
      setDispatch(dData);
    } catch (err) {
      setError("Failed to connect to the Dispatch API. Ensure the backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="h-full w-full flex flex-col items-center justify-center text-slate-400 space-y-4">
        <Loader2 className="w-10 h-10 animate-spin text-solar" />
        <p>Running AI Optimization Models...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full w-full flex flex-col items-center justify-center p-8">
        <div className="bg-red-900/20 border border-red-900/50 p-6 rounded-xl flex flex-col items-center text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-red-400 mb-4" />
          <h3 className="text-lg font-bold text-slate-100 mb-2">Connection Error</h3>
          <p className="text-slate-400 mb-6">{error}</p>
          <button 
            onClick={loadData}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors border border-slate-700"
          >
            <RefreshCw className="w-4 h-4" />
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto pb-12">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-slate-100">System Overview</h1>
        <p className="text-slate-400 mt-1">Real-time microgrid performance and AI dispatch recommendations.</p>
      </header>

      <KPICards dispatchData={dispatch} />
      
      <div className="space-y-6">
        <ForecastChart data={forecast} />
        <DispatchChart data={dispatch} onBarClick={setSelectedRecord} />
      </div>

      <ExplainabilityPanel 
        isOpen={!!selectedRecord} 
        onClose={() => setSelectedRecord(null)} 
        record={selectedRecord} 
      />
    </div>
  );
}
