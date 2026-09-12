'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MapPin, Zap, Battery, Droplet, Sun, Wind } from 'lucide-react';

// Dynamically import the map component so it doesn't SSR (Leaflet requires window)
const MapComponent = dynamic(() => import('../../../components/MapComponent'), { 
  ssr: false,
  loading: () => (
    <div className="h-[500px] w-full bg-slate-900 border-2 border-slate-800 rounded-xl flex items-center justify-center text-slate-500">
      Loading geographic data...
    </div>
  )
});

export default function MapPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Microgrid Map</h2>
          <p className="text-slate-400">Geographic overview of community assets and critical infrastructure.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="col-span-1 lg:col-span-3">
          <Card className="bg-slate-900 border-slate-800 overflow-hidden">
             <MapComponent />
          </Card>
        </div>
        
        <div className="col-span-1 space-y-4">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-lg">Assets Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-yellow-500/10 rounded-full text-yellow-500">
                  <Sun size={20} />
                </div>
                <div>
                  <div className="font-bold text-slate-200">Solar Array (250 kW)</div>
                  <div className="text-xs text-slate-400">Status: Producing (84 kW)</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-500/10 rounded-full text-blue-500">
                  <Wind size={20} />
                </div>
                <div>
                  <div className="font-bold text-slate-200">Wind Turbine (100 kW)</div>
                  <div className="text-xs text-slate-400">Status: Producing (36 kW)</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-500/10 rounded-full text-indigo-500">
                  <Battery size={20} />
                </div>
                <div>
                  <div className="font-bold text-slate-200">Main Battery (500 kWh)</div>
                  <div className="text-xs text-slate-400">Status: Discharging</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-red-500/10 rounded-full text-red-500">
                  <Droplet size={20} />
                </div>
                <div>
                  <div className="font-bold text-slate-200">Diesel Backup (150 kW)</div>
                  <div className="text-xs text-slate-400">Status: Standby</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800 border-l-4 border-l-emerald-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-slate-400">Critical Infrastructure</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2 text-sm text-emerald-400">
                <MapPin size={14} /> Community Health Clinic
              </div>
              <div className="flex items-center gap-2 text-sm text-emerald-400">
                <MapPin size={14} /> Main Water Pump
              </div>
              <div className="flex items-center gap-2 text-sm text-emerald-400">
                <MapPin size={14} /> School Building
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
