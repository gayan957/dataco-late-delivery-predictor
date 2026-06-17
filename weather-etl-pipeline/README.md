# Weather ETL Pipeline

> Automated data pipeline that ingests hourly weather data for 3 global 
> cities, transforms and enriches it, and loads it into PostgreSQL — 
> with full logging and idempotent upserts.

## Architecture
[paste the diagram image here]

## Tech stack
- Python 3.11 · Pandas · psycopg2 · Requests
- PostgreSQL 16 (Dockerised)

## What this demonstrates
- Modular ETL pattern (separate Extract / Transform / Load layers)
- Idempotent loading — safe to re-run without duplicating data
- Structured logging to both console and file
- Type-casting, null handling, and derived feature engineering
- Environment-based config with .env

## How to run
[your setup steps]

## Sample output
[paste your terminal summary report screenshot here

## Day 2 — Airflow orchestration

The Day 1 pipeline is wrapped in an Airflow DAG with:
- Hourly scheduling via cron
- 3 automatic retries with 5-min backoff
- XCom-based data passing between tasks
- on_failure_callback for alerting
- Idempotent catchup=False to prevent duplicate loads

Airflow UI: http://localhost:8080