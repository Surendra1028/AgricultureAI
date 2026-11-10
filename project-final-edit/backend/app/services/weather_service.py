import httpx
async def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": latitude, "longitude": longitude,
              "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
              "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
              "timezone": "auto", "forecast_days": 3}
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
