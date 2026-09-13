'use client';

import { useSettings } from '@/contexts/SettingsContext';
import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { AlertTriangle, Battery, CloudRain, ShieldAlert, Zap } from 'lucide-react';

const INITIAL_ALERTS = [
  {
    id: 1,
    type: 'warning',
    status: 'active',
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
    status: 'active',
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
    status: 'active',
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
    status: 'resolved',
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

export default function AlertsPage() {
  const { currency, powerScale } = useSettings();
  const [alerts, setAlerts] = useState(INITIAL_ALERTS);
  const [filter, setFilter] = useState('all');

  React.useEffect(() => {
    // Background simulation: generates a new realistic alert every 12 seconds for the dashboard demo
    const interval = setInterval(() => {
      setAlerts(prev => {
        const templates = [
          { type: 'warning', icon: Battery, title: 'Battery Temperature Alert', description: 'Cell temperature in rack B3 exceeded optimal operational bounds.', action: 'Run cooling diagnostic.', color: 'text-yellow-500', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20' },
          { type: 'critical', icon: Zap, title: 'Transient Voltage Sag', description: 'Voltage sag of 4.2% detected on primary healthcare feeder.', action: 'Isolate non-critical loads.', color: 'text-red-500', bg: 'bg-red-500/10', border: 'border-red-500/20' },
          { type: 'info', icon: CloudRain, title: 'Forecast Anomaly', description: 'Updated satellite imagery indicates heavy cloud cover incoming earlier than predicted.', action: 'AI adjusting dispatch strategy.', color: 'text-emerald-500', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
          { type: 'warning', icon: ShieldAlert, title: 'Generator Maintenance Warning', description: 'Diesel Genset #1 fuel filter pressure drop detected during standby test.', action: 'Schedule preventative maintenance.', color: 'text-yellow-500', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20' },
        ];
        const template = templates[Math.floor(Math.random() * templates.length)];
        const newAlert = {
          id: Date.now(),
          status: 'active',
          time: 'Just now',
          ...template
        };
        // Prepend new alert and keep max 15 alerts so the list doesn't grow forever
        return [newAlert, ...prev].slice(0, 15);
      });
    }, 12000); 
    
    return () => clearInterval(interval);
  }, []);

  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'all') return true;
    if (filter === 'resolved') return alert.status === 'resolved';
    if (filter === 'critical') return alert.type === 'critical' && alert.status !== 'resolved';
    if (filter === 'warning') return alert.type === 'warning' && alert.status !== 'resolved';
    return true;
  });

  const handleDismiss = (id: number) => {
    setAlerts(alerts.filter(a => a.id !== id));
  };

  const handleAcknowledge = (id: number) => {
    setAlerts(alerts.map(a => a.id === id ? { ...a, status: 'resolved' } : a));
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Alerts & Events</h2>
        <p className="text-outline">Critical notifications, warnings, and system logs.</p>
      </div>

      <div className="flex items-center gap-4 mb-6">
        <button 
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${filter === 'all' ? 'bg-surface-container text-on-background' : 'text-outline hover:text-on-background'}`}
        >
          All Alerts
        </button>
        <button 
          onClick={() => setFilter('critical')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${filter === 'critical' ? 'bg-surface-container text-on-background' : 'text-outline hover:text-on-background'}`}
        >
          Critical Only
        </button>
        <button 
          onClick={() => setFilter('warning')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${filter === 'warning' ? 'bg-surface-container text-on-background' : 'text-outline hover:text-on-background'}`}
        >
          Warnings
        </button>
        <button 
          onClick={() => setFilter('resolved')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${filter === 'resolved' ? 'bg-surface-container text-on-background' : 'text-outline hover:text-on-background'}`}
        >
          Resolved
        </button>
      </div>

      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <div className="text-outline py-8 text-center bg-surface rounded-xl border border-outline-variant">No alerts found for this filter.</div>
        ) : (
          filteredAlerts.map((alert) => {
            const Icon = alert.icon;
            const isResolved = alert.status === 'resolved';
            return (
              <Card key={alert.id} className={`bg-surface border ${alert.border} ${isResolved ? 'opacity-60' : ''}`}>
                <CardContent className="flex items-start gap-4 p-6">
                  <div className={`p-3 rounded-full ${alert.bg} ${alert.color}`}>
                    <Icon size={24} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className={`font-bold text-lg ${alert.color}`}>
                        {alert.title}
                        {isResolved && <span className="ml-2 text-xs bg-surface-container text-on-surface-variant px-2 py-0.5 rounded-full border border-outline font-normal">Resolved</span>}
                      </h3>
                      <span className="text-xs text-outline">{alert.time}</span>
                    </div>
                    <p className="text-on-surface-variant mt-1">{alert.description}</p>
                    
                    <div className="mt-4 flex items-center justify-between">
                      <div className="text-sm">
                        <span className="text-outline">Recommended Action: </span>
                        <span className="font-medium text-on-surface">{alert.action}</span>
                      </div>
                      <div className="flex gap-2">
                        {alert.type !== 'info' && (
                          <button onClick={() => handleDismiss(alert.id)} className="px-3 py-1 text-xs border border-outline rounded hover:bg-surface-container text-on-surface-variant">
                            Dismiss
                          </button>
                        )}
                        {!isResolved && (
                          <button onClick={() => handleAcknowledge(alert.id)} className={`px-3 py-1 text-xs rounded font-bold ${alert.bg} ${alert.color} border ${alert.border} hover:opacity-80`}>
                            {alert.type === 'info' ? 'View' : 'Acknowledge'}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
}

