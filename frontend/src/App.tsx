import { useState } from 'react';
import { Activity, LayoutDashboard, SlidersHorizontal } from 'lucide-react';
import Dashboard from './components/Dashboard';
import Simulator from './components/Simulator';
import { cn } from './lib/utils';

function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'simulator'>('overview');

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col z-20">
        <div className="p-6 flex items-center gap-3 border-b border-slate-800">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-solar to-diesel flex items-center justify-center shadow-lg shadow-solar/20">
            <Activity className="w-5 h-5 text-slate-950" />
          </div>
          <h1 className="font-bold text-lg tracking-tight text-slate-100">Microgrid AI</h1>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          <button
            onClick={() => setActiveTab('overview')}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors",
              activeTab === 'overview' 
                ? "bg-slate-800 text-white shadow-sm border border-slate-700" 
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent"
            )}
          >
            <LayoutDashboard className="w-4 h-4" />
            Overview
          </button>
          <button
            onClick={() => setActiveTab('simulator')}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors",
              activeTab === 'simulator' 
                ? "bg-slate-800 text-white shadow-sm border border-slate-700" 
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent"
            )}
          >
            <SlidersHorizontal className="w-4 h-4" />
            Simulator
          </button>
        </nav>
        
        <div className="p-4 border-t border-slate-800 text-xs text-slate-500 flex justify-between items-center">
          <span>System Status:</span>
          <span className="text-battery font-medium flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-battery animate-pulse"></span>
            Online
          </span>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative bg-slate-950">
        {/* Subtle grid background */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />
        <div className="relative p-8 z-10 min-h-full">
          {activeTab === 'overview' ? <Dashboard /> : <Simulator />}
        </div>
      </main>
    </div>
  );
}

export default App;
