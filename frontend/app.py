# Owner: M3 – Primesh Marasingha
"""
Streamlit UI for the DataCo Late Delivery Risk Predictor.

Start with:
    make ui          # requires `make api` running on port 8000

Inputs:  order-time fields only (no leakage)
Outputs: delivery-risk probability, High/Medium/Low tier, suggested action
"""
from __future__ import annotations

from datetime import date

import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"

SHIPPING_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]
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
    "Indoor/Outdoor Games", "Accessories", "Trade-In",
    "As Seen on TV!", "Golf Bags & Carts", "Electronics",
    "Strength Training", "Men's Golf Clubs", "Team Sports",
    "Tennis & Racquet", "Women's Golf Clubs", "Garden",
    "Baseball & Softball", "Girls' Apparel", "Shop All Sports",
    "Boys' Apparel", "Computers", "Health and Beauty", "DVDs",
    "Music", "Books", "Cameras", "Video Games", "Baby",
    "Soccer", "Hunting & Shooting", "Toy Vehicles", "Movies",
    "Children's Books", "Cell Phones", "Basketball", "Hockey",
    "Pet Supplies", "Football", "Hockey Equipment", "Swimming",
    "Boxing & MMA", "Lacrosse", "Rugby", "Volleyball",
    "Other Sports",
]
DEPARTMENTS = [
    "Outdoors", "Fan Shop", "Golf", "Apparel", "Footwear",
    "Technology", "Fitness", "Health and Beauty", "Toys", "Music",
    "DVDs", "Books", "Baby", "Pet Shop",
]

TIER_STYLES = {
    "High":   {"bg": "#fee2e2", "border": "#ef4444", "icon": "🔴",
               "action": "Flag immediately for expedited processing. "
                         "Notify the customer and consider upgrading the shipping mode."},
    "Medium": {"bg": "#fef9c3", "border": "#eab308", "icon": "🟡",
               "action": "Monitor this order closely. "
                         "Review shipping mode and carrier capacity."},
    "Low":    {"bg": "#dcfce7", "border": "#22c55e", "icon": "🟢",
               "action": "No action required. Process through standard fulfilment."},
}


def _risk_tier(prob: float) -> str:
    if prob >= 0.65:
        return "High"
    if prob >= 0.35:
        return "Medium"
    return "Low"


def _call_backend(payload: dict) -> dict:
    resp = requests.post(f"{BACKEND_URL}/predict", json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    st.set_page_config(
        page_title="Late Delivery Risk Predictor",
        page_icon="📦",
        layout="centered",
    )

    st.title("📦 Late Delivery Risk Predictor")
    st.caption("IT3051 Fundamentals of Data Mining · DataCo Smart Supply Chain")

    # ----------------------------------------------------------------
    # Input form
    # ----------------------------------------------------------------
    with st.form("order_form"):
        st.subheader("Order Details")

        col_a, col_b = st.columns(2)

        with col_a:
            shipping_mode    = st.selectbox("Shipping Mode *", SHIPPING_MODES)
            payment_type     = st.selectbox("Payment Type *", PAYMENT_TYPES)
            customer_segment = st.selectbox("Customer Segment *", SEGMENTS)
            market           = st.selectbox("Market *", MARKETS)
            order_region     = st.selectbox("Order Region *", REGIONS)
            department_name  = st.selectbox("Department *", DEPARTMENTS)

        with col_b:
            category_name = st.selectbox("Category *", CATEGORIES)
            order_country = st.text_input("Order Country", value="United States")
            order_city    = st.text_input("Order City", value="Chicago")
            product_name  = st.text_input("Product Name", value="")
            product_price = st.number_input(
                "Product Price ($) *", min_value=0.0, value=50.0, step=0.01,
            )
            quantity = st.number_input(
                "Quantity *", min_value=1, max_value=100, value=1, step=1,
            )

        st.markdown("---")
        col_c, col_d = st.columns(2)
        with col_c:
            discount_rate = st.slider(
                "Discount Rate", min_value=0.0, max_value=1.0,
                value=0.0, step=0.01, format="%.2f",
            )
        with col_d:
            order_date = st.date_input("Order Date", value=date.today())

        submitted = st.form_submit_button(
            "Predict Delivery Risk", use_container_width=True, type="primary",
        )

    # ----------------------------------------------------------------
    # Validation
    # ----------------------------------------------------------------
    if submitted:
        errors = []
        if not order_country.strip():
            errors.append("Order Country is required.")
        if not order_city.strip():
            errors.append("Order City is required.")
        if product_price <= 0:
            errors.append("Product Price must be greater than 0.")

        if errors:
            for err in errors:
                st.error(err)
            st.stop()

        # ----------------------------------------------------------------
        # Backend call
        # ----------------------------------------------------------------
        payload = {
            "shipping_mode":    shipping_mode,
            "payment_type":     payment_type,
            "customer_segment": customer_segment,
            "market":           market,
            "order_region":     order_region,
            "order_country":    order_country.strip(),
            "order_city":       order_city.strip(),
            "category_name":    category_name,
            "product_name":     product_name.strip() or category_name,
            "department_name":  department_name,
            "product_price":    float(product_price),
            "quantity":         int(quantity),
            "discount_rate":    float(discount_rate),
        }

        with st.spinner("Running model…"):
            try:
                result = _call_backend(payload)
            except requests.exceptions.ConnectionError:
                st.error(
                    "**Cannot reach the backend.** "
                    "Make sure the API is running: run `make api` in a separate terminal."
                )
                st.stop()
            except requests.exceptions.HTTPError as exc:
                code = exc.response.status_code
                detail = exc.response.json().get("detail", exc.response.text)
                if code == 501:
                    st.warning(
                        "⚙️ The inference endpoint is not yet implemented "
                        "(backend/app.py TODO). "
                        "Once M3 wires up the model, predictions will appear here."
                    )
                else:
                    st.error(f"Backend error {code}: {detail}")
                st.stop()
            except requests.exceptions.Timeout:
                st.error("Request timed out. The backend may be busy.")
                st.stop()
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")
                st.stop()

        # ----------------------------------------------------------------
        # Result display
        # ----------------------------------------------------------------
        prob  = result["probability"]
        label = result["label"]
        tier  = result["risk_tier"]
        style = TIER_STYLES[tier]

        st.divider()
        st.subheader("Prediction")

        m1, m2, m3 = st.columns(3)
        m1.metric("Risk Probability", f"{prob:.1%}")
        m2.metric("Prediction",       "Late" if label == 1 else "On Time")
        m3.metric("Risk Tier",        f"{style['icon']} {tier}")

        st.progress(min(prob, 1.0))

        # Risk tier card
        st.markdown(
            f"""
            <div style="
                background:{style['bg']};
                border-left: 4px solid {style['border']};
                border-radius: 6px;
                padding: 12px 16px;
                margin-top: 12px;
            ">
                <strong>{style['icon']} {tier} Risk — Suggested Action</strong><br>
                {style['action']}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Order summary expander
        with st.expander("Order summary"):
            st.json({
                "shipping_mode":    shipping_mode,
                "market":           market,
                "order_region":     order_region,
                "category":         category_name,
                "product_price":    f"${product_price:.2f}",
                "quantity":         quantity,
                "discount_rate":    f"{discount_rate:.0%}",
                "order_date":       str(order_date),
            })


if __name__ == "__main__":
    main()
