# Owner: M3 (inference wiring) / M4 (evaluate integration)
"""
FastAPI inference service for the DataCo Late Delivery Predictor.

Start with:
    make api
    # or: uvicorn backend.app:app --reload --port 8000

Endpoints:
    POST /predict   → PredictionResponse
    GET  /health    → {"status": "ok"}

TODO (M3 / M4):
    Implement the predict() function:
    1. Convert the OrderFeatures pydantic model to a pd.DataFrame whose
       columns match the pipeline's expected inputs
       (CATEGORICAL_LOW + CATEGORICAL_HIGH + NUMERIC from src/config.py).
    2. Call pipeline.predict_proba(df)[:, 1] to get probability.
    3. Apply the risk-tier thresholds (≥0.65 → High, 0.35–0.65 → Medium,
       <0.35 → Low).
    4. Return PredictionResponse.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).parent.parent
MODEL_PATH = ROOT / "models" / "final_pipeline.pkl"

app = FastAPI(
    title="DataCo Late Delivery Predictor",
    description="IT3051 – predicts late-delivery risk at order time.",
    version="0.1.0",
)


# ---------------------------------------------------------------------------
# Model loading (lazy, cached)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_pipeline():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. Run `make train-xgb` first."
        )
    return joblib.load(MODEL_PATH)


# ---------------------------------------------------------------------------
# Pydantic schemas (order-time fields only — no leakage)
# ---------------------------------------------------------------------------

class OrderFeatures(BaseModel):
    """All fields available at the time an order is placed."""

    shipping_mode:    str   = Field(..., example="Standard Class",
                                    description="Shipping Mode")
    payment_type:     str   = Field(..., example="DEBIT",
                                    description="Payment method (Type column)")
    customer_segment: str   = Field(..., example="Consumer")
    market:           str   = Field(..., example="LATAM")
    order_region:     str   = Field(..., example="Western Europe")
    order_country:    str   = Field(..., example="United States")
    order_city:       str   = Field(..., example="New York City")
    category_name:    str   = Field(..., example="Fishing")
    product_name:     str   = Field(..., example="Perfect Fitness Perfect Rip Deck")
    department_name:  str   = Field(..., example="Outdoors")
    product_price:    float = Field(..., ge=0, example=50.0,
                                    description="Order Item Product Price")
    quantity:         int   = Field(..., ge=1, example=1,
                                    description="Order Item Quantity")
    discount_rate:    float = Field(..., ge=0.0, le=1.0, example=0.0,
                                    description="Order Item Discount Rate")
    sales_per_customer: float = Field(default=0.0, ge=0)
    benefit_per_order:  float = Field(default=0.0)
    latitude:           float = Field(default=0.0)
    longitude:          float = Field(default=0.0)


class PredictionResponse(BaseModel):
    probability: float = Field(..., description="P(late delivery)")
    label:       int   = Field(..., description="1 = late, 0 = on time")
    risk_tier:   str   = Field(..., description="High / Medium / Low")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(order: OrderFeatures):
    """
    Run the trained pipeline on a single order and return a risk prediction.
    """
    # TODO M3/M4: implement full inference
    # Sketch:
    #   pipeline = _load_pipeline()
    #   row = {
    #       "Shipping Mode":            order.shipping_mode,
    #       "Type":                     order.payment_type,
    #       "Customer Segment":         order.customer_segment,
    #       "Market":                   order.market,
    #       "Order Region":             order.order_region,
    #       "Order Country":            order.order_country,
    #       "Order City":               order.order_city,
    #       "Category Name":            order.category_name,
    #       "Product Name":             order.product_name,
    #       "Department Name":          order.department_name,
    #       "Order Item Product Price": order.product_price,
    #       "Order Item Quantity":      order.quantity,
    #       "Order Item Discount Rate": order.discount_rate,
    #       "Order Item Discount":      order.product_price * order.quantity * order.discount_rate,
    #       "Sales":                    order.product_price * order.quantity * (1 - order.discount_rate),
    #       "Order Item Profit Ratio":  0.0,   # unknown at order time; use 0 or mean-impute
    #       "Sales per customer":       order.sales_per_customer,
    #       "Benefit per order":        order.benefit_per_order,
    #       "Product Price":            order.product_price,
    #       "Latitude":                 order.latitude,
    #       "Longitude":                order.longitude,
    #   }
    #   df = pd.DataFrame([row])
    #   prob = float(pipeline.predict_proba(df)[0, 1])
    #   label = int(prob >= 0.5)
    #   tier = "High" if prob >= 0.65 else "Medium" if prob >= 0.35 else "Low"
    #   return PredictionResponse(probability=prob, label=label, risk_tier=tier)
    raise HTTPException(
        status_code=501,
        detail="Inference not yet implemented — see TODO in backend/app.py",
    )
