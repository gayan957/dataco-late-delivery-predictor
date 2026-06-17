import os
from dotenv import load_dotenv

load_dotenv()

CITIES = [
    {"name": "Colombo", "lat": 6.9271, "lon": 79.8612},
    {"name": "London",  "lat": 51.5074, "lon": -0.1278},
    {"name": "Tokyo",   "lat": 35.6762, "lon": 139.6503},
]

DATABASE_URL = os.getenv("DATABASE_URL")
API_BASE_URL = "https://api.open-meteo.com/v1/forecast"
API_PARAMS = ["temperature_2m", "precipitation", "windspeed_10m", "weathercode"]