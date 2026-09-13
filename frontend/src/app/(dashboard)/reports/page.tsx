'use client';

import { useSettings } from '@/contexts/SettingsContext';
import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { FileText, Download, Activity } from 'lucide-react';

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
  const { currency, powerScale, formatCurrency, formatPower } = useSettings();
  const [activeTab, setActiveTab] = useState<TabKey>('daily');

  const activeData = REPORT_DATA[activeTab];

  const exportCSV = () => {
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Asset,Capacity,Energy Delivered,Capacity Factor,Availability,Status\n";
    
    activeData.table.forEach(row => {
      // Clean up text if needed and join with commas
      const rowString = `${row.asset},${row.cap.includes("{powerScale}") ? row.cap.replace(/([\d,.-]+)\s*\{powerScale\}/g, (m, num) => formatPower(parseFloat(num.replace(/,/g,'')))) : row.cap},${row.energy},${row.cf},${row.avail},${row.status}`;
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
            <h2 className="text-2xl font-bold tracking-tight text-on-surface">Executive Energy & ESG Reports</h2>
            <span className="px-2 py-1 bg-emerald-500/20 text-emerald-500 text-[10px] font-bold rounded uppercase tracking-wider border border-emerald-500/30">
              Audit Compliant
            </span>
          </div>
          <p className="text-outline mt-1 text-sm">Automated operational dispatch summaries, financial fuel audits, and sustainability reporting</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={exportPDF} className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-on-surface rounded-xl font-medium text-sm transition-colors shadow-lg shadow-emerald-900/20">
            <Download size={16} /> Export PDF
          </button>
          <button onClick={exportCSV} className="flex items-center gap-2 px-4 py-2 bg-surface-container hover:bg-slate-700 text-on-surface border border-outline rounded-xl font-medium text-sm transition-colors">
            <FileText size={16} /> Export CSV
          </button>
        </div>
      </div>

      {/* Tabs Menu - Hidden during PDF print */}
      <div className="flex gap-6 border-b border-outline-variant pb-2 print:hidden overflow-x-auto">
        {(Object.keys(REPORT_DATA) as TabKey[]).map((key) => (
          <button 
            key={key}
            onClick={() => setActiveTab(key)}
            className={`text-sm font-bold pb-2 whitespace-nowrap transition-colors ${
              activeTab === key 
                ? "text-on-surface border-b-2 border-emerald-500" 
                : "text-outline hover:text-on-surface border-b-2 border-transparent"
            }`}
          >
            {REPORT_DATA[key].label}
          </button>
        ))}
      </div>

      {/* Printable Report Document */}
      <div className="bg-surface rounded-xl border border-outline-variant shadow-2xl relative overflow-hidden print:bg-white print:text-black print:border-none print:shadow-none print:m-0 print:p-0">
        
        {/* Subtle Watermark (Visible on screen and print) */}
        <div className="absolute inset-0 pointer-events-none flex items-center justify-center opacity-[0.03] print:opacity-[0.05]">
          <Activity size={400} className="text-on-surface print:text-black" />
        </div>

        {/* Official Header Strip */}
        <div className="h-2 w-full bg-emerald-500 print:bg-emerald-700"></div>

        <div className="p-8 md:p-12 relative z-10">
          {/* Document Header */}
          <div className="flex flex-col md:flex-row justify-between items-start border-b-2 border-outline-variant pb-8 mb-8 print:border-slate-300">
            <div className="flex gap-4 items-start">
              <div className="p-3 bg-emerald-500/10 rounded-lg border border-emerald-500/20 print:bg-transparent print:border-slate-300">
                <Activity size={32} className="text-emerald-500 print:text-emerald-700" />
              </div>
              <div>
                <div className="text-[10px] font-bold tracking-widest text-emerald-500 uppercase mb-1 print:text-emerald-700">Gridwise Microgrid Intelligence System</div>
                <h1 className="text-3xl font-extrabold text-on-surface mb-2 print:text-black tracking-tight">{activeData.title}</h1>
                <p className="text-sm font-medium text-outline print:text-slate-600">Facility: Kutch Rural Microgrid (Dhordo, Gujarat)</p>
              </div>
            </div>
            
            <div className="mt-6 md:mt-0 text-left md:text-right flex flex-col justify-end h-full">
              <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs mb-3">
                <span className="text-outline print:text-slate-500 text-right">Report Ref:</span>
                <span className="font-mono text-on-surface print:text-black font-bold">{activeData.ref}</span>
                <span className="text-outline print:text-slate-500 text-right">Generated:</span>
                <span className="font-mono text-on-surface print:text-black font-bold">12 Sep 2026</span>
                <span className="text-outline print:text-slate-500 text-right">Status:</span>
                <span className="font-mono text-emerald-500 print:text-emerald-700 font-bold">VERIFIED</span>
              </div>
            </div>
          </div>

          {/* KPI Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
            <div className="bg-surface-container/50 p-5 rounded-xl border border-outline-variant/50 print:bg-slate-50 print:border-slate-200">
              <div className="text-xs font-semibold text-outline uppercase tracking-wider mb-2 print:text-slate-500">Total Generation</div>
              <div className="text-3xl font-black text-on-surface print:text-black mb-1">{activeData.generation} <span className="text-base font-normal text-on-surface-variant print:text-slate-500">kWh</span></div>
              <div className="text-xs text-emerald-500 font-bold">91.2% Renewable</div>
            </div>
            <div className="bg-surface-container/50 p-5 rounded-xl border border-outline-variant/50 print:bg-slate-50 print:border-slate-200">
              <div className="text-xs font-semibold text-outline uppercase tracking-wider mb-2 print:text-slate-500">Operating Cost</div>
              <div className="text-3xl font-black text-emerald-500 print:text-emerald-700 mb-1">{formatCurrency(parseFloat(activeData.cost.replace(/[^0-9.-]+/g,"")))}</div>
              <div className="text-xs text-emerald-500 font-bold">Saved {formatCurrency(parseFloat(activeData.saved.replace(/[^0-9.-]+/g,"")))}</div>
            </div>
            <div className="bg-surface-container/50 p-5 rounded-xl border border-outline-variant/50 print:bg-slate-50 print:border-slate-200">
              <div className="text-xs font-semibold text-outline uppercase tracking-wider mb-2 print:text-slate-500">Diesel Displaced</div>
              <div className="text-3xl font-black text-amber-500 print:text-amber-700 mb-1">{activeData.diesel} <span className="text-base font-normal text-amber-500/70 print:text-slate-500">Litres</span></div>
              <div className="text-xs text-on-surface print:text-slate-700 font-bold">43% reduction</div>
            </div>
            <div className="bg-surface-container/50 p-5 rounded-xl border border-outline-variant/50 print:bg-slate-50 print:border-slate-200">
              <div className="text-xs font-semibold text-outline uppercase tracking-wider mb-2 print:text-slate-500">CO₂ Abated</div>
              <div className="text-3xl font-black text-cyan-400 print:text-cyan-700 mb-1">{activeData.co2} <span className="text-base font-normal text-cyan-400/70 print:text-slate-500">kg</span></div>
              <div className="text-xs text-emerald-500 font-bold">100% clinic uptime</div>
            </div>
          </div>

          {/* Data Table */}
          <div className="mb-10">
            <h3 className="text-xs font-bold tracking-widest text-on-surface uppercase mb-4 print:text-slate-800 border-b border-outline-variant print:border-slate-300 pb-2">Subsystem Dispatch Performance</h3>
            <div className="overflow-hidden rounded-lg border border-outline-variant print:border-slate-300 print:rounded-none">
              <table className="w-full text-sm text-left">
                <thead className="text-[11px] text-outline uppercase bg-surface-container print:bg-slate-100 print:text-slate-600 border-b border-outline-variant print:border-slate-300 font-bold tracking-wider">
                  <tr>
                    <th className="px-6 py-4">Asset</th>
                    <th className="px-6 py-4">Capacity</th>
                    <th className="px-6 py-4">Energy Delivered</th>
                    <th className="px-6 py-4">Capacity Factor</th>
                    <th className="px-6 py-4">Availability</th>
                    <th className="px-6 py-4 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/50 print:divide-slate-200 bg-background/50 print:bg-white text-on-surface-variant print:text-slate-700">
                  {activeData.table.map((row, idx) => (
                    <tr key={idx} className="hover:bg-surface-container/30 transition-colors print:hover:bg-white">
                      <td className="px-6 py-4 font-bold text-on-surface print:text-black">{row.asset}</td>
                      <td className="px-6 py-4">{row.cap.replace('{powerScale}', powerScale)}</td>
                      <td className="px-6 py-4 text-on-surface print:text-slate-900 font-mono">{row.energy}</td>
                      <td className="px-6 py-4">{row.cf}</td>
                      <td className="px-6 py-4 text-emerald-500 print:text-emerald-700 font-bold">{row.avail}</td>
                      <td className={`px-6 py-4 text-right font-bold ${row.statusColor.replace('print:text-cyan-600', 'print:text-cyan-800').replace('print:text-emerald-600', 'print:text-emerald-800')}`}>{row.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Observations & Signatures */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-6 border-t-2 border-outline-variant print:border-slate-300">
            <div className="md:col-span-2">
              <h4 className="text-xs font-bold tracking-widest text-on-surface uppercase mb-3 print:text-slate-800">Auditor & System Observations</h4>
              <p className="text-sm text-outline print:text-slate-600 leading-relaxed text-justify">
                {activeData.observations}
              </p>
            </div>
            
            <div className="md:col-span-1 flex flex-col justify-end space-y-6">
              <div className="border-b border-outline print:border-slate-400 pb-2">
                <span className="text-[10px] text-outline print:text-slate-500 uppercase tracking-wider font-bold">Authorized By</span>
                <div className="font-signature text-2xl mt-4 text-on-surface print:text-black opacity-80" style={{ fontFamily: "'Dancing Script', cursive, serif" }}>Gridwise AI Auditor</div>
              </div>
              <div className="border-b border-outline print:border-slate-400 pb-2">
                <span className="text-[10px] text-outline print:text-slate-500 uppercase tracking-wider font-bold">Timestamp & Hash</span>
                <div className="font-mono text-[10px] mt-2 text-on-surface-variant print:text-slate-500 break-all">
                  0x7A9B...4F21 (Immutable Ledger Record)
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

