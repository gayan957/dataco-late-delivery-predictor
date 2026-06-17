from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta

sys.path.insert(0, "/opt/airflow")

from airflow import DAG
from airflow.operators.python import PythonOperator

from config.settings import CITIES
from src.extractor import extract_all
from src.transformer import transform_all
from src.loader import load
from src.logger import get_logger

logger = get_logger("weather_dag")

# ── Default args apply to every task ──────────────────────────────────────────
default_args = {
    "owner": "you",
    "retries": 3,                          # retry 3 times on failure
    "retry_delay": timedelta(minutes=5),   # wait 5 min between retries
    "email_on_failure": False,
    "email_on_retry": False,
}

# ── Failure callback (fires if all retries exhausted) ─────────────────────────
def on_failure_callback(context):
    task_id  = context["task_instance"].task_id
    dag_id   = context["dag"].dag_id
    exc      = context.get("exception")
    logger.error(f"ALERT: Task {task_id} in {dag_id} failed. Exception: {exc}")
    # In production: send Slack/email here


# ── Task functions ─────────────────────────────────────────────────────────────
def check_api_health(**context):
    """Validate the Open-Meteo API is reachable before doing real work."""
    import requests
    test_city = CITIES[0]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={test_city['lat']}&longitude={test_city['lon']}&hourly=temperature_2m&forecast_days=1"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    logger.info("API health check passed")
    return "healthy"


def extract_weather(**context):
    """Extract raw weather data and push to XCom for downstream tasks."""
    raw_records = extract_all(CITIES)
    if not raw_records:
        raise ValueError("No data extracted — all cities failed")

    # XCom can only store JSON-serialisable data
    serialisable = [
        {"city": r["city"], "raw": r["raw"]}
        for r in raw_records
    ]
    context["ti"].xcom_push(key="raw_records", value=serialisable)
    logger.info(f"Pushed {len(serialisable)} raw records to XCom")
    return len(serialisable)


def transform_data(**context):
    """Pull raw records from XCom, transform, push clean data to XCom."""
    raw_records = context["ti"].xcom_pull(
        task_ids="extract_weather", key="raw_records"
    )
    if not raw_records:
        raise ValueError("No raw records found in XCom")

    df = transform_all(raw_records)

    # Store as list-of-dicts for XCom (DataFrames aren't serialisable)
    records_json = df.to_json(orient="records", date_format="iso")
    context["ti"].xcom_push(key="clean_records", value=records_json)
    logger.info(f"Transformed {len(df)} rows, pushed to XCom")
    return len(df)


def load_to_postgres(**context):
    """Pull clean records from XCom and load into PostgreSQL."""
    import pandas as pd
    records_json = context["ti"].xcom_pull(
        task_ids="transform_data", key="clean_records"
    )
    if not records_json:
        raise ValueError("No clean records found in XCom")

    df = pd.read_json(records_json, orient="records")
    df["recorded_at"] = pd.to_datetime(df["recorded_at"])

    rows = load(df)
    logger.info(f"Loaded {rows} rows into PostgreSQL")
    return rows


# ── DAG definition ─────────────────────────────────────────────────────────────
with DAG(
    dag_id="weather_etl_pipeline",
    default_args=default_args,
    description="Hourly weather ETL: Open-Meteo → PostgreSQL",
    schedule="@hourly",
    start_date=datetime(2024, 1, 1),
    catchup=False,                   # don't backfill missed runs
    tags=["etl", "weather", "portfolio"],
    on_failure_callback=on_failure_callback,
) as dag:

    t1_health = PythonOperator(
        task_id="check_api_health",
        python_callable=check_api_health,
    )

    t2_extract = PythonOperator(
        task_id="extract_weather",
        python_callable=extract_weather,
    )

    t3_transform = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )

    t4_load = PythonOperator(
        task_id="load_to_postgres",
        python_callable=load_to_postgres,
    )

    # ── Task dependency chain ──────────────────────────────────────────────────
    t1_health >> t2_extract >> t3_transform >> t4_load