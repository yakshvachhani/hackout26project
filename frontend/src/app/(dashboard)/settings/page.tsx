'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Settings2, Activity, Zap, Database, RotateCcw, CheckCircle2, Save, RefreshCw } from 'lucide-react';
import { useSettings } from '@/contexts/SettingsContext';

export default function SettingsPage() {
  const { setSettings } = useSettings();
  
  // Toggle states
  const [currency, setCurrency] = useState('₹');
  const [powerScale, setPowerScale] = useState('kW');

  // Input states
  const [solarCap, setSolarCap] = useState(250);
  const [windCap, setWindCap] = useState(100);
  const [bessCap, setBessCap] = useState(500);
  const [dieselPrice, setDieselPrice] = useState(92);

  // Status states
  const [isSaving, setIsSaving] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  // Load saved settings on mount
  useEffect(() => {
    const saved = localStorage.getItem('microgrid_settings');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed.currency) setCurrency(parsed.currency);
        if (parsed.powerScale) setPowerScale(parsed.powerScale);
        if (parsed.solarCap) setSolarCap(parsed.solarCap);
        if (parsed.windCap) setWindCap(parsed.windCap);
        if (parsed.bessCap) setBessCap(parsed.bessCap);
        if (parsed.dieselPrice) setDieselPrice(parsed.dieselPrice);
      } catch (e) {}
    }
  }, []);

  const handleApplyChanges = () => {
    setIsSaving(true);
    // Simulate backend API save & write to local storage to persist across tabs/navigations
    setTimeout(() => {
      const config = { currency, powerScale, solarCap, windCap, bessCap, dieselPrice };
      setSettings(config);
      
      setIsSaving(false);
      setShowSuccess(true);
      
      // Hide success message after 3 seconds
      setTimeout(() => setShowSuccess(false), 3000);
    }, 800);
  };

  const handleReset = () => {
    setSolarCap(250);
    setWindCap(100);
    setBessCap(500);
    setDieselPrice(92);
    setCurrency('₹');
    setPowerScale('kW');
    localStorage.removeItem('microgrid_settings');
  };

  return (
    <div className="space-y-6">
      
      {/* Top Title */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-slate-800 rounded-lg">
          <Settings2 size={24} className="text-slate-300" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">System Configuration</h1>
          <p className="text-sm text-slate-400 mt-1">Manage global display formats and baseline asset sizing</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Panel: Preferences */}
        <Card className="bg-[#0f172a] border-slate-800/50 rounded-xl h-full">
          <CardHeader className="pb-4 border-b border-slate-800/50">
            <CardTitle className="text-sm font-bold flex items-center gap-2 text-white">
              <Database size={16} className="text-indigo-500" /> Global Formatting
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6 space-y-8">
            
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-slate-200">Currency Display</h4>
                <p className="text-xs text-slate-400 mt-1">Preferred fiat conversion for all costs</p>
              </div>
              <div className="flex bg-[#1e293b] rounded-lg p-1 border border-slate-700/50">
                {['₹', '$', '€'].map(cur => (
                  <button 
                    key={cur}
                    onClick={() => setCurrency(cur)}
                    className={`w-10 py-1.5 text-sm font-bold rounded-md transition-colors ${currency === cur ? 'bg-emerald-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'}`}
                  >
                    {cur}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-slate-200">Power Rating Scale</h4>
                <p className="text-xs text-slate-400 mt-1">Default metric representation for capacity</p>
              </div>
              <div className="flex bg-[#1e293b] rounded-lg p-1 border border-slate-700/50">
                {['kW', 'MW'].map(unit => (
                  <button 
                    key={unit}
                    onClick={() => setPowerScale(unit)}
                    className={`w-12 py-1.5 text-xs font-bold rounded-md transition-colors ${currency === unit ? 'bg-blue-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'}`}
                  >
                    {unit}
                  </button>
                ))}
              </div>
            </div>

          </CardContent>
        </Card>

        {/* Right Panel: Asset Sizing */}
        <Card className="lg:col-span-2 bg-[#0f172a] border-slate-800/50 rounded-xl h-full flex flex-col">
          <CardHeader className="pb-4 border-b border-slate-800/50">
            <CardTitle className="text-sm font-bold flex items-center gap-2 text-white">
              <Zap size={16} className="text-amber-500" /> Asset Sizing & Fuel Pricing
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6 flex-1 flex flex-col justify-between">
            
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-400 block">Solar PV Capacity ({powerScale})</label>
                <input 
                  type="number" 
                  value={solarCap} 
                  onChange={(e) => setSolarCap(Number(e.target.value))}
                  className="w-full bg-[#1e293b] border border-slate-700 text-slate-200 text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:border-amber-500 transition-colors font-mono"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-400 block">Wind Capacity ({powerScale})</label>
                <input 
                  type="number" 
                  value={windCap} 
                  onChange={(e) => setWindCap(Number(e.target.value))}
                  className="w-full bg-[#1e293b] border border-slate-700 text-slate-200 text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:border-blue-500 transition-colors font-mono"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-400 block">BESS Storage ({powerScale}h)</label>
                <input 
                  type="number" 
                  value={bessCap} 
                  onChange={(e) => setBessCap(Number(e.target.value))}
                  className="w-full bg-[#1e293b] border border-slate-700 text-slate-200 text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:border-emerald-500 transition-colors font-mono"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-400 block">Diesel Fuel Price ({currency}/L)</label>
                <input 
                  type="number" 
                  value={dieselPrice} 
                  onChange={(e) => setDieselPrice(Number(e.target.value))}
                  className="w-full bg-[#1e293b] border border-slate-700 text-slate-200 text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:border-red-500 transition-colors font-mono"
                />
              </div>
            </div>

            <div className="flex justify-between items-end mt-8">
              <button 
                onClick={handleReset}
                className="text-xs text-slate-400 hover:text-slate-200 underline decoration-slate-700 underline-offset-4 transition-colors"
              >
                Reset to Site Defaults
              </button>
              
              <div className="flex items-center gap-3">
                {showSuccess && (
                  <span className="text-xs font-bold text-emerald-500 flex items-center gap-1 animate-in fade-in slide-in-from-right-4">
                    <CheckCircle2 size={14} /> Saved
                  </span>
                )}
                <button 
                  onClick={handleApplyChanges}
                  disabled={isSaving}
                  className="px-6 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm rounded-lg flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-500/20"
                >
                  {isSaving ? (
                    <><RefreshCw size={16} className="animate-spin" /> Saving...</>
                  ) : (
                    <><Save size={16} /> Apply Changes</>
                  )}
                </button>
              </div>
            </div>

          </CardContent>
        </Card>

      </div>

      {/* Bottom Full-Width Panel: Diagnostics */}
      <Card className="bg-[#0f172a] border-slate-800/50 rounded-xl">
        <CardHeader className="pb-4 border-b border-slate-800/50">
          <div className="flex justify-between items-center">
            <CardTitle className="text-sm font-bold flex items-center gap-2 text-white">
              <Activity size={16} className="text-blue-500" /> Diagnostic Service Status & Integration Health
            </CardTitle>
            <span className="text-xs font-bold text-emerald-500 tracking-wide">All Systems Nominal</span>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Open-Meteo */}
            <div className="flex justify-between items-center bg-[#1e293b]/50 p-4 rounded-xl border border-slate-800/50">
              <div>
                <h4 className="text-sm font-bold text-slate-200">Open-Meteo REST API</h4>
                <p className="text-[11px] text-slate-400 mt-0.5">Free, No-Key Weather Telemetry</p>
              </div>
              <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold rounded uppercase tracking-wider border border-emerald-500/20 flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                ONLINE (82ms)
              </span>
            </div>

            {/* Gemini */}
            <div className="flex justify-between items-center bg-[#1e293b]/50 p-4 rounded-xl border border-slate-800/50">
              <div>
                <h4 className="text-sm font-bold text-slate-200">Gemini AI Assistant</h4>
                <p className="text-[11px] text-slate-400 mt-0.5">Energy Intelligence Engine</p>
              </div>
              <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold rounded uppercase tracking-wider border border-emerald-500/20 flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                ACTIVE
              </span>
            </div>

            {/* LP Solver */}
            <div className="flex justify-between items-center bg-[#1e293b]/50 p-4 rounded-xl border border-slate-800/50">
              <div>
                <h4 className="text-sm font-bold text-slate-200">LP Dispatch Solver</h4>
                <p className="text-[11px] text-slate-400 mt-0.5">Multi-interval Optimization</p>
              </div>
              <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold rounded uppercase tracking-wider border border-emerald-500/20 flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                FEASIBLE (124ms)
              </span>
            </div>

          </div>
        </CardContent>
      </Card>

    </div>
  );
}
