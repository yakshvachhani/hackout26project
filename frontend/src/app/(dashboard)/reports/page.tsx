'use client';

import { useSettings } from '@/contexts/SettingsContext';
import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { FileText, Download } from 'lucide-react';

const REPORT_DATA = {
  daily: {
    id: 'daily',
    label: "Daily Operational Log",
    title: "Daily Operational & Dispatch Audit Log",
    ref: "#GW-2026-09",
    generation: "1,084",
    cost: "{currency}85,197",
    saved: "{currency}1,610",
    diesel: "39.0",
    co2: "105",
    observations: "The automated linear programming dispatch solver maintained zero unserved energy throughout the reporting period. Battery reserve was strictly preserved above the 20% security threshold, safeguarding critical healthcare loads during the evening peak. Diesel generator engagement was successfully delayed until 19:40, resulting in a 43% absolute reduction in fuel burn compared to standard heuristic dispatch logic.",
    table: [
      { asset: "Central Solar PV", cap: "250 {powerScale}", energy: "684 kWh", cf: "22.4%", avail: "100%", status: "Nominal", statusColor: "text-cyan-400 print:text-cyan-600" },
      { asset: "Wind Turbine", cap: "100 {powerScale}", energy: "248 kWh", cf: "31.2%", avail: "98.5%", status: "Nominal", statusColor: "text-cyan-400 print:text-cyan-600" },
      { asset: "BESS Storage", cap: "500 kWh", energy: "342 kWh cycled", cf: "91.8% η", avail: "100%", status: "Healthy", statusColor: "text-cyan-400 print:text-cyan-600" },
      { asset: "Diesel Genset", cap: "150 {powerScale}", energy: "152 kWh (Peaking)", cf: "14.1%", avail: "99.1%", status: "Standby", statusColor: "text-amber-500 font-medium" }
    ]
  },
  weekly: {
    id: 'weekly',
    label: "Weekly Dispatch Summary",
    title: "Weekly Dispatch & Performance Summary",
    ref: "#GW-2026-W37",
    generation: "7,854",
    cost: "{currency}584,200",
    saved: "{currency}12,450",
    diesel: "275.5",
    co2: "740",
    observations: "Weekly solar irradiance was 12% above the seasonal average, allowing the BESS to cycle efficiently and absorb excess daytime generation. Wind patterns remained stable, contributing to a solid 34% capacity factor over the 7-day period. Grid stability was maintained with 100% uptime.",
    table: [
      { asset: "Central Solar PV", cap: "250 {powerScale}", energy: "4,980 kWh", cf: "24.1%", avail: "99.8%", status: "Nominal", statusColor: "text-cyan-400 print:text-cyan-600" },
      { asset: "Wind Turbine", cap: "100 {powerScale}", energy: "1,850 kWh", cf: "34.0%", avail: "97.2%", status: "Maintenance Req", statusColor: "text-amber-500 font-medium" },
      { asset: "BESS Storage", cap: "500 kWh", energy: "2,410 kWh cycled", cf: "91.5% η", avail: "100%", status: "Healthy", statusColor: "text-cyan-400 print:text-cyan-600" },
      { asset: "Diesel Genset", cap: "150 {powerScale}", energy: "1,024 kWh", cf: "12.5%", avail: "99.0%", status: "Nominal", statusColor: "text-cyan-400 print:text-cyan-600" }
    ]
  },
  monthly: {
    id: 'monthly',
    label: "Monthly Financial Audit",
    title: "Monthly Financial & Efficiency Audit",
    ref: "#GW-2026-M09",
    generation: "32,850",
    cost: "{currency}2,540,100",
    saved: "{currency}54,200",
    diesel: "1,150",
    co2: "3,200",
    observations: "Financial audit indicates a 15% reduction in Levelized Cost of Energy (LCOE) compared to the baseline projection. Optimization algorithms successfully shifted 85% of non-critical pumping loads to high-solar-yield hours, maximizing free renewable energy and minimizing diesel reliance.",
    table: [
      { asset: "Central Solar PV", cap: "250 {powerScale}", energy: "21,500 kWh", cf: "23.8%", avail: "99.5%", status: "Nominal", statusColor: "text-cyan-400 print:text-cyan-600" },
      { asset: "Wind Turbine", cap: "100 {powerScale}", energy: "7,200 kWh", cf: "30.0%", avail: "95.5%", status: "Repaired", statusColor: "text-emerald-500 print:text-emerald-600" },
      { asset: "BESS Storage", cap: "500 kWh", energy: "10,200 kWh cycled", cf: "91.2% η", avail: "100%", status: "Healthy", statusColor: "text-cyan-400 print:text-cyan-600" },
      { asset: "Diesel Genset", cap: "150 {powerScale}", energy: "4,150 kWh", cf: "15.0%", avail: "98.5%", status: "Nominal", statusColor: "text-cyan-400 print:text-cyan-600" }
    ]
  },
  annual: {
    id: 'annual',
    label: "Annual ESG & Carbon Report",
    title: "Annual ESG & Carbon Abatement Report",
    ref: "#GW-2026-YTD",
    generation: "394,200",
    cost: "{currency}30,481,200",
    saved: "{currency}650,400",
    diesel: "14,050",
    co2: "38,500",
    observations: "Total carbon abated aligns perfectly with corporate ESG sustainability goals. The microgrid has achieved a 91.5% renewable penetration rate YTD. Diesel displacement resulted in the prevention of 38.5 metric tons of CO2 emissions, fully qualifying the site for Tier-1 Carbon Credits under the national registry.",
    table: [
      { asset: "Central Solar PV", cap: "250 {powerScale}", energy: "265,000 kWh", cf: "24.5%", avail: "99.1%", status: "Nominal", statusColor: "text-cyan-400 print:text-cyan-600" },
      { asset: "Wind Turbine", cap: "100 {powerScale}", energy: "85,200 kWh", cf: "31.5%", avail: "94.2%", status: "Scheduled Maint", statusColor: "text-amber-500 font-medium" },
      { asset: "BESS Storage", cap: "500 kWh", energy: "125,000 kWh cycled", cf: "90.8% η", avail: "99.9%", status: "Degradation 2%", statusColor: "text-amber-500 font-medium" },
      { asset: "Diesel Genset", cap: "150 {powerScale}", energy: "44,000 kWh", cf: "14.2%", avail: "98.0%", status: "Nominal", statusColor: "text-cyan-400 print:text-cyan-600" }
    ]
  }
};

type TabKey = keyof typeof REPORT_DATA;

export default function ReportsPage() {
  const { currency, powerScale } = useSettings();
  const [activeTab, setActiveTab] = useState<TabKey>('daily');

  const activeData = REPORT_DATA[activeTab];

  const exportCSV = () => {
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Asset,Capacity,Energy Delivered,Capacity Factor,Availability,Status\n";
    
    activeData.table.forEach(row => {
      // Clean up text if needed and join with commas
      const rowString = `${row.asset},${row.cap.replace(/\{powerScale\}/g, powerScale)},${row.energy},${row.cf},${row.avail},${row.status}`;
      csvContent += rowString + "\n";
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `${activeTab}_report_${activeData.ref}.csv`.replace('#', ''));
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
            <span className="px-2 py-1 bg-emerald-500/20 text-emerald-500 text-[10px] font-bold rounded uppercase tracking-wider border border-emerald-500/30">
              Audit Compliant
            </span>
          </div>
          <p className="text-slate-400 mt-1 text-sm">Automated operational dispatch summaries, financial fuel audits, and sustainability reporting</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={exportPDF} className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-medium text-sm transition-colors shadow-lg shadow-emerald-900/20">
            <Download size={16} /> Export PDF
          </button>
          <button onClick={exportCSV} className="flex items-center gap-2 px-4 py-2 bg-[#1e293b]/50 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl font-medium text-sm transition-colors">
            <FileText size={16} /> Export CSV
          </button>
        </div>
      </div>

      {/* Tabs Menu - Hidden during PDF print */}
      <div className="flex gap-6 border-b border-slate-800/50 pb-2 print:hidden overflow-x-auto">
        {(Object.keys(REPORT_DATA) as TabKey[]).map((key) => (
          <button 
            key={key}
            onClick={() => setActiveTab(key)}
            className={`text-sm font-bold pb-2 whitespace-nowrap transition-colors ${
              activeTab === key 
                ? "text-white border-b-2 border-emerald-500" 
                : "text-slate-400 hover:text-slate-200 border-b-2 border-transparent"
            }`}
          >
            {REPORT_DATA[key].label}
          </button>
        ))}
      </div>

      {/* Printable Report Document */}
      <div className="bg-[#0f172a] rounded-xl border border-slate-800/50 p-8 shadow-2xl relative print:bg-[#0f172a] print:text-black print:border-none print:shadow-none print:p-0">
        
        {/* Document Header */}
        <div className="flex justify-between items-start mb-10">
          <div>
            <div className="text-[10px] font-bold tracking-widest text-emerald-500 uppercase mb-2">Gridwise Microgrid Intelligence System</div>
            <h1 className="text-2xl font-bold text-white mb-1 print:text-white">{activeData.title}</h1>
            <p className="text-sm text-slate-400 print:text-slate-300">Facility: Kutch Rural Microgrid (Dhordo, Gujarat)</p>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-400 mb-1 print:text-white0">Report Ref: {activeData.ref}</div>
            <div className="text-xs text-slate-400 mb-2 print:text-white0">Generated: 12 September 2026</div>
            <div className="inline-block px-2 py-0.5 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold uppercase tracking-wider rounded border border-emerald-500/20">
              Verified
            </div>
          </div>
        </div>

        {/* KPI Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
          <div className="bg-[#0f172a]/50 p-4 rounded-xl border border-slate-800/50 print:bg-[#1e293b]/50 print:border-slate-800/50">
            <div className="text-xs text-slate-400 mb-2 print:text-white0">Total Generation</div>
            <div className="text-2xl font-bold text-white print:text-white mb-1">{activeData.generation} <span className="text-sm font-normal text-slate-300 print:text-white0">kWh</span></div>
            <div className="text-xs text-emerald-500 font-medium">91.2% Renewable</div>
          </div>
          <div className="bg-[#0f172a]/50 p-4 rounded-xl border border-slate-800/50 print:bg-[#1e293b]/50 print:border-slate-800/50">
            <div className="text-xs text-slate-400 mb-2 print:text-white0">Operating Cost</div>
            <div className="text-2xl font-bold text-emerald-500 print:text-emerald-600 mb-1">{activeData.cost.replace(/\{currency\}/g, currency)}</div>
            <div className="text-xs text-emerald-500 font-medium">Saved {activeData.saved.replace(/\{currency\}/g, currency)}</div>
          </div>
          <div className="bg-[#0f172a]/50 p-4 rounded-xl border border-slate-800/50 print:bg-[#1e293b]/50 print:border-slate-800/50">
            <div className="text-xs text-slate-400 mb-2 print:text-white0">Diesel Displaced</div>
            <div className="text-2xl font-bold text-amber-500 print:text-amber-600 mb-1">{activeData.diesel} <span className="text-sm font-normal text-amber-500/70">Litres</span></div>
            <div className="text-xs text-white0 font-medium">43% reduction</div>
          </div>
          <div className="bg-[#0f172a]/50 p-4 rounded-xl border border-slate-800/50 print:bg-[#1e293b]/50 print:border-slate-800/50">
            <div className="text-xs text-slate-400 mb-2 print:text-white0">CO₂ Abated</div>
            <div className="text-2xl font-bold text-cyan-400 print:text-cyan-600 mb-1">{activeData.co2} <span className="text-sm font-normal text-cyan-400/70">kg</span></div>
            <div className="text-xs text-emerald-500 font-medium">100% clinic uptime</div>
          </div>
        </div>

        {/* Data Table */}
        <div className="mb-10">
          <h3 className="text-xs font-bold tracking-widest text-white uppercase mb-4 print:text-white">Subsystem Dispatch Performance</h3>
          <div className="overflow-hidden rounded-xl border border-slate-800/50 print:border-slate-700">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-slate-400 uppercase bg-[#0f172a]/50 border-b border-slate-800/50 print:bg-[#1e293b] print:text-white0 print:border-slate-700">
                <tr>
                  <th className="px-6 py-4 font-medium">Asset</th>
                  <th className="px-6 py-4 font-medium">Capacity</th>
                  <th className="px-6 py-4 font-medium">Energy Delivered</th>
                  <th className="px-6 py-4 font-medium">Capacity Factor</th>
                  <th className="px-6 py-4 font-medium">Availability</th>
                  <th className="px-6 py-4 font-medium text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 print:divide-slate-200 bg-slate-950 text-slate-300 print:text-slate-300">
                {activeData.table.map((row, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 font-medium text-white print:text-white">{row.asset}</td>
                    <td className="px-6 py-4">{row.cap}</td>
                    <td className="px-6 py-4 text-slate-300 print:text-slate-300">{row.energy}</td>
                    <td className="px-6 py-4">{row.cf}</td>
                    <td className="px-6 py-4 text-emerald-500 font-medium">{row.avail}</td>
                    <td className={`px-6 py-4 text-right ${row.statusColor}`}>{row.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Observations Footer */}
        <div className="bg-[#0f172a]/30 p-6 rounded-xl border border-slate-800/50 print:bg-slate-950 print:border-slate-700">
          <h4 className="text-sm font-bold text-white mb-2 print:text-white">Auditor & System Observations:</h4>
          <p className="text-sm text-slate-400 leading-relaxed print:text-slate-300">
            {activeData.observations}
          </p>
        </div>

      </div>
    </div>
  );
}
