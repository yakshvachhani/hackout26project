'use client';

import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons in Next.js
const customIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});





































































































export default function MapComponent() {
  const center: [number, number] = [23.7337, 69.8597]; // Kutch coordinates

  return (
    <div className="h-[600px] w-full z-0 relative">
      <MapContainer 
        center={center} 
        zoom={14} 
        scrollWheelZoom={false} 
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        {/* Assets */}
        <Marker position={[23.7337, 69.8597]} icon={customIcon}>
          <Popup>
            <div className="text-slate-900 font-bold">Solar Farm 1</div>
            <div className="text-sm">Status: Producing 84kW</div>
          </Popup>
        </Marker>
        
        <Marker position={[23.7380, 69.8620]} icon={customIcon}>
          <Popup>
            <div className="text-slate-900 font-bold">Wind Turbine 1</div>
            <div className="text-sm">Status: Producing 36kW</div>
          </Popup>
        </Marker>

        <Marker position={[23.7320, 69.8550]} icon={customIcon}>
          <Popup>
            <div className="text-slate-900 font-bold">Main Battery Storage</div>
            <div className="text-sm">Status: Discharging (68%)</div>
          </Popup>
        </Marker>

        {/* Load Coverage Circle */}
        <Circle center={center} pathOptions={{ fillColor: '#10b981', color: '#10b981' }} radius={800} opacity={0.2} />
        
      </MapContainer>
    </div>
  );
}
