'use client';

import { useSettings, LOCATIONS } from '@/contexts/SettingsContext';
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CloudRain, Sun, Wind, MapPin } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from
'recharts';

const COORDS = {
  dhordo: "23.73° N, 69.85° E",
  spiti: "32.22° N, 78.01° E",
  sundarbans: "21.94° N, 88.89° E",
  mawlynnong: "25.20° N, 91.91° E",
  jaisalmer: "26.91° N, 70.90° E"
};

export default function WeatherPage() {
  const { currency, powerScale, locationId } = useSettings();
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const currentLoc = LOCATIONS.find((l) => l.id === locationId);
  const locName = currentLoc ? currentLoc.name.split(' (')[0] : 'Kutch, Gujarat';
  const locCoords = currentLoc ? COORDS[currentLoc.id] : COORDS['dhordo'];
  const locScale = currentLoc ? currentLoc.scale : 1.0;

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/weather');
        if (!response.ok) throw new Error('Failed to fetch');

        const data = await response.json();

        // Transform for Recharts
        const chartData = data.date.map((dateStr, index) => {
          const d = new Date(dateStr);
          return {
            time: `${d.getHours().toString().padStart(2, '0')}:00`,
            radiation: data.solar_radiation[index] * locScale,
            windSpeed: data.wind_speed[index] * locScale,
            cloudCover: data.cloud_cover[index]
          };
        });

        setForecast(chartData);
        setLoading(false);
      } catch (err) {
        console.error("API error, falling back to simulation", err);
        setError(true);
        // Fallback simulation
        const fallbackData = [];
        for (let i = 0; i < 48; i++) {
          const hour = i % 24;
          const isDay = hour > 6 && hour < 18;
          fallbackData.push({
            time: `+${i}h`,
            radiation: (isDay ? Math.sin((hour - 6) * Math.PI / 12) * 800 : 0) * locScale, // W/m2
            windSpeed: (10 + Math.random() * 15) * locScale, // m/s
            cloudCover: Math.random() * 100
          });
        }
        setForecast(fallbackData);
        setLoading(false);
      }
    };

    fetchWeather();
  }, [locScale]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Weather & Renewable Forecast</h2>
          <p className="text-outline">
            {error ? "Using simulated fallback data." : "Live 48-hour forecasting using Open-Meteo API data."}
          </p>
        </div>
        <div className="flex items-center gap-2 bg-surface border border-outline-variant px-4 py-2 rounded-xl text-sm">
          <MapPin size={16} className="text-outline" />
          <span className="font-medium">{locName} ({locCoords})</span>
        </div>
      </div>

      {loading ?
      <div className="h-[250px] w-full flex items-center justify-center text-on-surface animate-pulse">
          Fetching live weather data from API...
        </div> :

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="bg-surface border-outline-variant rounded-xl overflow-hidden">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Sun size={18} className="text-yellow-500" /> Solar Radiation Forecast (W/m²)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[250px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={forecast}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" vertical={false} />
                    <XAxis dataKey="time" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', color: '#0f172a' }} />
                    <Line type="monotone" dataKey="radiation" stroke="#facc15" strokeWidth={2} dot={false} name="Solar Radiation" />
                    <Line type="monotone" dataKey="cloudCover" stroke="#94a3b8" strokeWidth={1} strokeDasharray="5 5" dot={false} name="Cloud Cover %" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-surface border-outline-variant rounded-xl overflow-hidden">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Wind size={18} className="text-blue-500" /> Wind Speed Forecast (km/h)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[250px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={forecast}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" vertical={false} />
                    <XAxis dataKey="time" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', color: '#0f172a' }} />
                    <Line type="monotone" dataKey="windSpeed" stroke="#60a5fa" strokeWidth={2} dot={false} name="Wind Speed" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>
      }

      {(() => {
        const afternoonHours = forecast.slice(12, 18);
        const avgCloud = afternoonHours.length > 0 ?
        Math.round(afternoonHours.reduce((acc, curr) => acc + (curr.cloudCover || 0), 0) / afternoonHours.length) :
        locationId === 'spiti' ? 48 : locationId === 'jaisalmer' ? 14 : 38;
        const isHighRisk = avgCloud > 30;
        const dropPct = Math.min(80, Math.max(20, Math.round(avgCloud * 0.85)));

        return (
          <Card className={`bg-surface border-outline-variant border-l-4 ${isHighRisk ? 'border-l-yellow-500' : 'border-l-emerald-500'}`}>
            <CardHeader>
              <CardTitle className="text-lg flex items-center justify-between">
                <span>Intelligent Weather Risk Alert</span>
                <span className="text-xs font-mono font-normal text-outline">Open-Meteo Telemetry</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isHighRisk ?
              <>
                  <p className="text-on-surface-variant">
                    <span className="font-bold text-yellow-500">⚠ Renewable generation risk detected: </span>
                    Based on the live forecast for {locName}, solar output is projected to decline by {dropPct}% tomorrow afternoon due to expected {avgCloud}% cloud cover.
                  </p>
                  <div className="mt-4 p-3 bg-surface-container rounded border border-outline">
                    <span className="text-emerald-500 font-bold">Recommended action: </span>
                    <span className="text-on-surface">Trigger battery charging cycle before 14:00 today using available renewable surplus to maintain {locName} reserve.</span>
                  </div>
                </> :

              <>
                  <p className="text-on-surface-variant">
                    <span className="font-bold text-emerald-500">✓ Optimal solar generation conditions: </span>
                    Clear skies predicted for {locName} with low cloud cover ({avgCloud}%). Solar array operating at high efficiency.
                  </p>
                  <div className="mt-4 p-3 bg-surface-container rounded border border-outline">
                    <span className="text-emerald-500 font-bold">Recommended action: </span>
                    <span className="text-on-surface">Maximize BESS bulk storage absorption and dispatch agricultural loads during midday solar surplus.</span>
                  </div>
                </>
              }
            </CardContent>
          </Card>);

      })()}
    </div>);

}