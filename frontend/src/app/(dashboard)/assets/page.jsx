'use client';

import { useSettings, LOCATIONS } from '@/contexts/SettingsContext';
import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Sun, Wind, Battery, Droplet, X } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from 'recharts';

const DATA_TODAY = [
{ time: '00:00', value: 0 }, { time: '02:00', value: 0 }, { time: '04:00', value: 0 },
{ time: '06:00', value: 12 }, { time: '08:00', value: 45 }, { time: '10:00', value: 85 },
{ time: '12:00', value: 110 }, { time: '14:00', value: 90 }, { time: '16:00', value: 45 },
{ time: '18:00', value: 15 }, { time: '20:00', value: 0 }, { time: '22:00', value: 0 }];


const DATA_7D = [
{ time: 'Mon', value: 420 }, { time: 'Tue', value: 380 }, { time: 'Wed', value: 510 },
{ time: 'Thu', value: 490 }, { time: 'Fri', value: 550 }, { time: 'Sat', value: 600 },
{ time: 'Sun', value: 580 }];


const DATA_30D = [
{ time: 'Week 1', value: 3200 }, { time: 'Week 2', value: 2900 },
{ time: 'Week 3', value: 3500 }, { time: 'Week 4', value: 3800 }];














export default function AssetsPage() {
  const { currency, powerScale, formatCurrency, formatPower, locationId } = useSettings();
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [timeframe, setTimeframe] = useState('today');

  const locScale = LOCATIONS.find((l) => l.id === locationId)?.scale || 1.0;

  const [liveData, setLiveData] = useState({
    solar: 50900 * locScale,
    wind: 37400 * locScale,
    bess: 7100 * locScale,
    diesel: 0
  });

  React.useEffect(() => {
    // Reset base values when location changes
    setLiveData({
      solar: 50900 * locScale,
      wind: 37400 * locScale,
      bess: 7100 * locScale,
      diesel: 0
    });

    const interval = setInterval(() => {
      setLiveData((prev) => ({
        solar: Math.max(0, prev.solar + (Math.random() * 2000 - 1000) * locScale),
        wind: Math.max(0, prev.wind + (Math.random() * 2000 - 1000) * locScale),
        bess: prev.bess + (Math.random() * 1000 - 500) * locScale,
        diesel: prev.diesel > 0 ? Math.max(0, prev.diesel + (Math.random() * 1000 - 500)) : 0
      }));
    }, 3000);
    return () => clearInterval(interval);
  }, [locScale]);

  const ASSETS = [
  {
    id: 'solar',
    name: 'Central Solar PV Array',
    subtitle: 'Solar Array',
    Icon: Sun,
    status: liveData.solar > 0 ? 'Producing' : 'Standby',
    statusStyle: liveData.solar > 0 ? 'text-emerald-500 border-emerald-500/30 bg-emerald-500/10' : 'text-outline border-outline bg-surface-container/80',
    iconColor: 'text-emerald-500',
    specs: [
    { label: 'Nameplate', value: '250 {powerScale}', valueStyle: 'text-on-surface font-bold' },
    { label: 'Current Output', value: formatPower(liveData.solar), valueStyle: 'text-emerald-500 font-bold' },
    { label: 'Efficiency', value: '21.4% (Tier-1 Bifacial)', valueStyle: 'text-on-surface font-bold' },
    { label: 'Availability', value: '99.7%', valueStyle: 'text-blue-400 font-bold' }],

    modalSpecs: [
    { label: 'Panels:', value: '580W Bifacial TOPCon (540 modules)' },
    { label: 'Inverters:', value: '2x 125 {powerScale} String Inverters (SMA)' },
    { label: 'Tilt:', value: '24° Fixed South-facing' },
    { label: 'Last Cleaned:', value: '3 days ago' },
    { label: 'Next Maintenance:', value: 'In 18 days' }]

  },
  {
    id: 'wind',
    name: 'Utility Wind Turbine Mast',
    subtitle: 'Wind Turbine',
    Icon: Wind,
    status: liveData.wind > 0 ? 'Generating' : 'Standby',
    statusStyle: liveData.wind > 0 ? 'text-emerald-500 border-emerald-500/30 bg-emerald-500/10' : 'text-outline border-outline bg-surface-container/80',
    iconColor: 'text-emerald-500',
    specs: [
    { label: 'Nameplate', value: '100 {powerScale}', valueStyle: 'text-on-surface font-bold' },
    { label: 'Current Output', value: formatPower(liveData.wind), valueStyle: 'text-emerald-500 font-bold' },
    { label: 'Efficiency', value: '42.8% (Betz limit norm)', valueStyle: 'text-on-surface font-bold' },
    { label: 'Availability', value: '98.5%', valueStyle: 'text-blue-400 font-bold' }],

    modalSpecs: [
    { label: 'Turbine Model:', value: 'Vestas V100 100kW' },
    { label: 'Hub Height:', value: '65 meters' },
    { label: 'Cut-in Speed:', value: '3.5 m/s' },
    { label: 'Last Serviced:', value: '45 days ago' },
    { label: 'Next Maintenance:', value: 'In 140 days' }]

  },
  {
    id: 'bess',
    name: 'Containerized BESS Storage',
    subtitle: 'Battery Storage',
    Icon: Battery,
    status: 'Standby / Discharging',
    statusStyle: 'text-emerald-500 border-emerald-500/30 bg-emerald-500/10',
    iconColor: 'text-emerald-500',
    specs: [
    { label: 'Nameplate', value: '500 kWh / 120 {powerScale}', valueStyle: 'text-on-surface font-bold' },
    { label: 'Current Output', value: `+${formatPower(liveData.bess)}`, valueStyle: 'text-emerald-500 font-bold' },
    { label: 'Efficiency', value: '91.8% Roundtrip', valueStyle: 'text-on-surface font-bold' },
    { label: 'Availability', value: '100%', valueStyle: 'text-blue-400 font-bold' }],

    modalSpecs: [
    { label: 'Chemistry:', value: 'Lithium Iron Phosphate (LFP)' },
    { label: 'Cycles Logged:', value: '1,420 cycles' },
    { label: 'State of Health (SoH):', value: '98.2%' },
    { label: 'Thermal System:', value: 'Liquid Cooled (Nominal)' },
    { label: 'Next Maintenance:', value: 'In 210 days' }]

  },
  {
    id: 'diesel',
    name: 'Auxiliary Diesel Generator',
    subtitle: 'Thermal Genset',
    Icon: Droplet,
    status: liveData.diesel > 0 ? 'Running' : 'Standby Reserve',
    statusStyle: liveData.diesel > 0 ? 'text-red-500 border-red-500/30 bg-red-500/10' : 'text-outline border-outline bg-surface-container/80',
    iconColor: 'text-emerald-500',
    specs: [
    { label: 'Nameplate', value: '150 {powerScale}', valueStyle: 'text-on-surface font-bold' },
    { label: 'Current Output', value: formatPower(liveData.diesel), valueStyle: liveData.diesel > 0 ? 'text-red-500 font-bold' : 'text-emerald-500 font-bold' },
    { label: 'Efficiency', value: '34.2% Brake Thermal', valueStyle: 'text-on-surface font-bold' },
    { label: 'Availability', value: '99.1%', valueStyle: 'text-blue-400 font-bold' }],

    modalSpecs: [
    { label: 'Engine Model:', value: 'Cummins QSB7-G5' },
    { label: 'Fuel Remaining:', value: '4,200 L (84% tank)' },
    { label: 'Run Hours:', value: '342 hrs' },
    { label: 'Last Test Run:', value: '14 days ago' },
    { label: 'Next Maintenance:', value: 'In 60 days' }]

  }];


  // Live API State
  const [dispatchData, setDispatchData] = useState([]);
  const [analyticsData, setAnalyticsData] = useState([]);

  // Fetch LIVE data from backend APIs
  React.useEffect(() => {
    // 1. Fetch Today's 24-hour dispatch curve
    fetch('http://localhost:8000/api/dispatch').
    then((res) => res.json()).
    then((data) => setDispatchData(Array.isArray(data) ? data : [])).
    catch(console.error);

    // 2. Fetch Historical 30-day analytics from the SQLite Database
    fetch('http://localhost:8000/api/analytics').
    then((res) => res.json()).
    then((data) => setAnalyticsData(Array.isArray(data) ? data : [])).
    catch(console.error);
  }, []);

  // Dynamically map the correct live API data depending on which asset is clicked and what timeframe is selected
  let activeChartData = [];
  if (selectedAsset && dispatchData.length > 0) {
    if (timeframe === 'today') {
      activeChartData = dispatchData.map((d) => ({
        time: d.time,
        value: selectedAsset.id === 'solar' ? d.solar :
        selectedAsset.id === 'wind' ? d.wind :
        selectedAsset.id === 'bess' ? d.batteryDischarge :
        d.diesel
      }));
    } else {
      const days = timeframe === '7d' ? 7 : 30;
      // Get the last N days from the database history
      const recentHistory = analyticsData.slice(-days);

      // Calculate a baseline daily total from the dispatch curve
      let baseDailyTotal = 0;
      dispatchData.forEach((h) => {
        baseDailyTotal +=
        selectedAsset.id === 'solar' ? h.solar :
        selectedAsset.id === 'wind' ? h.wind :
        selectedAsset.id === 'bess' ? h.batteryDischarge : h.diesel;

      });

      activeChartData = recentHistory.map((d) => {
        // Since SQLite doesn't store asset-level {powerScale} per day, we modulate the baseline 
        // using the real daily API metrics (renewablePenetration / dieselDependency)
        let modulatedValue = baseDailyTotal;
        if (selectedAsset.id !== 'diesel') {
          modulatedValue *= d.renewablePenetration / 100;
        } else {
          modulatedValue *= d.dieselDependency / 100;
        }

        return {
          time: d.day, // e.g. "Day 1"
          value: Math.round(modulatedValue)
        };
      });
    }
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12 relative">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-1">
          <h2 className="text-2xl font-bold tracking-tight text-on-surface">Energy Assets Registry & Health</h2>
          <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold rounded uppercase tracking-wider border border-emerald-500/20">
            4 Operational Assets
          </span>
        </div>
        <p className="text-outline text-sm">Real-time asset telemetry, operational limits, health metrics, and preventative maintenance schedules</p>
      </div>

      {/* Grid of Assets */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {ASSETS.map((asset) =>
        <Card key={asset.id} className="bg-surface border-outline-variant rounded-xl overflow-hidden shadow-xl flex flex-col">
            <CardContent className="p-6 flex-1 flex flex-col">
              
              <div className="flex justify-between items-start mb-8">
                <div className="flex gap-4 items-start">
                  <div className={`p-2.5 rounded-xl bg-surface-container/80 border border-outline/50 ${asset.iconColor}`}>
                    <asset.Icon size={24} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-on-surface leading-tight mb-1">{asset.name}</h3>
                    <p className="text-sm text-outline">{asset.subtitle}</p>
                  </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-medium border ${asset.statusStyle}`}>
                  {asset.status}
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4 mb-8">
                {asset.specs.map((spec, i) =>
              <div key={i}>
                    <p className="text-[11px] text-on-surface mb-1">{spec.label}</p>
                    <p className={`text-sm ${spec.valueStyle}`}>{spec.value.includes("{powerScale}") ? spec.value.replace(/([\d,.-]+)\s*\{powerScale\}/g, (m, num) => formatPower(parseFloat(num.replace(/,/g, '')))) : spec.value}</p>
                  </div>
              )}
              </div>

              <div className="mt-auto pt-6 border-t border-outline-variant/80 flex justify-between items-center">
                <span className="text-xs text-on-surface">Click to inspect telemetry history</span>
                <button
                onClick={() => setSelectedAsset(asset)}
                className="text-emerald-500 text-xs font-bold hover:text-emerald-300 transition-colors flex items-center gap-1 group">
                
                  Asset Details <span className="group-hover:translate-x-1 transition-transform">→</span>
                </button>
              </div>

            </CardContent>
          </Card>
        )}
      </div>

      {/* Modal Overlay */}
      {selectedAsset &&
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm">
          <div className="bg-surface border border-outline-variant rounded-xl shadow-2xl w-full max-w-4xl overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-200">
            
            <div className="flex items-start justify-between p-6 border-b border-outline-variant/50">
              <div className="flex gap-4 items-center">
                <div className={`p-2 rounded bg-surface-container ${selectedAsset.iconColor}`}>
                  <selectedAsset.Icon size={28} />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-on-surface leading-none mb-1.5">{selectedAsset.name}</h3>
                  <p className="text-outline text-sm">{selectedAsset.subtitle} Telemetry & Diagnostics</p>
                </div>
              </div>
              <button
              onClick={() => setSelectedAsset(null)}
              className="text-outline hover:text-on-surface p-2 rounded hover:bg-surface-container transition-colors">
              
                <X size={24} />
              </button>
            </div>

            <div className="p-8 pb-4">
              <div className="flex justify-between items-center mb-6">
                <h4 className="text-sm font-bold text-on-surface">Historical Telemetry Curve</h4>
                <div className="flex bg-surface-container/50 rounded-xl p-1 border border-outline/50">
                  <button
                  onClick={() => setTimeframe('today')}
                  className={`px-4 py-1 text-xs font-bold rounded transition-colors ${timeframe === 'today' ? 'bg-emerald-500/20 text-emerald-500' : 'text-outline hover:text-on-surface'}`}>
                  
                    Today
                  </button>
                  <button
                  onClick={() => setTimeframe('7d')}
                  className={`px-4 py-1 text-xs font-bold rounded transition-colors ${timeframe === '7d' ? 'bg-emerald-500/20 text-emerald-500' : 'text-outline hover:text-on-surface'}`}>
                  
                    7d
                  </button>
                  <button
                  onClick={() => setTimeframe('30d')}
                  className={`px-4 py-1 text-xs font-bold rounded transition-colors ${timeframe === '30d' ? 'bg-emerald-500/20 text-emerald-500' : 'text-outline hover:text-on-surface'}`}>
                  
                    30d
                  </button>
                </div>
              </div>

              <div className="h-64 w-full mb-8 relative">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={activeChartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={true} horizontal={true} stroke="#e2e8f0" />
                    <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dy={10} />
                    <YAxis
                    domain={[0, 'auto']}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#64748b', fontSize: 12 }}
                    tickFormatter={(val) => formatPower(val)} />
                  
                    <Tooltip
                    contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px' }}
                    itemStyle={{ color: '#10b981' }} />
                  
                    <Area type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorValue)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {selectedAsset.modalSpecs.map((spec, i) =>
              <div key={i} className="flex justify-between items-center p-4 bg-surface-container/30 rounded-xl border border-outline-variant">
                    <span className="text-on-surface-variant font-medium text-sm">{spec.label}</span>
                    <span className="text-on-surface font-bold text-sm">{spec.value.includes("{powerScale}") ? spec.value.replace(/([\d,.-]+)\s*\{powerScale\}/g, (m, num) => formatPower(parseFloat(num.replace(/,/g, '')))) : spec.value}</span>
                  </div>
              )}
              </div>
            </div>

            <div className="p-6 pt-4 flex justify-end">
              <button
              onClick={() => setSelectedAsset(null)}
              className="px-6 py-2.5 bg-surface-container hover:bg-outline-variant text-on-surface text-sm font-bold rounded-xl transition-colors border border-outline">
              
                Close Diagnostic View
              </button>
            </div>

          </div>
        </div>
      }

    </div>);

}