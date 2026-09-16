from typing import List, Union
from pydantic import field_validator
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    from pydantic import BaseModel
    class BaseSettings(BaseModel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
    SettingsConfigDict = dict


class Settings(BaseSettings):
    APP_NAME: str = "OptiGrid-AI Microgrid Optimizer"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    DEMO_MODE: bool = True

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./optigrid.db"

    # External APIs
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    NASA_POWER_BASE_URL: str = "https://power.larc.nasa.gov/api"

    # Microgrid Default Coordinates (e.g. Remote Solar/Wind Off-Grid Community)
    DEFAULT_LATITUDE: float = 23.0225
    DEFAULT_LONGITUDE: float = 72.5714

    # CORS
    FRONTEND_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    # WebSocket & Telemetry
    TELEMETRY_INTERVAL_SECONDS: int = 5

    @field_validator("FRONTEND_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
