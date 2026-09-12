'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';

type Settings = {
  currency: string;
  powerScale: string;
  solarCap: number;
  windCap: number;
  bessCap: number;
  dieselPrice: number;
  rates: Record<string, number>;
  setSettings: (settings: Partial<Settings>) => void;
  formatCurrency: (baseValueINR: number, decimals?: number) => string;
  formatPower: (baseValueKW: number, decimals?: number) => string;
};

const defaultSettings: Settings = {
  currency: '₹',
  powerScale: 'kW',
  solarCap: 250,
  windCap: 100,
  bessCap: 500,
  dieselPrice: 92,
  rates: { '$': 1, '₹': 83.5, '€': 0.92, '£': 0.79 },
  setSettings: () => {},
  formatCurrency: (val) => `₹${val}`,
  formatPower: (val) => `${val} kW`,
};

const SettingsContext = createContext<Settings>(defaultSettings);

export const SettingsProvider = ({ children }: { children: React.ReactNode }) => {
  const [settings, setSettingsState] = useState<Omit<Settings, 'setSettings' | 'formatCurrency' | 'formatPower'>>({
    currency: '₹',
    powerScale: 'kW',
    solarCap: 250,
    windCap: 100,
    bessCap: 500,
    dieselPrice: 92,
    rates: { '$': 1, '₹': 83.5, '€': 0.92, '£': 0.79 },
  });

  useEffect(() => {
    const saved = localStorage.getItem('microgrid_settings');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setSettingsState(prev => ({ ...prev, ...parsed }));
      } catch (e) {}
    }

    // Fetch live exchange rates relative to USD (free, no API key required)
    fetch('https://open.er-api.com/v6/latest/USD')
      .then(res => res.json())
      .then(data => {
        if (data && data.rates) {
          setSettingsState(prev => ({
            ...prev,
            rates: {
              '$': 1,
              '₹': data.rates.INR || 83.5,
              '€': data.rates.EUR || 0.92,
              '£': data.rates.GBP || 0.79
            }
          }));
        }
      })
      .catch(err => console.error("Failed to fetch exchange rates", err));
  }, []);

  const setSettings = (newSettings: Partial<Settings>) => {
    setSettingsState(prev => {
      const next = { ...prev, ...newSettings };
      localStorage.setItem('microgrid_settings', JSON.stringify({
        currency: next.currency,
        powerScale: next.powerScale,
        solarCap: next.solarCap,
        windCap: next.windCap,
        bessCap: next.bessCap,
        dieselPrice: next.dieselPrice
      }));
      return next;
    });
  };

  // Base values in the app are hardcoded as INR (₹).
  const formatCurrency = (baseValueINR: number, decimals = 0) => {
    const rateINR = settings.rates['₹'] || 83.5;
    const targetRate = settings.rates[settings.currency] || 1;
    
    // Convert INR -> USD -> Target Currency
    const valueUSD = baseValueINR / rateINR;
    const converted = valueUSD * targetRate;

    return `${settings.currency}${converted.toLocaleString(undefined, { maximumFractionDigits: decimals, minimumFractionDigits: decimals })}`;
  };

  const formatPower = (baseValueKW: number, decimals = 1) => {
    if (settings.powerScale === 'MW') {
      return `${(baseValueKW / 1000).toLocaleString(undefined, { maximumFractionDigits: decimals })} MW`;
    }
    return `${baseValueKW.toLocaleString(undefined, { maximumFractionDigits: 0 })} kW`;
  };

  return (
    <SettingsContext.Provider value={{ ...settings, setSettings, formatCurrency, formatPower }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => useContext(SettingsContext);
