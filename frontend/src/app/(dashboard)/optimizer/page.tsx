'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Play, Settings, ArrowRight, Zap, Target, BarChart, Server } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function OptimizerPage() {
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const runOptimization = async () => {
    setIsOptimizing(true);
    try {
      // In a real app we fetch from our backend
      // const res = await fetch('http://localhost:8000/api/optimize?grid_id=1', { method: 'POST' });
      // const json = await res.json();
      
      // Simulate API delay
      await new Promise(r => setTimeout(r, 1200));
      
      setResult({
        solver_status: "Optimal",
        cost: 3240.50,
        baseline_cost: 4850.00,
        diesel_savings: 43,
        co2_savings: 43,
        explanation: "Solar generation is expected to be high between 10:00 and 15:00, so the optimizer prioritizes solar and charges the battery. Battery discharge is reserved for the evening peak because diesel fuel cost is high."
      });
    } catch (e) {
      console.error(e);
    }
    setIsOptimizing(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Energy Mix Optimizer</h2>
        <p className="text-slate-400">Configure parameters and run the MILP optimization engine.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Controls */}
        <div className="col-span-1 space-y-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Settings size={18} /> Optimization Parameters</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <label className="text-slate-400 font-medium">Diesel Price (₹/L)</label>
                  <span className="text-slate-50 font-mono">90.00</span>
                </div>
                <input type="range" min="50" max="150" defaultValue="90" className="w-full accent-emerald-500" />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <label className="text-slate-400 font-medium">Carbon Price (₹/ton)</label>
                  <span className="text-slate-50 font-mono">1000</span>
                </div>
                <input type="range" min="0" max="5000" defaultValue="1000" className="w-full accent-emerald-500" />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <label className="text-slate-400 font-medium">Min Battery Reserve (%)</label>
                  <span className="text-slate-50 font-mono">20%</span>
                </div>
                <input type="range" min="0" max="50" defaultValue="20" className="w-full accent-emerald-500" />
              </div>

              <div className="space-y-2">
                <label className="text-sm text-slate-400 font-medium block mb-2">Priority Objective</label>
                <div className="flex bg-slate-800 p-1 rounded-md">
                  <button className="flex-1 py-1.5 text-xs font-medium bg-emerald-600 text-white rounded shadow-sm">Lowest Cost</button>
                  <button className="flex-1 py-1.5 text-xs font-medium text-slate-400 hover:text-slate-200">Balanced</button>
                  <button className="flex-1 py-1.5 text-xs font-medium text-slate-400 hover:text-slate-200">Lowest Emissions</button>
                </div>
              </div>

              <button 
                onClick={runOptimization}
                disabled={isOptimizing}
                className="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                {isOptimizing ? (
                  <span className="animate-pulse">Optimizing...</span>
                ) : (
                  <><Play size={18} fill="currentColor" /> Run Optimization</>
                )}
              </button>
              
              <div className="text-xs text-slate-500 text-center flex items-center justify-center gap-1">
                <Server size={12} /> Powered by SciPy MILP Solver
              </div>

            </CardContent>
          </Card>
        </div>

        {/* Results */}
        <div className="col-span-1 lg:col-span-2">
          {!result && !isOptimizing && (
            <div className="h-full min-h-[400px] border-2 border-dashed border-slate-800 rounded-xl flex flex-col items-center justify-center text-slate-500">
              <Target size={48} className="mb-4 opacity-50" />
              <p>Adjust parameters and run the optimizer to generate a dispatch strategy.</p>
            </div>
          )}

          {isOptimizing && (
            <div className="h-full min-h-[400px] border border-slate-800 rounded-xl flex flex-col items-center justify-center text-emerald-500 bg-slate-900/50">
              <Zap size={48} className="mb-4 animate-pulse" />
              <p className="animate-pulse">Solving mixed-integer linear program...</p>
            </div>
          )}

          {result && !isOptimizing && (
            <div className="space-y-6">
              <Card className="bg-slate-900 border-slate-800 border-l-4 border-l-emerald-500">
                <CardHeader>
                  <CardTitle>Optimization Strategy</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-300 leading-relaxed">
                    {result.explanation}
                  </p>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader className="pb-2"><CardTitle className="text-sm text-slate-400">Daily Cost</CardTitle></CardHeader>
                  <CardContent>
                    <div className="flex items-end gap-2">
                      <span className="text-2xl font-bold text-emerald-400">₹{result.cost.toFixed(0)}</span>
                      <span className="text-sm text-slate-500 line-through mb-1">₹{result.baseline_cost.toFixed(0)}</span>
                    </div>
                    <p className="text-xs text-emerald-500 mt-1 font-medium">↓ {(100 - (result.cost / result.baseline_cost) * 100).toFixed(1)}% savings</p>
                  </CardContent>
                </Card>

                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader className="pb-2"><CardTitle className="text-sm text-slate-400">Diesel Use</CardTitle></CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-slate-50">52 L</div>
                    <p className="text-xs text-emerald-500 mt-1 font-medium">↓ {result.diesel_savings}% reduction</p>
                  </CardContent>
                </Card>

                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader className="pb-2"><CardTitle className="text-sm text-slate-400">Emissions</CardTitle></CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-slate-50">139 kg</div>
                    <p className="text-xs text-emerald-500 mt-1 font-medium">↓ {result.co2_savings}% reduction</p>
                  </CardContent>
                </Card>
              </div>

              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2"><BarChart size={18} /> Recommended Dispatch Plan</CardTitle>
                  <CardDescription>View the detailed hour-by-hour schedule in the Live Dispatch view.</CardDescription>
                </CardHeader>
                <CardContent className="flex justify-end">
                   <button className="text-emerald-400 text-sm font-medium flex items-center hover:text-emerald-300">
                     View Full Schedule <ArrowRight size={16} className="ml-1" />
                   </button>
                </CardContent>
              </Card>

            </div>
          )}
        </div>

      </div>
    </div>
  );
}
