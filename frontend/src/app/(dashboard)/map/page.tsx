'use client';

import { useSettings } from '@/contexts/SettingsContext';
import React from 'react';

export default function MapPage() {
  const { currency, powerScale } = useSettings();
  return (
    <div className="flex h-full w-full items-center justify-center p-8 text-center text-slate-400">
      <div>
        <h2 className="text-2xl font-bold mb-2">Map Feature Disabled</h2>
        <p>The Google Maps API integration has been removed from this project.</p>
      </div>
    </div>
  );
}
