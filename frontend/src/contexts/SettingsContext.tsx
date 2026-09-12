'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';

type Settings = {
  currency: string;
  powerScale: string;
  solarCap: number;
  windCap: number;
  bessCap: number;
  dieselPrice: number;
  setSettings: (settings: Partial<Settings>) => void;
};

const defaultSettings: Settings = {
  currency: '₹',
  powerScale: 'kW',
  solarCap: 250,
  windCap: 100,
  bessCap: 500,
  dieselPrice: 92,
  setSettings: () => {},
};

const SettingsContext = createContext<Settings>(defaultSettings);

export const SettingsProvider = ({ children }: { children: React.ReactNode }) => {
  const [settings, setSettingsState] = useState<Omit<Settings, 'setSettings'>>({
    currency: '₹',
    powerScale: 'kW',
    solarCap: 250,
    windCap: 100,
    bessCap: 500,
    dieselPrice: 92,
  });

  useEffect(() => {
    const saved = localStorage.getItem('microgrid_settings');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setSettingsState(prev => ({ ...prev, ...parsed }));
      } catch (e) {}
    }
  }, []);

  const setSettings = (newSettings: Partial<Settings>) => {
    setSettingsState(prev => {
      const next = { ...prev, ...newSettings };
      localStorage.setItem('microgrid_settings', JSON.stringify(next));
      return next;
    });
  };

  return (
    <SettingsContext.Provider value={{ ...settings, setSettings }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => useContext(SettingsContext);
