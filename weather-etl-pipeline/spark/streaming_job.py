import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, TimestampType
)
JAR_DIR = os.path.join(os.path.dirname(__file__), "jars")
JARS = ",".join([
    f"{JAR_DIR}/spark-sql-kafka-0-10_2.12-3.5.0.jar",
    f"{JAR_DIR}/kafka-clients-3.4.1.jar",
    f"{JAR_DIR}/spark-token-provider-kafka-0-10_2.12-3.5.0.jar",
    f"{JAR_DIR}/commons-pool2-2.11.1.jar",
    f"{JAR_DIR}/postgresql-42.7.1.jar",
])

KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_TOPIC     = "weather-stream"
PG_URL          = "jdbc:postgresql://localhost:5432/weather_stream"
PG_PROPS        = {"user": "postgres", "password": "secret", "driver": "org.postgresql.Driver"}

# ── Spark session ──────────────────────────────────────────────────────────────
spark = (
    SparkSession.builder
    .appName("WeatherStreamingPipeline")
    .config("spark.jars", JARS)
    .config("spark.sql.shuffle.partitions", "3")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

# ── Schema for the incoming JSON ───────────────────────────────────────────────
sensor_schema = StructType([
    StructField("city",          StringType(),    True),
    StructField("timestamp",     StringType(),    True),
    StructField("temperature_c", DoubleType(),    True),
    StructField("windspeed_kmh", DoubleType(),    True),
    StructField("humidity_pct",  DoubleType(),    True),
    StructField("sensor_id",     StringType(),    True),
])

# ── 1. Read from Kafka ─────────────────────────────────────────────────────────
raw_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
    .option("subscribe", KAFKA_TOPIC)
    .option("startingOffsets", "latest")
    .load()
)

# ── 2. Parse JSON payload ──────────────────────────────────────────────────────
parsed = (
    raw_stream
    .select(F.from_json(F.col("value").cast("string"), sensor_schema).alias("data"))
    .select("data.*")
    .withColumn("event_time", F.to_timestamp("timestamp"))
    .drop("timestamp")
)

# ── 3. Watermark + windowed aggregation ───────────────────────────────────────
# Watermark: tolerate up to 30s of late-arriving data
# Window: compute stats over a rolling 1-minute window, sliding every 10s
windowed_agg = (
    parsed
    .withWatermark("event_time", "30 seconds")
    .groupBy(
        F.window("event_time", "1 minute", "10 seconds"),
        F.col("city"),
    )
    .agg(
        F.round(F.avg("temperature_c"), 2).alias("avg_temperature"),
        F.round(F.max("temperature_c"), 2).alias("max_temperature"),
        F.round(F.min("temperature_c"), 2).alias("min_temperature"),
        F.round(F.avg("windspeed_kmh"), 2).alias("avg_windspeed"),
        F.count("*").alias("reading_count"),
    )
    .select(
        F.col("window.start").alias("window_start"),
        F.col("window.end").alias("window_end"),
        "city", "avg_temperature", "max_temperature",
        "min_temperature", "avg_windspeed", "reading_count",
    )
)

# ── 4. Sink A — Live console (great for demos) ─────────────────────────────────
console_query = (
    windowed_agg.writeStream
    .outputMode("update")       # emit rows as they update, not just at window close
    .format("console")
    .option("truncate", False)
    .trigger(processingTime="10 seconds")
    .start()
)

# ── 5. Sink B — PostgreSQL via foreachBatch ────────────────────────────────────
def write_to_postgres(batch_df, batch_id):
    if batch_df.count() == 0:
        return

    # Convert to pandas and upsert manually to handle duplicates
    import psycopg2
    import psycopg2.extras

    records = batch_df.toPandas().to_dict("records")

    upsert_sql = """
        INSERT INTO streaming_readings
            (window_start, window_end, city, avg_temperature, max_temperature,
             min_temperature, avg_windspeed, reading_count)
        VALUES
            (%(window_start)s, %(window_end)s, %(city)s, %(avg_temperature)s,
             %(max_temperature)s, %(min_temperature)s, %(avg_windspeed)s, %(reading_count)s)
        ON CONFLICT (window_start, city) DO UPDATE SET
            avg_temperature = EXCLUDED.avg_temperature,
            max_temperature = EXCLUDED.max_temperature,
            min_temperature = EXCLUDED.min_temperature,
            avg_windspeed   = EXCLUDED.avg_windspeed,
            reading_count   = EXCLUDED.reading_count,
            processed_at    = NOW();
    """

    conn = psycopg2.connect(
        "postgresql://postgres:secret@localhost:5432/weather_stream"
    )
    try:
        with conn.cursor() as cur:
            psycopg2.extras.execute_batch(cur, upsert_sql, records)
        conn.commit()
        print(f"[Batch {batch_id}] Upserted {len(records)} rows to PostgreSQL")
    except Exception as e:
        conn.rollback()
        print(f"[Batch {batch_id}] Error: {e}")
    finally:
        conn.close()
        
print("Streaming job running. Ctrl+C to stop.")
spark.streams.awaitAnyTermination()