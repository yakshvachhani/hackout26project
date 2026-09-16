'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';

export const LOCATIONS = [
  { id: 'dhordo', name: 'Kutch Rural Microgrid (Dhordo, Gujarat)', scale: 1.0 },
  { id: 'spiti', name: 'Spiti Valley Microgrid (Himachal Pradesh)', scale: 0.6 },
  { id: 'sundarbans', name: 'Sundarbans Island Grid (West Bengal)', scale: 1.2 },
  { id: 'mawlynnong', name: 'Mawlynnong Eco-Grid (Meghalaya)', scale: 0.8 },
  { id: 'jaisalmer', name: 'Jaisalmer Desert Hub (Rajasthan)', scale: 1.5 }
];

type Settings = {
  currency: string;
  powerScale: string;
  solarCap: number;
  windCap: number;
  bessCap: number;
  dieselPrice: number;
  rates: Record<string, number>;
  locationId: string;
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
  locationId: 'dhordo',
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
    locationId: 'dhordo',
  });

  useEffect(() => {
    const saved = localStorage.getItem('microgrid_settings');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setSettingsState(prev => ({ ...prev, ...parsed }));
      } catch (e) {}
    }

    // Fetch live exchange rates and live diesel price in parallel
    Promise.all([
      fetch('https://open.er-api.com/v6/latest/USD').then(res => res.json()).catch(() => null),
      fetch('https://www.fueleconomy.gov/ws/rest/fuelprices').then(res => res.text()).catch(() => null)
    ]).then(([ratesData, fuelText]) => {
      let newRates = { '$': 1, '₹': 83.5, '€': 0.92, '£': 0.79 };
      if (ratesData && ratesData.rates) {
        newRates = {
          '$': 1,
          '₹': ratesData.rates.INR || 83.5,
          '€': ratesData.rates.EUR || 0.92,
          '£': ratesData.rates.GBP || 0.79
        };
      }

      let fetchedPriceUSDPerLiter: number | null = null;
      if (fuelText) {
        try {
          const parser = new DOMParser();
          const xmlDoc = parser.parseFromString(fuelText, "text/xml");
          const dieselNode = xmlDoc.getElementsByTagName("diesel")[0];
          if (dieselNode && dieselNode.textContent) {
             fetchedPriceUSDPerLiter = parseFloat(dieselNode.textContent) / 3.78541;
          }
        } catch(e) {}
      }

      setSettingsState(prev => {
        const nextState = { ...prev, rates: newRates };
        // If they didn't explicitly save a custom diesel price in local storage, use live price
        const saved = localStorage.getItem('microgrid_settings');
        const hasSavedDiesel = saved && JSON.parse(saved).dieselPrice;
        
        if (!hasSavedDiesel && fetchedPriceUSDPerLiter !== null) {
          const currentRate = newRates[nextState.currency] || 1;
          nextState.dieselPrice = Number((fetchedPriceUSDPerLiter * currentRate).toFixed(2));
        }
        
        return nextState;
      });
    });
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
        dieselPrice: next.dieselPrice,
        locationId: next.locationId
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

    return `${settings.currency}${converted.toLocaleString('en-IN', { maximumFractionDigits: decimals, minimumFractionDigits: decimals })}`;
  };

  const formatPower = (baseValueKW: number, decimals = 1) => {
    if (settings.powerScale === 'MW') {
      return `${(baseValueKW / 1000).toLocaleString('en-IN', { maximumFractionDigits: decimals })} MW`;
    }
    return `${baseValueKW.toLocaleString('en-IN', { maximumFractionDigits: 0 })} kW`;
  };

  return (
    <SettingsContext.Provider value={{ ...settings, setSettings, formatCurrency, formatPower }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => useContext(SettingsContext);
