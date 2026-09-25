# Owner: M3 – Primesh Marasingha
"""
Central configuration for the DataCo Late-Delivery-REGRESSION project.
All other modules import from here.

Task switched from classification → regression (instructor-approved).
New target: 'Days for shipping (real)'  (integer 0-6)
Expected performance: MAE ≈ 1.0, R² ≈ 0.40-0.45.
R² > 0.75 is a leakage signal.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT           = Path(__file__).parent.parent
DATA_RAW       = ROOT / "data" / "raw" / "DataCoSupplyChainDataset.csv"
DATA_PROCESSED = ROOT / "data" / "processed"
MODELS_DIR     = ROOT / "models"
RESULTS_DIR    = ROOT / "results"
REPORTS_DIR    = ROOT / "reports"

# ---------------------------------------------------------------------------
# Experiment settings
# ---------------------------------------------------------------------------
RANDOM_SEED = 42
TASK        = "regression"
TARGET      = "Days for shipping (real)"

# R² above this threshold almost certainly means a leakage column crept in
LEAKAGE_R2_THRESHOLD = 0.75

# Scheduled shipping days per mode (constant, determined by Shipping Mode only)
# Confirmed from raw data: Same Day=0, First Class=1, Second Class=2, Standard=4
SCHEDULED_DAYS = {
    "Same Day":       0,
    "First Class":    1,
    "Second Class":   2,
    "Standard Class": 4,
}

# ---------------------------------------------------------------------------
# Leakage columns — NEVER use as features
# ---------------------------------------------------------------------------
LEAKAGE_COLS = [
    "Late_delivery_risk",           # binary flag derived from target → leakage
    "Delivery Status",              # post-delivery label
    "shipping date (DateOrders)",   # only known after dispatch
    "Order Status",                 # final fulfilment outcome (filter then drop)
]

# ---------------------------------------------------------------------------
# Drop columns (non-leakage: PII, duplicates, constants, IDs)
# NOTE: 'Days for shipment (scheduled)' is NO LONGER here — it is now a feature.
# ---------------------------------------------------------------------------
DROP_COLS = [
    # PII
    "Customer Email", "Customer Password",
    "Customer Fname", "Customer Lname",
    "Customer Street", "Customer Zipcode",
    # Near-empty / constant
    "Order Zipcode",        # 86 % null
    "Product Description",  # 100 % null
    "Product Status",       # single value throughout
    "Product Image",        # URL, no predictive value
    # Exact duplicate pairs (keep the more interpretable name)
    "Order Customer Id",        # == Customer Id
    "Order Item Cardprod Id",   # == Product Card Id
    "Product Category Id",      # == Category Id
    "Order Profit Per Order",   # == Benefit per order
    "Order Item Total",         # == Sales per customer
    "Order Item Product Price", # == Product Price (confirmed by M1)
    # Identifiers / 1-to-1 mappings (encode info already in a string column)
    "Customer Id",      # identifier — would let model memorise customers
    "Department Id",    # 1-to-1 with Department Name
    "Product Card Id",  # 1-to-1 with Product Name
    "Order Item Id",    # row identifier, no signal
    # Category Id is a duplicate of Category Name; keep the name
    "Category Id",
]

# ---------------------------------------------------------------------------
# Order statuses to exclude before any modelling
# ---------------------------------------------------------------------------
CANCELLED_STATUSES = ["CANCELED", "SUSPECTED_FRAUD"]

# ---------------------------------------------------------------------------
# Feature column lists  (consumed by src/encoders.py ColumnTransformer)
# ---------------------------------------------------------------------------

# One-hot encoded — low cardinality (≤ ~25 unique values)
CATEGORICAL_LOW = [
    "Shipping Mode",    # 4 values
    "Type",             # 4 values (payment type)
    "Customer Segment", # 3 values
    "Market",           # 5 values
    "Order Region",     # 22 values
    "Department Name",  # 22 values
]

# Target-encoded — high cardinality
CATEGORICAL_HIGH = [
    "Order City",    # ~3,585 values
    "Order State",   # ~1,083 values
    "Customer City", # ~563 values
    "Order Country", # ~164 values
    "Product Name",  # ~118 values
    "Category Name", # ~50 values
]

# Numeric pass-through (imputed; optionally scaled)
NUMERIC_BASE = [
    "Days for shipment (scheduled)",  # known at order time — legitimate feature
    "Benefit per order",
    "Sales per customer",
    "Order Item Discount",
    "Order Item Discount Rate",
    "Order Item Profit Ratio",
    "Order Item Quantity",
    "Sales",
    "Product Price",
    "Latitude",
    "Longitude",
]

# Engineered by M2's feature transformers (DateFeatures, OrderFeatures, GeoFeatures)
NUMERIC_ENGINEERED = [
    # DateFeatures
    "order_weekday",
    "order_month",
    "order_hour",
    "order_quarter",
    "is_weekend",
    # OrderFeatures
    "order_items",
    "order_total_sales",
    "order_n_products",
    # GeoFeatures
    "is_domestic",
]

NUMERIC = NUMERIC_BASE + NUMERIC_ENGINEERED
