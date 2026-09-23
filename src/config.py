# Owner: M3 – Primesh Marasingha
"""
Central configuration: paths, constants, and column lists.
All other modules import from here — never hard-code paths or column names elsewhere.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
DATA_RAW = ROOT / "data" / "raw" / "DataCoSupplyChainDataset.csv"
DATA_PROCESSED = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"
REPORTS_DIR = ROOT / "reports"

# ---------------------------------------------------------------------------
# Experiment settings
# ---------------------------------------------------------------------------
RANDOM_SEED = 42
TARGET = "Late_delivery_risk"

# ---------------------------------------------------------------------------
# Columns that must NEVER appear as model features (confirmed leakage).
# These are only known at delivery time, not at order time.
# ---------------------------------------------------------------------------
LEAKAGE_COLS = [
    "Days for shipping (real)",   # actual transit days — unavailable at order time
    "Delivery Status",            # derived from real shipping days
    "shipping date (DateOrders)", # occurs after the order is placed
    "Order Status",               # final fulfilment outcome
]

# ---------------------------------------------------------------------------
# Columns to drop for other reasons (duplicates, PII, near-zero variance).
# ---------------------------------------------------------------------------
DROP_COLS = [
    # Scheduled shipping days is deterministic given Shipping Mode → drop to
    # avoid indirect leakage through a derived constant.
    "Days for shipment (scheduled)",
    # PII
    "Customer Email",
    "Customer Password",
    "Customer Fname",
    "Customer Lname",
    "Customer Street",
    "Customer Zipcode",
    # 86 % null
    "Order Zipcode",
    # 100 % null / constant
    "Product Description",
    "Product Status",
    "Product Image",
    # Exact duplicate columns
    "Order Customer Id",       # == Customer Id
    "Order Item Cardprod Id",  # == Product Card Id
    "Product Category Id",     # == Category Id
    "Order Profit Per Order",  # duplicate aggregate
    "Order Item Total",        # == Sales (item-level)
]

# ---------------------------------------------------------------------------
# Order statuses to exclude before any modelling
# ---------------------------------------------------------------------------
CANCELLED_STATUSES = ["CANCELED", "SUSPECTED_FRAUD"]

# ---------------------------------------------------------------------------
# Feature column lists consumed by src/encoders.py ColumnTransformer.
# Add engineered column names here once src/features.py is implemented.
# ---------------------------------------------------------------------------

# One-hot encoded (low cardinality ≤ ~25 unique values)
CATEGORICAL_LOW = [
    "Shipping Mode",     # 4 values
    "Type",              # 4 values (payment type)
    "Customer Segment",  # 3 values
    "Market",            # 5 values
    "Order Region",      # 22 values
    "Department Name",   # 22 values
]

# Target / frequency encoded (high cardinality)
CATEGORICAL_HIGH = [
    "Order City",    # 3,597 unique values
    "Order Country", # 164
    "Product Name",  # 118
    "Category Name", # 50
]

# Pass-through numeric features
NUMERIC = [
    "Benefit per order",
    "Sales per customer",
    "Order Item Discount",
    "Order Item Discount Rate",
    "Order Item Product Price",
    "Order Item Profit Ratio",
    "Order Item Quantity",
    "Sales",
    "Product Price",
    "Latitude",
    "Longitude",
]
