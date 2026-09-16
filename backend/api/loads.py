from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import LoadRecord

router = APIRouter(tags=["Priority Load Management"])


@router.get("/loads")
async def get_load_status(db: Session = Depends(get_db)):
    """Returns hierarchical P0 (Critical), P1 (Shiftable), and P2 (Deferrable) load status."""
    latest = db.query(LoadRecord).order_by(LoadRecord.timestamp.desc()).first()

    total_demand = latest.total_demand_kw if latest else 48.2
    p0_pct = latest.p0_served_pct if latest else 100.0
    p1_pct = latest.p1_served_pct if latest else 92.0
    p2_pct = latest.p2_served_pct if latest else 61.0

    return {
        "totalDemandKw": total_demand,
        "summary": {
            "p0ServedPercent": p0_pct,
            "p1ServedPercent": p1_pct,
            "p2ServedPercent": p2_pct,
        },
        "priorities": [
            {
                "id": "p0",
                "tier": "P0 — CRITICAL",
                "type": "PROTECTED",
                "color": "#EF4444",
                "servedPercent": p0_pct,
                "currentKw": 15.0,
                "maxKw": 15.0,
                "items": [
                    {"name": "Off-Grid Community Hospital", "kw": 8.5, "status": "PROTECTED"},
                    {"name": "Vaccine Storage Refrigerators", "kw": 3.2, "status": "PROTECTED"},
                    {"name": "Emergency Communications Tower", "kw": 2.1, "status": "PROTECTED"},
                    {"name": "Central Security & Street Lighting", "kw": 1.2, "status": "PROTECTED"},
                ]
            },
            {
                "id": "p1",
                "tier": "P1 — SHIFTABLE",
                "type": "SHIFTABLE",
                "color": "#F59E0B",
                "servedPercent": p1_pct,
                "currentKw": 18.4,
                "maxKw": 20.0,
                "items": [
                    {"name": "Community Water Well Pumps", "kw": 9.0, "status": "ACTIVE"},
                    {"name": "Agricultural Irrigation Pumps", "kw": 6.4, "status": "ACTIVE"},
                    {"name": "Grain Processing Workshop", "kw": 3.0, "status": "SHIFTED_PARTIAL"},
                ]
            },
            {
                "id": "p2",
                "tier": "P2 — DEFERRABLE",
                "type": "CURTAILABLE",
                "color": "#3B82F6",
                "servedPercent": p2_pct,
                "currentKw": 14.8,
                "maxKw": 24.2,
                "items": [
                    {"name": "Residential AC & High Power Units", "kw": 8.2, "status": "CURTAILED_30%"},
                    {"name": "Community Center Secondary Lighting", "kw": 4.1, "status": "ACTIVE"},
                    {"name": "EV / E-Motorcycle Charging Station", "kw": 2.5, "status": "CURTAILED_50%"},
                ]
            }
        ]
    }


@router.get("/demand")
async def get_demand_series():
    """Returns 24h hourly demand breakdown for frontend."""
    import math
    res = []
    for i in range(24):
        base = 35.0 + 15.0 * math.sin((i - 6) * math.pi / 12) if 6 <= i <= 22 else 20.0
        tot = round(base, 1)
        res.append({
            'time': f"{str(i).zfill(2)}:00",
            'household': round(tot * 0.6, 1),
            'business': round(tot * 0.3, 1),
            'critical': round(tot * 0.1, 1),
            'total': tot
        })
    return res
