'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Settings, Save } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">System Settings</h2>
        <p className="text-slate-400">Configuration for optimization, thresholds, and environment.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle>Microgrid Profile</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm text-slate-400">Microgrid Name</label>
              <input type="text" defaultValue="Kutch Rural Microgrid" className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-slate-200" />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-400">Location Coordinates (Lat, Lng)</label>
              <div className="flex gap-2">
                <input type="text" defaultValue="23.7337" className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-slate-200" />
                <input type="text" defaultValue="69.8597" className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-slate-200" />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-400">Timezone</label>
              <select className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-slate-200">
                <option>Asia/Kolkata (IST)</option>
                <option>UTC</option>
              </select>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle>Optimizer Defaults</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm text-slate-400">Default Diesel Cost (₹/L)</label>
              <input type="number" defaultValue="90" className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-slate-200" />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-400">Carbon Cost Penalty (₹/ton)</label>
              <input type="number" defaultValue="1000" className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-slate-200" />
            </div>
            <div className="pt-4">
              <button className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded font-medium transition-colors">
                <Save size={16} /> Save Configuration
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
