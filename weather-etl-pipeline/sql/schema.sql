CREATE TABLE IF NOT EXISTS weather_readings (
    id              SERIAL PRIMARY KEY,
    city            VARCHAR(100)   NOT NULL,
    recorded_at     TIMESTAMPTZ    NOT NULL,
    temperature_c   NUMERIC(5, 2),
    precipitation_mm NUMERIC(6, 2),
    windspeed_kmh   NUMERIC(6, 2),
    weather_code    INTEGER,
    weather_description VARCHAR(100),
    temp_feels_cold BOOLEAN,
    ingested_at     TIMESTAMPTZ    DEFAULT NOW(),
    UNIQUE(city, recorded_at)      -- prevents duplicate loads
);

CREATE TABLE IF NOT EXISTS streaming_readings (
    window_start     TIMESTAMPTZ,
    window_end       TIMESTAMPTZ,
    city             VARCHAR(100),
    avg_temperature  NUMERIC(5, 2),
    max_temperature  NUMERIC(5, 2),
    min_temperature  NUMERIC(5, 2),
    avg_windspeed    NUMERIC(6, 2),
    reading_count    INTEGER,
    processed_at     TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (window_start, city)
);