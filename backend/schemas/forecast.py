from pydantic import BaseModel


class ForecastInterval(BaseModel):
    interval: int
    time: str
    demand: float
    solar: float
    wind: float
    batterySoc: float
    diesel: float

    # snake_case aliases for flexible consumption
    demand_kw: float = 0.0
    solar_kw: float = 0.0
    wind_kw: float = 0.0
    battery_soc: float = 0.0
    diesel_kw: float = 0.0
