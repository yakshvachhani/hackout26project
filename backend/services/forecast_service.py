import math
import random
import logging
from typing import List, Optional
from backend.schemas.forecast import ForecastInterval

logger = logging.getLogger(__name__)


class ForecastService:
    """Generates 24-hour ahead microgrid operational forecasts at 15-minute resolution (96 intervals)."""

    def generate_24h_forecast(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> List[ForecastInterval]:
        try:
            from data import get_api_forecast_payload
            if latitude is None or longitude is None:
                try:
                    from backend.services.location_service import location_service
                    loc = location_service.get_active_location()
                    latitude = loc.latitude
                    longitude = loc.longitude
                except Exception:
                    pass

            raw_intervals = get_api_forecast_payload(
                duration_hours=24,
                latitude=latitude,
                longitude=longitude,
            )
            if raw_intervals and len(raw_intervals) == 96:
                return [ForecastInterval(**item) for item in raw_intervals]
        except Exception as e:
            logger.warning(f"Error invoking Member 4 forecast service ({e}); utilizing baseline generator.")

        return self._fallback_generate_24h_forecast()

    def _fallback_generate_24h_forecast(self) -> List[ForecastInterval]:
        intervals: List[ForecastInterval] = []

        for i in range(96):
            total_minutes = i * 15
            hour = total_minutes // 60
            minute = total_minutes % 60
            time_str = f"{hour:02d}:{minute:02d}"

            # Demand curve: night low (20-30kW), morning peak (45kW), afternoon (35kW), evening peak (65-70kW)
            demand_val = 25.0 + math.sin((hour - 4) * math.pi / 12) * 15.0 + math.exp(-math.pow(hour - 20, 2) / 8) * 30.0
            demand_val = max(18.0, min(75.0, demand_val + random.uniform(-1.0, 1.0)))

            # Solar PV generation: 0 at night, bell curve from 06:00 to 18:00 peaking at ~45kW
            solar_val = 0.0
            if 6 <= hour <= 18:
                solar_val = 45.0 * math.sin((hour - 6) * math.pi / 12)
                solar_val = max(0.0, solar_val + random.uniform(-1.5, 1.5))

            # Wind generation: fluctuating between 8kW and 24kW, slightly higher in early morning and night
            wind_val = 14.0 + math.cos((hour + 2) * math.pi / 8) * 6.0 + random.uniform(-1.5, 1.5)
            wind_val = max(5.0, min(25.0, wind_val))

            net_renewable = solar_val + wind_val

            # Battery SOC simulation
            if 10 <= hour <= 16:
                soc = 60.0 + ((hour - 10) * 5.0)  # Charging up during daytime solar excess
            elif 17 <= hour <= 23:
                soc = 90.0 - ((hour - 17) * 4.5)  # Discharging during evening load peak
            else:
                soc = 60.0 - (hour * 0.5)
            soc = max(20.0, min(95.0, round(soc)))

            # Diesel generation required if renewable + battery deficit
            diesel_val = 0.0
            if (net_renewable + 15.0) < demand_val and soc <= 25:
                diesel_val = demand_val - net_renewable - 5.0
            diesel_val = max(0.0, round(diesel_val, 1))

            demand_rounded = round(demand_val, 1)
            solar_rounded = round(solar_val, 1)
            wind_rounded = round(wind_val, 1)

            intervals.append(
                ForecastInterval(
                    interval=i + 1,
                    time=time_str,
                    demand=demand_rounded,
                    solar=solar_rounded,
                    wind=wind_rounded,
                    batterySoc=float(soc),
                    diesel=diesel_val,
                    demand_kw=demand_rounded,
                    solar_kw=solar_rounded,
                    wind_kw=wind_rounded,
                    battery_soc=float(soc),
                    diesel_kw=diesel_val
                )
            )

        return intervals


forecast_service = ForecastService()
