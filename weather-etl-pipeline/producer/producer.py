import json
import time
import random
from datetime import datetime, timezone
from kafka import KafkaProducer

CITIES = [
    {"name": "Colombo", "base_temp": 30, "base_wind": 18},
    {"name": "London",  "base_temp": 12, "base_wind": 25},
    {"name": "Tokyo",   "base_temp": 22, "base_wind": 15},
]

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8"),
)

def generate_reading(city: dict) -> dict:
    """Simulate a realistic sensor reading with gaussian noise."""
    return {
        "city":          city["name"],
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(city["base_temp"] + random.gauss(0, 2), 2),
        "windspeed_kmh": round(max(0, city["base_wind"] + random.gauss(0, 5)), 2),
        "humidity_pct":  round(random.uniform(40, 95), 1),
        "sensor_id":     f"sensor_{city['name'].lower()}_01",
    }

print("Producer started — streaming weather data to Kafka...")
try:
    while True:
        for city in CITIES:
            reading = generate_reading(city)
            producer.send(
                topic="weather-stream",
                key=city["name"],       # partition key ensures city ordering
                value=reading,
            )
            print(f"  Sent: {city['name']} | {reading['temperature_c']}°C | {reading['windspeed_kmh']} km/h")
        producer.flush()
        time.sleep(1)
except KeyboardInterrupt:
    print("\nProducer stopped.")
    producer.close()