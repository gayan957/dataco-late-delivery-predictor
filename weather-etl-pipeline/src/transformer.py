import pandas as pd
from src.logger import get_logger

logger = get_logger("transformer")

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog", 51: "Light drizzle", 61: "Slight rain",
    71: "Slight snow", 80: "Rain showers", 95: "Thunderstorm",
}

def transform(raw_record: dict) -> pd.DataFrame:
    """Clean and enrich one city's raw data into a DataFrame."""
    city = raw_record["city"]
    raw  = raw_record["raw"]

    df = pd.DataFrame(raw)
    df.rename(columns={
        "time": "recorded_at",
        "temperature_2m": "temperature_c",
        "precipitation": "precipitation_mm",
        "windspeed_10m": "windspeed_kmh",
        "weathercode": "weather_code",
    }, inplace=True)

    df["recorded_at"]      = pd.to_datetime(df["recorded_at"])
    df["temperature_c"]    = pd.to_numeric(df["temperature_c"], errors="coerce")
    df["precipitation_mm"] = pd.to_numeric(df["precipitation_mm"], errors="coerce").fillna(0)
    df["windspeed_kmh"]    = pd.to_numeric(df["windspeed_kmh"], errors="coerce")
    df["city"]             = city
    df["weather_description"] = df["weather_code"].map(WEATHER_CODES).fillna("Unknown")
    df["temp_feels_cold"]  = df["temperature_c"] < 10   # simple derived flag

    df.dropna(subset=["temperature_c", "windspeed_kmh"], inplace=True)
    logger.info(f"Transformed {len(df)} rows for {city}")
    return df

def transform_all(raw_records: list) -> pd.DataFrame:
    frames = [transform(r) for r in raw_records]
    return pd.concat(frames, ignore_index=True)