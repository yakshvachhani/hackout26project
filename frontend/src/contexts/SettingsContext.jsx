'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';

export const LOCATIONS = [
{ id: 'dhordo', name: 'Kutch Rural Microgrid (Dhordo, Gujarat)', scale: 1.0 },
{ id: 'spiti', name: 'Spiti Valley Microgrid (Himachal Pradesh)', scale: 0.6 },
{ id: 'sundarbans', name: 'Sundarbans Island Grid (West Bengal)', scale: 1.2 },
{ id: 'mawlynnong', name: 'Mawlynnong Eco-Grid (Meghalaya)', scale: 0.8 },
{ id: 'jaisalmer', name: 'Jaisalmer Desert Hub (Rajasthan)', scale: 1.5 }];























const defaultSettings = {
  currency: '₹',
  powerScale: 'kW',
  solarCap: 250,
  windCap: 100,
  bessCap: 500,
  dieselPrice: 92,
  rates: { '$': 1, '₹': 83.5, '€': 0.92, '£': 0.79 },
  locationId: 'dhordo',
  mode: 'LIVE',
  simScenario: 'nominal',
  setMode: () => {},
  setSimScenario: () => {},
  setSettings: () => {},
  formatCurrency: (val) => `₹${val}`,
  formatPower: (val) => `${val} kW`
};

const SettingsContext = createContext(defaultSettings);

export const SettingsProvider = ({ children }) => {
  const [settings, setSettingsState] = useState({
    currency: '₹',
    powerScale: 'kW',
    solarCap: 250,
    windCap: 100,
    bessCap: 500,
    dieselPrice: 92,
    rates: { '$': 1, '₹': 83.5, '€': 0.92, '£': 0.79 },
    locationId: 'dhordo',
    mode: 'LIVE',
    simScenario: 'nominal'
  });

  useEffect(() => {
    const saved = localStorage.getItem('microgrid_settings');
    const savedMode = localStorage.getItem('microgrid_mode');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setSettingsState((prev) => ({
          ...prev,
          ...parsed,
          ...(savedMode ? { mode: savedMode } : {})
        }));
      } catch (e) {}
    } else if (savedMode) {
      setSettingsState((prev) => ({ ...prev, mode: savedMode }));
    }

    // Fetch live exchange rates
    fetch('https://open.er-api.com/v6/latest/USD').
    then((res) => res.json()).
    catch(() => null).
    then((ratesData) => {
      let newRates = { '$': 1, '₹': 83.5, '€': 0.92, '£': 0.79 };
      if (ratesData && ratesData.rates) {
        newRates = {
          '$': 1,
          '₹': ratesData.rates.INR || 83.5,
          '€': ratesData.rates.EUR || 0.92,
          '£': ratesData.rates.GBP || 0.79
        };
      }

      setSettingsState((prev) => {
        return { ...prev, rates: newRates };
      });
    });
  }, []);

  const setMode = (mode) => {
    setSettingsState((prev) => {
      try {
        localStorage.setItem('microgrid_mode', mode);
      } catch (e) {}
      return { ...prev, mode };
    });
  };

  const setSimScenario = (simScenario) => {
    setSettingsState((prev) => ({ ...prev, simScenario }));
  };

  const setSettings = (newSettings) => {
    setSettingsState((prev) => {
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
  const formatCurrency = (baseValueINR, decimals = 0) => {
    const rateINR = settings.rates['₹'] || 83.5;
    const targetRate = settings.rates[settings.currency] || 1;

    // Convert INR -> USD -> Target Currency
    const valueUSD = baseValueINR / rateINR;
    const converted = valueUSD * targetRate;

    return `${settings.currency}${converted.toLocaleString('en-IN', { maximumFractionDigits: decimals, minimumFractionDigits: decimals })}`;
  };

  const formatPower = (baseValueKW, decimals = 1) => {
    if (settings.powerScale === 'MW') {
      return `${(baseValueKW / 1000).toLocaleString('en-IN', { maximumFractionDigits: decimals })} MW`;
    }
    return `${baseValueKW.toLocaleString('en-IN', { maximumFractionDigits: 0 })} kW`;
  };

  return (
    <SettingsContext.Provider value={{ ...settings, setSettings, setMode, setSimScenario, formatCurrency, formatPower }}>
      {children}
    </SettingsContext.Provider>);

};

export const useSettings = () => useContext(SettingsContext);