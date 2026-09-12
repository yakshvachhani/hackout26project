'use client';

import { useSettings } from '@/contexts/SettingsContext';
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function ForecastPage() {
  const { currency, powerScale } = useSettings();
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Energy Forecasts</h2>
        <p className="text-slate-400">Short and long-term renewable generation forecasting.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-[#0f172a] border-slate-800/50 hover:border-blue-500 transition-colors cursor-pointer">
          <Link href="/weather">
            <CardHeader>
              <CardTitle className="text-blue-400">Weather & Renewables</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-300 mb-4">View 48-hour solar radiation, cloud cover, and wind speed forecasts powered by Open-Meteo.</p>
              <span className="flex items-center text-sm font-bold text-blue-500">Go to Weather Forecasts <ArrowRight size={16} className="ml-1"/></span>
            </CardContent>
          </Link>
        </Card>

        <Card className="bg-[#0f172a] border-slate-800/50 hover:border-emerald-500 transition-colors cursor-pointer">
          <Link href="/demand">
            <CardHeader>
              <CardTitle className="text-emerald-500">Community Load Demand</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-300 mb-4">View predictive community load profiles, split by residential, commercial, and critical infrastructure.</p>
              <span className="flex items-center text-sm font-bold text-emerald-500">Go to Demand Forecasts <ArrowRight size={16} className="ml-1"/></span>
            </CardContent>
          </Link>
        </Card>
      </div>
    </div>
  );
}
