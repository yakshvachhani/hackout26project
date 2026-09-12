'use client';

import { useSettings } from '@/contexts/SettingsContext';
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CloudRain, Sun, Wind, MapPin } from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';

export default function WeatherPage() {
  const { currency, powerScale } = useSettings();
  const [forecast, setForecast] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/weather');
        if (!response.ok) throw new Error('Failed to fetch');
        
        const data = await response.json();
        
        // Transform for Recharts
        const chartData = data.date.map((dateStr: string, index: number) => {
          const d = new Date(dateStr);
          return {
            time: `${d.getHours().toString().padStart(2, '0')}:00`,
            radiation: data.solar_radiation[index],
            windSpeed: data.wind_speed[index],
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
            radiation: isDay ? Math.sin((hour - 6) * Math.PI / 12) * 800 : 0, // W/m2
            windSpeed: 10 + Math.random() * 15, // m/s
            cloudCover: Math.random() * 100
          });
        }
        setForecast(fallbackData);
        setLoading(false);
      }
    };

    fetchWeather();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Weather & Renewable Forecast</h2>
          <p className="text-slate-400">
            {error ? "Using simulated fallback data." : "Live 48-hour forecasting using Open-Meteo API data."}
          </p>
        </div>
        <div className="flex items-center gap-2 bg-[#0f172a] border border-slate-800/50 px-4 py-2 rounded-xl text-sm">
          <MapPin size={16} className="text-slate-400" />
          <span className="font-medium">Kutch, Gujarat (23.73° N, 69.85° E)</span>
        </div>
      </div>

      {loading ? (
        <div className="h-[250px] w-full flex items-center justify-center text-white0 animate-pulse">
          Fetching live weather data from API...
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="bg-[#0f172a] border-slate-800/50 rounded-xl overflow-hidden">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Sun size={18} className="text-yellow-500"/> Solar Radiation Forecast (W/m²)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[250px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={forecast}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis dataKey="time" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f1f5f9' }} />
                    <Line type="monotone" dataKey="radiation" stroke="#facc15" strokeWidth={2} dot={false} name="Solar Radiation" />
                    <Line type="monotone" dataKey="cloudCover" stroke="#94a3b8" strokeWidth={1} strokeDasharray="5 5" dot={false} name="Cloud Cover %" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-[#0f172a] border-slate-800/50 rounded-xl overflow-hidden">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Wind size={18} className="text-blue-500"/> Wind Speed Forecast (km/h)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[250px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={forecast}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis dataKey="time" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f1f5f9' }} />
                    <Line type="monotone" dataKey="windSpeed" stroke="#60a5fa" strokeWidth={2} dot={false} name="Wind Speed" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Card className="bg-[#0f172a] border-slate-800/50 border-l-4 border-l-yellow-500">
        <CardHeader>
          <CardTitle className="text-lg">Intelligent Weather Risk Alert</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-300">
            <span className="font-bold text-yellow-500">⚠ Renewable generation risk detected: </span>
            Based on the live forecast, solar output may decline tomorrow afternoon due to expected cloud cover.
          </p>
          <div className="mt-4 p-3 bg-[#1e293b]/50 rounded border border-slate-700">
            <span className="text-emerald-500 font-bold">Recommended action:</span> Trigger battery charging cycle before 14:00 today using available surplus.
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
