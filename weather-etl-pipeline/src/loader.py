import psycopg2
import psycopg2.extras
import pandas as pd
from config.settings import DATABASE_URL
from src.logger import get_logger

logger = get_logger("loader")

def load(df: pd.DataFrame) -> int:
    """Upsert DataFrame rows into PostgreSQL. Returns rows inserted/updated."""
    records = df[[
        "city", "recorded_at", "temperature_c",
        "precipitation_mm", "windspeed_kmh",
        "weather_code", "weather_description", "temp_feels_cold"
    ]].to_dict("records")

    upsert_sql = """
        INSERT INTO weather_readings
            (city, recorded_at, temperature_c, precipitation_mm,
             windspeed_kmh, weather_code, weather_description, temp_feels_cold)
        VALUES
            (%(city)s, %(recorded_at)s, %(temperature_c)s, %(precipitation_mm)s,
             %(windspeed_kmh)s, %(weather_code)s, %(weather_description)s, %(temp_feels_cold)s)
        ON CONFLICT (city, recorded_at) DO UPDATE SET
            temperature_c       = EXCLUDED.temperature_c,
            precipitation_mm    = EXCLUDED.precipitation_mm,
            windspeed_kmh       = EXCLUDED.windspeed_kmh,
            weather_description = EXCLUDED.weather_description,
            ingested_at         = NOW();
    """
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                psycopg2.extras.execute_batch(cur, upsert_sql, records, page_size=100)
        logger.info(f"Loaded {len(records)} rows into PostgreSQL")
        return len(records)
    except Exception as e:
        logger.error(f"Load failed: {e}")
        raise