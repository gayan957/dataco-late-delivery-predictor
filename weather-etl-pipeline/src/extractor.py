import requests
from config.settings import API_BASE_URL, API_PARAMS
from src.logger import get_logger

logger = get_logger("extractor")

def fetch_weather(city: dict) -> dict:
    """Fetch hourly weather data for one city from Open-Meteo."""
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "hourly": ",".join(API_PARAMS),
        "forecast_days": 1,
        "timezone": "auto",
    }
    try:
        resp = requests.get(API_BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Fetched data for {city['name']} — {len(data['hourly']['time'])} records")
        return {"city": city["name"], "raw": data["hourly"]}
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch {city['name']}: {e}")
        return None

def extract_all(cities: list) -> list:
    results = [fetch_weather(c) for c in cities]
    return [r for r in results if r is not None]