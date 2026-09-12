'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Sun, Wind, Battery, Droplet, Activity, AlertCircle } from 'lucide-react';

export default function AssetsPage() {
  const [assets, setAssets] = React.useState<any[]>([]);

  React.useEffect(() => {
    fetch('http://localhost:8000/api/microgrids/1/status')
      .then(res => res.json())
      .then(data => {
        // Map backend assets to frontend UI shape
        const mappedAssets = data.assets.map((a: any) => {
          let icon = Sun;
          let color = "text-slate-500";
          let bg = "bg-slate-500/10";
          if (a.asset_type === "SOLAR") { icon = Sun; color = "text-yellow-500"; bg = "bg-yellow-500/10"; }
          if (a.asset_type === "WIND") { icon = Wind; color = "text-blue-500"; bg = "bg-blue-500/10"; }
          if (a.asset_type === "BATTERY") { icon = Battery; color = "text-indigo-500"; bg = "bg-indigo-500/10"; }
          if (a.asset_type === "DIESEL") { icon = Droplet; color = "text-red-500"; bg = "bg-red-500/10"; }
          
          return {
            name: a.name,
            type: a.asset_type,
            capacity: a.capacity_kw ? `${a.capacity_kw} kW` : `${a.capacity_kwh} kWh`,
            output: a.current_status === "Producing" || a.current_status === "Discharging" ? "Active" : "Standby",
            status: a.current_status,
            efficiency: `${(a.efficiency * 100).toFixed(0)}%`,
            health: "Good",
            icon, color, bg
          };
        });
        setAssets(mappedAssets);
      })
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Energy Assets</h2>
        <p className="text-slate-400">Detailed view and control of all microgrid generation and storage assets.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {assets.map((asset, idx) => {
          const Icon = asset.icon;
          return (
            <Card key={idx} className="bg-slate-900 border-slate-800">
              <CardHeader className="flex flex-row items-start justify-between pb-2">
                <div className="flex items-center gap-3">
                  <div className={`p-3 rounded-lg ${asset.bg} ${asset.color}`}>
                    <Icon size={24} />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{asset.name}</CardTitle>
                    <p className="text-sm text-slate-400">{asset.type} Asset</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 text-xs font-medium border border-slate-700">
                  <Activity size={14} className={asset.status === 'Producing' ? 'text-emerald-500' : 'text-slate-400'} />
                  {asset.status}
                </div>
              </CardHeader>
              <CardContent className="mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <p className="text-xs text-slate-500">Rated Capacity</p>
                    <p className="font-medium text-slate-200">{asset.capacity}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-slate-500">Current Output</p>
                    <p className={`font-bold ${asset.color}`}>{asset.output}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-slate-500">Operating Efficiency</p>
                    <p className="font-medium text-slate-200">{asset.efficiency}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-slate-500">System Health</p>
                    <p className={`font-medium flex items-center gap-1 ${asset.health.includes('Maintenance') ? 'text-yellow-500' : 'text-emerald-500'}`}>
                      {asset.health.includes('Maintenance') && <AlertCircle size={14} />}
                      {asset.health}
                    </p>
                  </div>
                </div>
                <div className="mt-6 flex gap-2">
                  <button className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-sm font-medium rounded transition-colors text-slate-200">Diagnostics</button>
                  <button className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-sm font-medium rounded transition-colors text-slate-200">Configure</button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
