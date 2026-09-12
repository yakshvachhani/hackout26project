import { ForecastRecord, DispatchRecord, SimulationRequest } from '../types';

const API_BASE = 'http://localhost:8000';

export async function fetchForecast(hours: number = 48): Promise<ForecastRecord[]> {
    const res = await fetch(`${API_BASE}/forecast?hours=${hours}`);
    if (!res.ok) throw new Error('Failed to fetch forecast');
    return res.json();
}

export async function fetchOptimize(hours: number = 48): Promise<DispatchRecord[]> {
    const res = await fetch(`${API_BASE}/optimize?hours=${hours}`);
    if (!res.ok) throw new Error('Failed to fetch optimized dispatch');
    return res.json();
}

export async function fetchDispatchHistory(hours: number = 24): Promise<DispatchRecord[]> {
    const res = await fetch(`${API_BASE}/dispatch-history?hours=${hours}`);
    if (!res.ok) throw new Error('Failed to fetch dispatch history');
    return res.json();
}

export async function simulateDispatch(params: SimulationRequest): Promise<DispatchRecord[]> {
    const res = await fetch(`${API_BASE}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
    });
    if (!res.ok) throw new Error('Simulation failed');
    return res.json();
}
