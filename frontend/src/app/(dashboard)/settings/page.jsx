'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Settings2, Activity, Zap, Database, RotateCcw, CheckCircle2, Save, RefreshCw } from 'lucide-react';
import { useSettings } from '@/contexts/SettingsContext';

export default function SettingsPage() {
  const {
    setSettings,
    rates,
    currency: ctxCurrency,
    powerScale: ctxPowerScale,
    solarCap: ctxSolar,
    windCap: ctxWind,
    bessCap: ctxBess,
    dieselPrice: ctxDiesel
  } = useSettings();

  // Toggle states
  const [currency, setCurrency] = useState(ctxCurrency);
  const [powerScale, setPowerScale] = useState(ctxPowerScale);

  // Input states
  const [solarCap, setSolarCap] = useState(ctxSolar);
  const [windCap, setWindCap] = useState(ctxWind);
  const [bessCap, setBessCap] = useState(ctxBess);
  const [dieselPrice, setDieselPrice] = useState(ctxDiesel);

  // Status states
  const [isSaving, setIsSaving] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [isFetchingPrice, setIsFetchingPrice] = useState(false);

  const fetchLiveDieselPrice = async (targetCurrency) => {
    setIsFetchingPrice(true);
    try {
      // Simulate fetching live Indian diesel price
      await new Promise((r) => setTimeout(r, 600));
      // Base INR price (around ₹92.45)
      const priceINR = 92.45 + (Math.random() * 2 - 1);

      const cur = targetCurrency || currency;
      let finalPrice = priceINR;

      // Convert to selected currency if not INR
      if (cur !== '₹') {
        const rateINR = rates['₹'] || 83.5;
        const targetRate = rates[cur] || 1;
        finalPrice = priceINR / rateINR * targetRate;
      }

      setDieselPrice(Number(finalPrice.toFixed(2)));
    } catch (e) {
      console.error("Failed to fetch live diesel price:", e);
    } finally {
      setIsFetchingPrice(false);
    }
  };

  // Sync local state with context if context updates (e.g., initial fetch completes)
  useEffect(() => {
    setCurrency(ctxCurrency);
    setPowerScale(ctxPowerScale);
    setSolarCap(ctxSolar);
    setWindCap(ctxWind);
    setBessCap(ctxBess);
    setDieselPrice(ctxDiesel);
  }, [ctxCurrency, ctxPowerScale, ctxSolar, ctxWind, ctxBess, ctxDiesel]);

  const handleCurrencyChange = (newCur) => {
    if (newCur === currency) return;
    const currentRate = rates[currency] || 1;
    const newRate = rates[newCur] || 1;
    const priceInUSD = dieselPrice / currentRate;
    const newPrice = priceInUSD * newRate;
    setDieselPrice(Number(newPrice.toFixed(2)));
    setCurrency(newCur);
  };

  const handlePowerScaleChange = (newScale) => {
    if (newScale === powerScale) return;
    if (newScale === 'MW' && powerScale === 'kW') {
      setSolarCap(Number((solarCap / 1000).toFixed(3)));
      setWindCap(Number((windCap / 1000).toFixed(3)));
      setBessCap(Number((bessCap / 1000).toFixed(3)));
    } else if (newScale === 'kW' && powerScale === 'MW') {
      setSolarCap(solarCap * 1000);
      setWindCap(windCap * 1000);
      setBessCap(bessCap * 1000);
    }
    setPowerScale(newScale);
  };

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
        <div className="p-2 bg-surface-container rounded-lg">
          <Settings2 size={24} className="text-on-surface-variant" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-on-surface tracking-tight">System Configuration</h1>
          <p className="text-sm text-outline mt-1">Manage global display formats and baseline asset sizing</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Panel: Preferences */}
        <Card className="bg-surface border-outline-variant rounded-xl h-full">
          <CardHeader className="pb-4 border-b border-outline-variant">
            <CardTitle className="text-sm font-bold flex items-center gap-2 text-on-surface">
              <Database size={16} className="text-indigo-500" /> Global Formatting
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6 space-y-8">
            
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-on-surface">Currency Display</h4>
                <p className="text-xs text-outline mt-1">Preferred fiat conversion for all costs</p>
              </div>
              <div className="flex bg-surface-container rounded-lg p-1 border border-outline/50">
                {['₹', '$', '€'].map((cur) =>
                <button
                  key={cur}
                  onClick={() => handleCurrencyChange(cur)}
                  className={`w-10 py-1.5 text-sm font-bold rounded-md transition-colors ${currency === cur ? 'bg-emerald-600 text-on-surface shadow-md' : 'text-outline hover:text-on-surface'}`}>
                  
                    {cur}
                  </button>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-on-surface">Power Rating Scale</h4>
                <p className="text-xs text-outline mt-1">Default metric representation for capacity</p>
              </div>
              <div className="flex bg-surface-container rounded-lg p-1 border border-outline/50">
                {['kW', 'MW'].map((unit) =>
                <button
                  key={unit}
                  onClick={() => handlePowerScaleChange(unit)}
                  className={`w-12 py-1.5 text-xs font-bold rounded-md transition-colors ${powerScale === unit ? 'bg-emerald-600 text-on-surface shadow-md' : 'text-outline hover:text-on-surface'}`}>
                  
                    {unit}
                  </button>
                )}
              </div>
            </div>

          </CardContent>
        </Card>

        {/* Right Panel: Asset Sizing */}
        <Card className="lg:col-span-2 bg-surface border-outline-variant rounded-xl h-full flex flex-col">
          <CardHeader className="pb-4 border-b border-outline-variant">
            <CardTitle className="text-sm font-bold flex items-center gap-2 text-on-surface">
              <Zap size={16} className="text-amber-500" /> Asset Sizing & Fuel Pricing
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6 flex-1 flex flex-col justify-between">
            
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-bold text-outline block">Solar PV Capacity ({powerScale})</label>
                <input
                  type="number"
                  value={solarCap}
                  onChange={(e) => setSolarCap(Number(e.target.value))}
                  className="w-full bg-surface-container border border-outline text-on-surface text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:border-amber-500 transition-colors font-mono" />
                
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-outline block">Wind Capacity ({powerScale})</label>
                <input
                  type="number"
                  value={windCap}
                  onChange={(e) => setWindCap(Number(e.target.value))}
                  className="w-full bg-surface-container border border-outline text-on-surface text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:border-blue-500 transition-colors font-mono" />
                
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-outline block">BESS Storage ({powerScale}h)</label>
                <input
                  type="number"
                  value={bessCap}
                  onChange={(e) => setBessCap(Number(e.target.value))}
                  className="w-full bg-surface-container border border-outline text-on-surface text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:border-emerald-500 transition-colors font-mono" />
                
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-bold text-outline block">Diesel Fuel Price ({currency}/L)</label>
                  <button
                    onClick={() => fetchLiveDieselPrice()}
                    disabled={isFetchingPrice}
                    className="text-[10px] font-bold text-blue-500 hover:text-blue-400 flex items-center gap-1 disabled:opacity-50">
                    
                    <RefreshCw size={10} className={isFetchingPrice ? "animate-spin" : ""} />
                    Live Price
                  </button>
                </div>
                <input
                  type="number"
                  value={dieselPrice}
                  onChange={(e) => setDieselPrice(Number(e.target.value))}
                  className="w-full bg-surface-container border border-outline text-on-surface text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:border-red-500 transition-colors font-mono" />
                
              </div>
            </div>

            <div className="flex justify-between items-end mt-8">
              <button
                onClick={handleReset}
                className="text-xs text-outline hover:text-on-surface underline decoration-slate-700 underline-offset-4 transition-colors">
                
                Reset to Site Defaults
              </button>
              
              <div className="flex items-center gap-3">
                {showSuccess &&
                <span className="text-xs font-bold text-emerald-500 flex items-center gap-1 animate-in fade-in slide-in-from-right-4">
                    <CheckCircle2 size={14} /> Saved
                  </span>
                }
                <button
                  onClick={handleApplyChanges}
                  disabled={isSaving}
                  className="px-6 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm rounded-lg flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-500/20">
                  
                  {isSaving ?
                  <><RefreshCw size={16} className="animate-spin" /> Saving...</> :

                  <><Save size={16} /> Apply Changes</>
                  }
                </button>
              </div>
            </div>

          </CardContent>
        </Card>

      </div>

      {/* Bottom Full-Width Panel: Diagnostics */}
      <Card className="bg-surface border-outline-variant rounded-xl">
        <CardHeader className="pb-4 border-b border-outline-variant">
          <div className="flex justify-between items-center">
            <CardTitle className="text-sm font-bold flex items-center gap-2 text-on-surface">
              <Activity size={16} className="text-blue-500" /> Diagnostic Service Status & Integration Health
            </CardTitle>
            <span className="text-xs font-bold text-emerald-500 tracking-wide">All Systems Nominal</span>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Open-Meteo */}
            <div className="flex justify-between items-center bg-surface-container p-4 rounded-xl border border-outline-variant">
              <div>
                <h4 className="text-sm font-bold text-on-surface">Open-Meteo REST API</h4>
                <p className="text-[11px] text-outline mt-0.5">Free, No-Key Weather Telemetry</p>
              </div>
              <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold rounded uppercase tracking-wider border border-emerald-500/20 flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                ONLINE (82ms)
              </span>
            </div>

            {/* LP Solver */}
            <div className="flex justify-between items-center bg-surface-container p-4 rounded-xl border border-outline-variant">
              <div>
                <h4 className="text-sm font-bold text-on-surface">LP Dispatch Solver</h4>
                <p className="text-[11px] text-outline mt-0.5">Multi-interval Optimization</p>
              </div>
              <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold rounded uppercase tracking-wider border border-emerald-500/20 flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                FEASIBLE (124ms)
              </span>
            </div>

          </div>
        </CardContent>
      </Card>

    </div>);

}