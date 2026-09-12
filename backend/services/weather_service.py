import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

class WeatherService:
    def __init__(self):
        # Setup the Open-Meteo API client with cache and retry on error
        self.cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=self.retry_session)
        self.url = "https://api.open-meteo.com/v1/forecast"

    def get_forecast(self, latitude: float, longitude: float, horizon_days: int = 3):
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["temperature_2m", "cloud_cover", "wind_speed_10m", "wind_direction_10m", "shortwave_radiation", "direct_normal_irradiance"],
            "forecast_days": horizon_days,
            "timezone": "Asia/Kolkata"
        }
        
        try:
            responses = self.openmeteo.weather_api(self.url, params=params)
            response = responses[0]
            
            hourly = response.Hourly()
            hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
            hourly_cloud_cover = hourly.Variables(1).ValuesAsNumpy()
            hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()
            hourly_wind_direction_10m = hourly.Variables(3).ValuesAsNumpy()
            hourly_shortwave_radiation = hourly.Variables(4).ValuesAsNumpy()
            
            hourly_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left"
                ).tolist(),
                "temperature": hourly_temperature_2m.tolist(),
                "cloud_cover": hourly_cloud_cover.tolist(),
                "wind_speed": hourly_wind_speed_10m.tolist(),
                "wind_direction": hourly_wind_direction_10m.tolist(),
                "solar_radiation": hourly_shortwave_radiation.tolist() # W/m^2
            }
            
            return {"status": "success", "data": hourly_data}
        except Exception as e:
            print(f"Weather API Error: {e}")
            return {"status": "error", "message": str(e), "fallback": True}

# Example usage
if __name__ == "__main__":
    ws = WeatherService()
    # Kutch coordinates
    data = ws.get_forecast(23.7337, 69.8597)
    print(data["status"])
    if data["status"] == "success":
        print(len(data["data"]["temperature"]), "hours of data fetched.")
