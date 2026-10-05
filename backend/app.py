"""
FastAPI inference service — DataCo Late Delivery Predictor.
Two models loaded at startup:
  • final_pipeline.pkl      — regression  → predicts delivery days
  • clf_final_pipeline.pkl  — classification → predicts late probability

Start:  make api   (uvicorn backend.app:app --reload --port 8000)
"""
from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT      = Path(__file__).parent.parent
REG_PATH  = ROOT / "models" / "final_pipeline.pkl"
CLF_PATH  = ROOT / "models" / "clf_final_pipeline.pkl"

CLF_THRESHOLD = 0.65

SCHEDULED_DAYS: dict[str, int] = {
    "Same Day":       0,
    "First Class":    1,
    "Second Class":   2,
    "Standard Class": 4,
}

FEATURE_COLS = [
    "Shipping Mode", "Market", "Order Country", "Category Name",
    "Order Item Quantity", "Customer Segment",
    "order_weekday", "order_month", "order_hour", "order_quarter", "is_weekend",
]

app = FastAPI(
    title="DataCo Late Delivery Predictor",
    description="IT3051 – regression + classification models at order placement time.",
    version="2.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def _load_reg():
    if not REG_PATH.exists():
        raise FileNotFoundError(f"Regression model not found: {REG_PATH}")
    return joblib.load(REG_PATH)


@lru_cache(maxsize=1)
def _load_clf():
    if not CLF_PATH.exists():
        raise FileNotFoundError(f"Classification model not found: {CLF_PATH}")
    return joblib.load(CLF_PATH)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_row(order: "OrderFeatures") -> dict:
    try:
        dt = datetime.strptime(order.order_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=422, detail="order_date must be YYYY-MM-DD")
    return {
        "Shipping Mode":       order.shipping_mode,
        "Market":              order.market,
        "Order Country":       order.order_country,
        "Category Name":       order.category_name,
        "Order Item Quantity": order.quantity,
        "Customer Segment":    order.customer_segment,
        "order_weekday":       dt.weekday(),
        "order_month":         dt.month,
        "order_hour":          dt.hour,
        "order_quarter":       (dt.month - 1) // 3 + 1,
        "is_weekend":          int(dt.weekday() >= 5),
    }


# ── Schemas ───────────────────────────────────────────────────────────────────

class OrderFeatures(BaseModel):
    shipping_mode:    str = Field(..., example="Standard Class")
    market:           str = Field(..., example="LATAM")
    order_country:    str = Field(..., example="Estados Unidos")
    category_name:    str = Field(..., example="Fishing")
    quantity:         int = Field(..., ge=1, le=10, example=1)
    customer_segment: str = Field(..., example="Consumer")
    order_date:       str = Field(..., example="2026-10-05",
                                  description="ISO date YYYY-MM-DD")


class PredictionResponse(BaseModel):
    predicted_days: float
    scheduled_days: int
    is_late:        bool
    late_by:        float
    shipping_mode:  str


class ClassifyResponse(BaseModel):
    is_late:      bool
    probability:  float = Field(..., description="P(late) from the classifier, 0–1")
    threshold:    float = Field(..., description="Decision threshold used")
    shipping_mode: str


class CombinedResponse(BaseModel):
    regression:     PredictionResponse
    classification: ClassifyResponse


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(order: OrderFeatures):
    try:
        pipeline = _load_reg()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    df = pd.DataFrame([_build_row(order)], columns=FEATURE_COLS)

    try:
        predicted_days = float(max(0.0, pipeline.predict(df)[0]))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Regression inference failed: {exc}")

    scheduled = SCHEDULED_DAYS.get(order.shipping_mode, 4)
    return PredictionResponse(
        predicted_days=round(predicted_days, 2),
        scheduled_days=scheduled,
        is_late=predicted_days > scheduled,
        late_by=round(predicted_days - scheduled, 2),
        shipping_mode=order.shipping_mode,
    )


@app.post("/classify", response_model=ClassifyResponse)
def classify(order: OrderFeatures):
    try:
        clf = _load_clf()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    df = pd.DataFrame([_build_row(order)], columns=FEATURE_COLS)

    try:
        proba = float(clf.predict_proba(df)[0][1])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Classification inference failed: {exc}")

    return ClassifyResponse(
        is_late=proba >= CLF_THRESHOLD,
        probability=round(proba, 4),
        threshold=CLF_THRESHOLD,
        shipping_mode=order.shipping_mode,
    )


@app.post("/predict/combined", response_model=CombinedResponse)
def predict_combined(order: OrderFeatures):
    """Run both models in one round-trip."""
    return CombinedResponse(
        regression=predict(order),
        classification=classify(order),
    )
