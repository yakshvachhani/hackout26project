'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Leaf, Droplet, Zap, Battery, CircleDollarSign, Wind, Sun, CloudRain } from 'lucide-react';
import { cn } from '@/lib/utils';

// Flow Diagram Component
function EnergyFlowDiagram({ data }: { data: any }) {
  if (!data) return <div className="h-64 flex items-center justify-center text-slate-500">Loading flow...</div>;

  return (
    <div className="relative h-80 w-full rounded-xl bg-slate-900 border border-slate-800 overflow-hidden flex items-center justify-center p-8">
      {/* Central Bus */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-slate-800 px-6 py-3 rounded-lg border-2 border-emerald-500 z-10 font-bold text-emerald-400">
        MICROGRID BUS
      </div>

      {/* Solar */}
      <div className="absolute top-8 left-1/2 -translate-x-1/2 flex flex-col items-center">
        <Sun className="text-yellow-400 mb-2" size={32} />
        <div className="bg-slate-800 px-3 py-1 rounded text-sm font-medium border border-slate-700">Solar</div>
        <div className="text-xs text-yellow-400 mt-1 font-mono">84 kW</div>
      </div>
      
      {/* Wind */}
      <div className="absolute top-1/2 left-8 -translate-y-1/2 flex flex-col items-center">
        <Wind className="text-blue-400 mb-2" size={32} />
        <div className="bg-slate-800 px-3 py-1 rounded text-sm font-medium border border-slate-700">Wind</div>
        <div className="text-xs text-blue-400 mt-1 font-mono">36 kW</div>
      </div>

      {/* Battery */}
      <div className="absolute top-1/2 right-8 -translate-y-1/2 flex flex-col items-center">
        <Battery className="text-indigo-400 mb-2" size={32} />
        <div className="bg-slate-800 px-3 py-1 rounded text-sm font-medium border border-slate-700">Battery</div>
        <div className="text-xs text-indigo-400 mt-1 font-mono">-22 kW</div>
        <div className="text-[10px] text-slate-400">SOC: 68%</div>
      </div>

      {/* Diesel */}
      <div className="absolute bottom-8 left-1/4 -translate-x-1/2 flex flex-col items-center">
        <Droplet className="text-red-400 mb-2" size={32} />
        <div className="bg-slate-800 px-3 py-1 rounded text-sm font-medium border border-slate-700">Diesel</div>
        <div className="text-xs text-red-400 mt-1 font-mono">18 kW</div>
      </div>

      {/* Load */}
      <div className="absolute bottom-8 right-1/4 translate-x-1/2 flex flex-col items-center">
        <Zap className="text-emerald-400 mb-2" size={32} />
        <div className="bg-slate-800 px-3 py-1 rounded text-sm font-medium border border-slate-700">Load</div>
        <div className="text-xs text-emerald-400 mt-1 font-mono">116 kW</div>
      </div>
      
      {/* TODO: Add SVG lines connecting them */}
    </div>
  );
}

function KpiCard({ title, value, subValue, icon: Icon, colorClass }: any) {
  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-slate-400">{title}</CardTitle>
        <Icon className={cn("h-4 w-4", colorClass)} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-slate-50">{value}</div>
        <p className="text-xs text-slate-500 mt-1">{subValue}</p>
      </CardContent>
    </Card>
  );
}

export default function OverviewPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    // In a real app we fetch from backend
    // fetch('http://localhost:8000/api/microgrids/1/status')
    setTimeout(() => {
      setData({ status: 'ok' } as any);
    }, 500);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Executive Overview</h2>
        <p className="text-slate-400">Real-time microgrid status and key performance indicators.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <KpiCard title="Renewable Share" value="74.8%" subValue="Target: 80%" icon={Leaf} colorClass="text-emerald-500" />
        <KpiCard title="Diesel Dependency" value="12.4%" subValue="-2.1% from yesterday" icon={Droplet} colorClass="text-red-500" />
        <KpiCard title="Current Load" value="116 kW" subValue="Peak: 184 kW" icon={Zap} colorClass="text-yellow-500" />
        <KpiCard title="Battery SOC" value="68%" subValue="Charging (340 kWh)" icon={Battery} colorClass="text-indigo-500" />
        <KpiCard title="Operating Cost" value="₹2,840" subValue="Projected: ₹3,240" icon={CircleDollarSign} colorClass="text-emerald-400" />
        <KpiCard title="Carbon Avoided" value="126 kg" subValue="Equivalent to 5 trees" icon={CloudRain} colorClass="text-blue-400" />
      </div>

      <div className="grid gap-4 grid-cols-1 xl:grid-cols-3">
        <Card className="col-span-2 bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle>Real-Time Power Flow</CardTitle>
          </CardHeader>
          <CardContent>
            <EnergyFlowDiagram data={data} />
          </CardContent>
        </Card>
        
        <Card className="col-span-1 bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle>Live Power Balance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 font-mono text-sm">
              <div className="space-y-2">
                <div className="text-slate-500 mb-1">GENERATION</div>
                <div className="flex justify-between text-yellow-400"><span>Solar</span><span>84 kW</span></div>
                <div className="flex justify-between text-blue-400"><span>Wind</span><span>36 kW</span></div>
                <div className="flex justify-between text-red-400"><span>Diesel</span><span>18 kW</span></div>
                <div className="flex justify-between text-indigo-400"><span>Battery</span><span>-22 kW</span></div>
                <div className="border-t border-slate-800 pt-2 flex justify-between font-bold text-white mt-2">
                  <span>Total Gen</span><span>116 kW</span>
                </div>
              </div>
              <div className="border-t border-slate-800 pt-4 space-y-2">
                <div className="flex justify-between text-emerald-400 font-bold"><span>Demand</span><span>116 kW</span></div>
                <div className="flex justify-between text-slate-400"><span>Spinning Reserve</span><span>24 kW</span></div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
