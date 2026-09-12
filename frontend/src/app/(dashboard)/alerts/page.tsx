import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, Battery, CloudRain, ShieldAlert, Zap } from 'lucide-react';

export default function AlertsPage() {
  const alerts = [
    {
      id: 1,
      type: 'warning',
      icon: CloudRain,
      title: 'Renewable generation risk detected',
      time: '10 mins ago',
      description: 'Solar output may decline by 38% tomorrow afternoon due to forecast cloud cover.',
      action: 'Charge battery to ≥80% before 14:00 today.',
      color: 'text-yellow-500',
      bg: 'bg-yellow-500/10',
      border: 'border-yellow-500/20'
    },
    {
      id: 2,
      type: 'critical',
      icon: ShieldAlert,
      title: 'Diesel Generator Engaged',
      time: '2 hours ago',
      description: 'Diesel backup was activated due to unexpected load spike exceeding solar and battery discharge limits.',
      action: 'Acknowledge event. Investigate load anomaly.',
      color: 'text-red-500',
      bg: 'bg-red-500/10',
      border: 'border-red-500/20'
    },
    {
      id: 3,
      type: 'info',
      icon: Zap,
      title: 'Optimization Complete',
      time: '4 hours ago',
      description: 'New optimal dispatch strategy generated for the next 48 hours.',
      action: 'View Strategy',
      color: 'text-emerald-500',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/20'
    },
    {
      id: 4,
      type: 'warning',
      icon: Battery,
      title: 'Low Battery Reserve',
      time: '1 day ago',
      description: 'Battery state of charge fell to 22%, approaching the 20% minimum reserve threshold.',
      action: 'Resolved automatically by shedding non-critical load.',
      color: 'text-yellow-500',
      bg: 'bg-yellow-500/10',
      border: 'border-yellow-500/20'
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Alerts & Events</h2>
        <p className="text-slate-400">Critical notifications, warnings, and system logs.</p>
      </div>

      <div className="flex items-center gap-4 mb-6">
        <button className="px-4 py-2 bg-slate-800 text-slate-100 rounded-md text-sm font-medium hover:bg-slate-700">All Alerts</button>
        <button className="px-4 py-2 text-slate-400 hover:text-slate-100 rounded-md text-sm font-medium">Critical Only</button>
        <button className="px-4 py-2 text-slate-400 hover:text-slate-100 rounded-md text-sm font-medium">Warnings</button>
        <button className="px-4 py-2 text-slate-400 hover:text-slate-100 rounded-md text-sm font-medium">Resolved</button>
      </div>

      <div className="space-y-4">
        {alerts.map((alert) => {
          const Icon = alert.icon;
          return (
            <Card key={alert.id} className={`bg-slate-900 border ${alert.border}`}>
              <CardContent className="flex items-start gap-4 p-6">
                <div className={`p-3 rounded-full ${alert.bg} ${alert.color}`}>
                  <Icon size={24} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className={`font-bold text-lg ${alert.color}`}>{alert.title}</h3>
                    <span className="text-xs text-slate-500">{alert.time}</span>
                  </div>
                  <p className="text-slate-300 mt-1">{alert.description}</p>
                  
                  <div className="mt-4 flex items-center justify-between">
                    <div className="text-sm">
                      <span className="text-slate-400">Recommended Action: </span>
                      <span className="font-medium text-slate-200">{alert.action}</span>
                    </div>
                    <div className="flex gap-2">
                      {alert.type !== 'info' && (
                        <button className="px-3 py-1 text-xs border border-slate-700 rounded hover:bg-slate-800 text-slate-300">Dismiss</button>
                      )}
                      <button className={`px-3 py-1 text-xs rounded font-bold ${alert.bg} ${alert.color} border ${alert.border} hover:opacity-80`}>
                        {alert.type === 'info' ? 'View' : 'Acknowledge'}
                      </button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
