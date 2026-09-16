# OptiGrid-AI Schemas Package
from backend.schemas.status import SystemStatusResponse, WeatherInfo, SystemMetrics, LiveDispatch
from backend.schemas.dispatch import OptimizeRequest, OptimizeResponse, DispatchDetail, MetricsDetail
from backend.schemas.battery import BatteryStatusResponse, BatterySocPoint
from backend.schemas.forecast import ForecastInterval
from backend.schemas.fuel import FuelStatusResponse, GeneratorStatus, FuelConsumptionPoint
from backend.schemas.simulation import SimulationRequest, SimulationResponse, SimulationImpact
from backend.schemas.alerts import AlertItem

__all__ = [
    "SystemStatusResponse",
    "WeatherInfo",
    "SystemMetrics",
    "LiveDispatch",
    "OptimizeRequest",
    "OptimizeResponse",
    "DispatchDetail",
    "MetricsDetail",
    "BatteryStatusResponse",
    "BatterySocPoint",
    "ForecastInterval",
    "FuelStatusResponse",
    "GeneratorStatus",
    "FuelConsumptionPoint",
    "SimulationRequest",
    "SimulationResponse",
    "SimulationImpact",
    "AlertItem"
]
