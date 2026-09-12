'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { FileText, Download } from 'lucide-react';

export default function ReportsPage() {
  const exportCSV = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Asset,Capacity,Energy Delivered,Capacity Factor,Availability,Status\n"
      + "Central Solar PV,250 kW,684 kWh,22.4%,100%,Nominal\n"
      + "Wind Turbine,100 kW,248 kWh,31.2%,98.5%,Nominal\n"
      + "BESS Storage,500 kWh,342 kWh cycled,91.8%,100%,Healthy\n"
      + "Diesel Genset,150 kW,152 kWh,14.1%,99.1%,Standby\n";
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "daily_dispatch_log.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportPDF = () => {
    window.print();
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Top Header - Hidden during PDF print */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 print:hidden">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold tracking-tight text-white">Executive Energy & ESG Reports</h2>
            <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 text-[10px] font-bold rounded uppercase tracking-wider border border-emerald-500/30">
              Audit Compliant
            </span>
          </div>
          <p className="text-slate-400 mt-1 text-sm">Automated operational dispatch summaries, financial fuel audits, and sustainability reporting</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={exportPDF} className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium text-sm transition-colors shadow-lg shadow-emerald-900/20">
            <Download size={16} /> Export PDF
          </button>
          <button onClick={exportCSV} className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg font-medium text-sm transition-colors">
            <FileText size={16} /> Export CSV
          </button>
        </div>
      </div>

      {/* Tabs Menu - Hidden during PDF print */}
      <div className="flex gap-6 border-b border-slate-800 pb-2 print:hidden">
        <button className="text-sm font-bold text-white border-b-2 border-emerald-500 pb-2">Daily Operational Log</button>
        <button className="text-sm font-medium text-slate-400 hover:text-slate-200 pb-2">Weekly Dispatch Summary</button>
        <button className="text-sm font-medium text-slate-400 hover:text-slate-200 pb-2">Monthly Financial Audit</button>
        <button className="text-sm font-medium text-slate-400 hover:text-slate-200 pb-2">Annual ESG & Carbon Report</button>
      </div>

      {/* Printable Report Document */}
      <div className="bg-[#0f172a] rounded-xl border border-slate-800 p-8 shadow-2xl relative print:bg-white print:text-black print:border-none print:shadow-none print:p-0">
        
        {/* Document Header */}
        <div className="flex justify-between items-start mb-10">
          <div>
            <div className="text-[10px] font-bold tracking-widest text-emerald-500 uppercase mb-2">Gridwise Microgrid Intelligence System</div>
            <h1 className="text-2xl font-bold text-white mb-1 print:text-slate-900">Daily Operational & Dispatch Audit Log</h1>
            <p className="text-sm text-slate-400 print:text-slate-600">Facility: Kutch Rural Microgrid (Dhordo, Gujarat)</p>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-400 mb-1 print:text-slate-500">Report Ref: #GW-2026-09</div>
            <div className="text-xs text-slate-400 mb-2 print:text-slate-500">Generated: 12 September 2026</div>
            <div className="inline-block px-2 py-0.5 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold uppercase tracking-wider rounded border border-emerald-500/20">
              Verified
            </div>
          </div>
        </div>

        {/* KPI Row */}
        <div className="grid grid-cols-4 gap-4 mb-10">
          <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800 print:bg-slate-50 print:border-slate-200">
            <div className="text-xs text-slate-400 mb-2 print:text-slate-500">Total Generation</div>
            <div className="text-2xl font-bold text-white print:text-slate-900 mb-1">1,084 <span className="text-sm font-normal text-slate-300 print:text-slate-500">kWh</span></div>
            <div className="text-xs text-emerald-500 font-medium">91.2% Renewable</div>
          </div>
          <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800 print:bg-slate-50 print:border-slate-200">
            <div className="text-xs text-slate-400 mb-2 print:text-slate-500">Operating Cost</div>
            <div className="text-2xl font-bold text-emerald-400 print:text-emerald-600 mb-1">₹85,197</div>
            <div className="text-xs text-emerald-500 font-medium">Saved ₹1,610</div>
          </div>
          <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800 print:bg-slate-50 print:border-slate-200">
            <div className="text-xs text-slate-400 mb-2 print:text-slate-500">Diesel Displaced</div>
            <div className="text-2xl font-bold text-amber-500 print:text-amber-600 mb-1">39.0 <span className="text-sm font-normal text-amber-500/70">Litres</span></div>
            <div className="text-xs text-slate-500 font-medium">43% reduction</div>
          </div>
          <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800 print:bg-slate-50 print:border-slate-200">
            <div className="text-xs text-slate-400 mb-2 print:text-slate-500">CO₂ Abated</div>
            <div className="text-2xl font-bold text-cyan-400 print:text-cyan-600 mb-1">105 <span className="text-sm font-normal text-cyan-400/70">kg</span></div>
            <div className="text-xs text-emerald-500 font-medium">100% clinic uptime</div>
          </div>
        </div>

        {/* Data Table */}
        <div className="mb-10">
          <h3 className="text-xs font-bold tracking-widest text-white uppercase mb-4 print:text-slate-900">Subsystem Dispatch Performance</h3>
          <div className="overflow-hidden rounded-lg border border-slate-800 print:border-slate-300">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-slate-400 uppercase bg-slate-900/50 border-b border-slate-800 print:bg-slate-100 print:text-slate-500 print:border-slate-300">
                <tr>
                  <th className="px-6 py-4 font-medium">Asset</th>
                  <th className="px-6 py-4 font-medium">Capacity</th>
                  <th className="px-6 py-4 font-medium">Energy Delivered</th>
                  <th className="px-6 py-4 font-medium">Capacity Factor</th>
                  <th className="px-6 py-4 font-medium">Availability</th>
                  <th className="px-6 py-4 font-medium text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 print:divide-slate-200 bg-transparent text-slate-300 print:text-slate-700">
                <tr>
                  <td className="px-6 py-4 font-medium text-white print:text-slate-900">Central Solar PV</td>
                  <td className="px-6 py-4">250 kW</td>
                  <td className="px-6 py-4">684 kWh</td>
                  <td className="px-6 py-4">22.4%</td>
                  <td className="px-6 py-4 text-emerald-500 font-medium">100%</td>
                  <td className="px-6 py-4 text-right text-cyan-400 print:text-cyan-600">Nominal</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 font-medium text-white print:text-slate-900">Wind Turbine</td>
                  <td className="px-6 py-4">100 kW</td>
                  <td className="px-6 py-4">248 kWh</td>
                  <td className="px-6 py-4">31.2%</td>
                  <td className="px-6 py-4 text-emerald-500 font-medium">98.5%</td>
                  <td className="px-6 py-4 text-right text-cyan-400 print:text-cyan-600">Nominal</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 font-medium text-white print:text-slate-900">BESS Storage</td>
                  <td className="px-6 py-4">500 kWh</td>
                  <td className="px-6 py-4">342 kWh cycled</td>
                  <td className="px-6 py-4">91.8% η</td>
                  <td className="px-6 py-4 text-emerald-500 font-medium">100%</td>
                  <td className="px-6 py-4 text-right text-cyan-400 print:text-cyan-600">Healthy</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 font-medium text-white print:text-slate-900">Diesel Genset</td>
                  <td className="px-6 py-4">150 kW</td>
                  <td className="px-6 py-4 text-slate-400 print:text-slate-500">152 kWh (Peaking)</td>
                  <td className="px-6 py-4">14.1%</td>
                  <td className="px-6 py-4 text-emerald-500 font-medium">99.1%</td>
                  <td className="px-6 py-4 text-right text-amber-500 font-medium">Standby</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Observations Footer */}
        <div className="bg-slate-900/30 p-6 rounded-lg border border-slate-800 print:bg-transparent print:border-slate-300">
          <h4 className="text-sm font-bold text-white mb-2 print:text-slate-900">Auditor & System Observations:</h4>
          <p className="text-sm text-slate-400 leading-relaxed print:text-slate-700">
            The automated linear programming dispatch solver maintained zero unserved energy throughout the reporting period. Battery reserve was strictly preserved above the 20% security threshold, safeguarding critical healthcare loads during the evening peak. Diesel generator engagement was successfully delayed until 19:40, resulting in a 43% absolute reduction in fuel burn compared to standard heuristic dispatch logic.
          </p>
        </div>

      </div>
    </div>
  );
}
