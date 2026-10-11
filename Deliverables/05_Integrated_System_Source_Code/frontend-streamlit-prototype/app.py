# Owner: M3 – Primesh Marasingha
"""
Streamlit UI — DataCo Late Delivery Days Predictor (Regression).

Modes
-----
  API mode  : POST /predict to backend/app.py  (make api)
  Local mode: loads models/xgb_pipeline.pkl directly if API is unreachable

Start: make ui   (requires make api in a second terminal, OR the pkl is present)
"""
from __future__ import annotations

import warnings
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BACKEND_URL = "http://localhost:8000"

# Scheduled days per shipping mode (confirmed from raw data)
SCHEDULED_DAYS = {
    "Same Day":       0,
    "First Class":    1,
    "Second Class":   2,
    "Standard Class": 4,
}

SHIPPING_MODES = list(SCHEDULED_DAYS.keys())
PAYMENT_TYPES  = ["DEBIT", "TRANSFER", "CASH", "PAYMENT"]
SEGMENTS       = ["Consumer", "Corporate", "Home Office"]
MARKETS        = ["LATAM", "Europe", "Pacific Asia", "USCA", "Africa"]
REGIONS        = [
    "Western Europe", "Central America", "Oceania", "Eastern Asia",
    "South America", "Eastern Europe", "Southeast Asia", "Western Asia",
    "West of USA", "US Center", "East of USA", "South Asia",
    "North Africa", "Central Asia", "Southern Africa", "Canada",
    "Caribbean", "West Africa", "Central Africa", "East Africa",
]
CATEGORIES = [
    "Fishing", "Cleats", "Camping & Hiking", "Cardio Equipment",
    "Women's Apparel", "Water Sports", "Men's Footwear",
    "Indoor/Outdoor Games", "Accessories", "Golf Bags & Carts",
    "Electronics", "Strength Training", "Team Sports",
    "Tennis & Racquet", "Garden", "Baseball & Softball",
    "Boys' Apparel", "Girls' Apparel", "Computers",
    "Health and Beauty", "DVDs", "Music", "Books", "Cameras",
    "Video Games", "Baby", "Soccer", "Hunting & Shooting",
    "Basketball", "Hockey", "Pet Supplies", "Football",
    "Swimming", "Boxing & MMA", "Lacrosse",
]
DEPARTMENTS = [
    "Outdoors", "Fan Shop", "Golf", "Apparel", "Footwear",
    "Technology", "Fitness", "Health and Beauty", "Toys", "Music",
    "DVDs", "Books", "Baby", "Pet Shop",
]

VERDICT_STYLE = {
    True:  {"label": "LATE",    "color": "#dc2626", "bg": "#fee2e2",
            "icon": "🔴",
            "tip":  "Consider expediting or upgrading the shipping mode."},
    False: {"label": "ON TIME", "color": "#16a34a", "bg": "#dcfce7",
            "icon": "🟢",
            "tip":  "No action required. Standard processing."},
}

# ---------------------------------------------------------------------------
# Local model (fallback when API is down)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def _load_local_model():
    path = Path("models/xgb_pipeline.pkl")
    if not path.exists():
        return None
    try:
        import joblib
        return joblib.load(path)
    except Exception:
        return None


def _build_input_row(
    shipping_mode: str,
    payment_type: str,
    customer_segment: str,
    market: str,
    order_region: str,
    order_country: str,
    order_city: str,
    customer_city: str,
    customer_country: str,
    category_name: str,
    product_name: str,
    department_name: str,
    product_price: float,
    quantity: int,
    discount_rate: float,
    order_date: date,
) -> pd.DataFrame:
    """Map form values to a DataFrame the pipeline expects."""
    # Format date to match M2's DateFeatures parse format
    d   = datetime.combine(order_date, datetime.min.time())
    dt_str = f"{d.month}/{d.day:02d}/{d.year} 00:00"

    sales    = product_price * quantity * (1.0 - discount_rate)
    discount = product_price * quantity * discount_rate
    sched    = SCHEDULED_DAYS.get(shipping_mode, 4)

    row = {
        # Core categoricals
        "Shipping Mode":                shipping_mode,
        "Type":                         payment_type,
        "Customer Segment":             customer_segment,
        "Market":                       market,
        "Order Region":                 order_region,
        "Order Country":                order_country,
        "Order City":                   order_city,
        "Order State":                  "",          # unknown at UI time
        "Customer City":                customer_city,
        "Customer State":               "",
        "Customer Country":             customer_country,
        "Category Name":                category_name,
        "Product Name":                 product_name or category_name,
        "Department Name":              department_name,
        # Date (M2's DateFeatures parses this)
        "order date (DateOrders)":      dt_str,
        # Numeric features
        "Days for shipment (scheduled)": sched,
        "Product Price":                product_price,
        "Order Item Quantity":          quantity,
        "Order Item Discount Rate":     discount_rate,
        "Order Item Discount":          discount,
        "Sales":                        sales,
        "Benefit per order":            0.0,         # unknown at order time
        "Sales per customer":           sales,
        "Order Item Profit Ratio":      0.0,
        "Latitude":                     0.0,
        "Longitude":                    0.0,
        # Order-level columns (used by M2's OrderFeatures; 1-item dummy order)
        "Order Id":                     999_999_999,
    }
    return pd.DataFrame([row])


def _local_predict(df: pd.DataFrame, shipping_mode: str) -> dict:
    model = _load_local_model()
    if model is None:
        raise FileNotFoundError(
            "models/xgb_pipeline.pkl not found. Run `make train-xgb` first."
        )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pred_days = float(model.predict(df)[0])

    sched   = SCHEDULED_DAYS.get(shipping_mode, 4)
    is_late = pred_days > sched
    return {
        "predicted_days": round(pred_days, 2),
        "scheduled_days": sched,
        "is_late":        is_late,
    }


def _api_predict(payload: dict) -> dict:
    resp = requests.post(f"{BACKEND_URL}/predict", json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="Delivery Days Predictor",
        page_icon="📦",
        layout="centered",
    )

    st.title("📦 Delivery Days Predictor")
    st.caption("IT3051 Data Mining · DataCo Supply Chain · Regression model")

    # ---------------------------------------------------------------- form
    with st.form("predict_form"):
        st.subheader("Order Details")
        col1, col2 = st.columns(2)

        with col1:
            shipping_mode    = st.selectbox("Shipping Mode *", SHIPPING_MODES)
            payment_type     = st.selectbox("Payment Type *", PAYMENT_TYPES)
            customer_segment = st.selectbox("Customer Segment *", SEGMENTS)
            market           = st.selectbox("Market *", MARKETS)
            order_region     = st.selectbox("Order Region *", REGIONS)
            department_name  = st.selectbox("Department *", DEPARTMENTS)

        with col2:
            category_name    = st.selectbox("Category *", CATEGORIES)
            order_country    = st.text_input("Order Country *", value="United States")
            order_city       = st.text_input("Order City", value="Chicago")
            customer_country = st.text_input("Customer Country", value="United States")
            customer_city    = st.text_input("Customer City", value="")
            product_name     = st.text_input("Product Name (optional)", value="")

        st.markdown("---")
        col3, col4, col5 = st.columns(3)
        with col3:
            product_price = st.number_input("Product Price ($) *", min_value=0.01,
                                            value=50.0, step=0.01)
        with col4:
            quantity      = st.number_input("Quantity *", min_value=1, max_value=100,
                                            value=1, step=1)
        with col5:
            discount_rate = st.slider("Discount Rate", 0.0, 1.0, 0.0, 0.01)

        order_date = st.date_input("Order Date", value=date.today())

        submitted = st.form_submit_button(
            "Predict Delivery Days", use_container_width=True, type="primary"
        )

    # ---------------------------------------------------------------- on submit
    if submitted:
        # Validation
        errors = []
        if not order_country.strip():
            errors.append("Order Country is required.")
        if product_price <= 0:
            errors.append("Product Price must be greater than 0.")
        for err in errors:
            st.error(err)
        if errors:
            st.stop()

        input_df = _build_input_row(
            shipping_mode, payment_type, customer_segment, market, order_region,
            order_country.strip(), order_city.strip(),
            customer_city.strip(), customer_country.strip(),
            category_name, product_name.strip(), department_name,
            product_price, int(quantity), discount_rate, order_date,
        )

        result = None
        mode_label = ""

        with st.spinner("Running model …"):
            # Try API first
            try:
                payload = {
                    "shipping_mode":    shipping_mode,
                    "payment_type":     payment_type,
                    "customer_segment": customer_segment,
                    "market":           market,
                    "order_region":     order_region,
                    "order_country":    order_country.strip(),
                    "order_city":       order_city.strip(),
                    "customer_city":    customer_city.strip(),
                    "customer_country": customer_country.strip(),
                    "category_name":    category_name,
                    "product_name":     product_name.strip() or category_name,
                    "department_name":  department_name,
                    "product_price":    float(product_price),
                    "quantity":         int(quantity),
                    "discount_rate":    float(discount_rate),
                    "order_date":       str(order_date),
                }
                result     = _api_predict(payload)
                mode_label = "API"
            except requests.exceptions.ConnectionError:
                pass  # fall through to local mode
            except requests.exceptions.HTTPError as exc:
                code = exc.response.status_code
                if code == 501:
                    pass  # backend stub not implemented yet — use local
                else:
                    st.error(f"Backend error {code}: {exc.response.text}")
                    st.stop()
            except requests.exceptions.Timeout:
                st.warning("API timed out — falling back to local model.")

            # Fall back to local pkl
            if result is None:
                try:
                    result     = _local_predict(input_df, shipping_mode)
                    mode_label = "Local pkl"
                except FileNotFoundError as exc:
                    st.error(
                        f"**No model available.**  {exc}\n\n"
                        "Start the API (`make api`) or train a model (`make train-xgb`)."
                    )
                    st.stop()
                except Exception as exc:
                    st.error(f"Local inference failed: {exc}")
                    st.stop()

        # ---------------------------------------------------------------- display
        pred_days  = result["predicted_days"]
        sched_days = result["scheduled_days"]
        is_late    = result.get("is_late", pred_days > sched_days)
        vs         = VERDICT_STYLE[is_late]

        st.divider()
        st.subheader("Prediction")

        m1, m2, m3 = st.columns(3)
        m1.metric("Predicted Days",  f"{pred_days:.1f}")
        m2.metric("Scheduled Days",  sched_days)
        m3.metric("Mode used",       mode_label)

        # Verdict card
        st.markdown(
            f"""
            <div style="
                background:{vs['bg']};
                border-left:5px solid {vs['color']};
                border-radius:6px;
                padding:14px 18px;
                margin-top:10px;
            ">
                <span style="font-size:1.3rem;font-weight:700;color:{vs['color']};">
                    {vs['icon']}  {vs['label']}
                </span><br>
                Predicted <b>{pred_days:.1f} days</b> vs scheduled
                <b>{sched_days} days</b>
                ({shipping_mode})<br>
                <i>{vs['tip']}</i>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Shipping mode context
        st.caption(
            f"ℹ️ For **{shipping_mode}**, scheduled = {sched_days} day(s). "
            f"Historical mean real days: "
            f"Same Day≈0.5 · First Class≈2.0 · Second Class≈4.0 · Standard Class≈4.0"
        )

        with st.expander("Order summary sent to model"):
            st.dataframe(input_df.T.rename(columns={0: "value"}))


if __name__ == "__main__":
    main()
