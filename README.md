# DataCo Late Delivery Risk Predictor

**IT3051 Fundamentals of Data Mining — Group Mini-Project**

Predicts whether an order will be delivered late *at the time it is placed*,
using the DataCo Smart Supply Chain dataset.

> **Dataset**: Mendeley Data — DOI [10.17632/8gx2fvg2k6.1](https://doi.org/10.17632/8gx2fvg2k6.1)
> 180,519 rows × 53 cols, LATIN-1 encoded.
> Target: `Late_delivery_risk` (1 = late, 54.8 %).

---

## Hard Rules — read before touching any code

| Rule | Detail |
|------|--------|
| **No leakage** | Never use `Days for shipping (real)`, `Delivery Status`, `shipping date (DateOrders)`, or `Order Status` as features — these are only known post-delivery. |
| **Grouped split** | All items sharing the same `Order Id` must land in the **same** partition. Use `GroupShuffleSplit` / `StratifiedGroupKFold`. A plain `train_test_split` is a bug. |
| **Fit-only-on-train** | Every encoder and scaler must be fitted exclusively on training fold data inside a sklearn `Pipeline`. Never call `.fit()` on test data. |
| **Exclude rows** | Remove `Order Status ∈ {CANCELED, SUSPECTED_FRAUD}` (7,754 rows) before any analysis or split. |

---

## Setup

```bash
# Requires Python 3.11 on PATH
make setup          # creates .venv and installs requirements.txt
```

---

## How to run

```bash
# 1. Place CSV in data/raw/ then generate the train/test split (M1 must implement data_prep.py)
make split

# 2. Train XGBoost (default: 5-fold StratifiedGroupKFold CV then final fit)
make train-xgb

# 3. Train with RandomizedSearchCV hyperparameter tuning
make train-xgb-tune

# 4. Start the REST API (port 8000)
make api

# 5. Start the Streamlit UI (port 8501; requires API running)
make ui

# 6. Run the anti-leakage test suite
make test
```

---

## File Ownership

| File / Directory | Owner | Status |
|------------------|-------|--------|
| `src/config.py` | **M3 – Primesh** | ✅ implemented |
| `src/encoders.py` | **M3 – Primesh** | ✅ implemented |
| `src/train_xgb.py` | **M3 – Primesh** | ✅ implemented |
| `frontend/app.py` | **M3 – Primesh** | ✅ implemented |
| `src/data_prep.py` | M1 | 🔧 stub |
| `src/features.py` | M2 | 🔧 stub |
| `notebooks/01_eda_m2.ipynb` | M2 | 🔧 stub |
| `src/evaluate.py` | M4 | 🔧 stub |
| `backend/app.py` | M3 / M4 | 🔧 stub |
| `src/train_logreg.py` | M1 / M4 | 🔧 stub |
| `src/train_rf.py` | M1 / M4 | 🔧 stub |
| `src/train_tree_knn.py` | M1 / M4 | 🔧 stub |
| `notebooks/03_models.ipynb` | M4 | 🔧 stub |

---

## Project structure

```
dataco-late-delivery-predictor/
├── data/
│   ├── raw/            # DataCoSupplyChainDataset.csv  ← gitignored
│   └── processed/      # parquet files from make split
├── models/             # trained .pkl files            ← gitignored
├── notebooks/
│   ├── 01_eda_m2.ipynb
│   ├── 02_encoding_m3.ipynb
│   └── 03_models.ipynb
├── src/
│   ├── config.py       # paths, constants, column lists
│   ├── data_prep.py    # load → clean → split  (M1)
│   ├── features.py     # date / geo / order features  (M2)
│   ├── encoders.py     # ColumnTransformer + select_features  (M3)
│   ├── evaluate.py     # metrics + CSV logging  (M4)
│   ├── train_xgb.py    # XGBoost pipeline  (M3)
│   ├── train_rf.py     # Random Forest  (M1/M4)
│   ├── train_logreg.py # Logistic Regression baseline  (M1/M4)
│   └── train_tree_knn.py # Decision Tree + KNN  (M1/M4)
├── backend/
│   └── app.py          # FastAPI inference API  (M3/M4)
├── frontend/
│   └── app.py          # Streamlit UI  (M3)
├── tests/
│   └── test_no_leakage.py
├── results/
│   └── experiments.csv
├── reports/            # figures, tables
├── requirements.txt
├── Makefile
└── .gitignore
```

---

## Encoding design (`src/encoders.py`)

| Block | Columns | Method |
|-------|---------|--------|
| `ohe` | Shipping Mode, Type, Customer Segment, Market, Order Region, Department Name | `OneHotEncoder(handle_unknown="ignore")` |
| `high_card` | Order City (3 597), Order Country (164), Product Name (118), Category Name (50) | `TargetEncoder(smooth="auto")` or `FrequencyEncoder` |
| `num` | 11 numeric columns | passthrough |

All transformers live inside a single `ColumnTransformer` which is the first
step of every `Pipeline` — guaranteeing no encoder sees test-fold labels.
