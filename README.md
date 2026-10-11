# DataCo Late Delivery Predictor

**IT3051 Fundamentals of Data Mining – Group Mini-Project 2026**

A machine-learning system that predicts, **at the moment an order is placed**:

- **how many days the order will take to ship** (regression – primary task), and
- **the probability that it will be delivered late** (classification – secondary task).

The models are served through a FastAPI back end and a React web application with Home, EDA, Logistics and Customer pages.

> **Dataset:** DataCo Smart Supply Chain for Big Data Analysis – Constante, F., Silva, F. and Pereira, A. (2019), Mendeley Data, DOI [10.17632/8gx2fvg2k6.1](https://doi.org/10.17632/8gx2fvg2k6.1).
> 180,519 order items × 53 columns, Latin-1 encoded, January 2015 – January 2018.

---

## Results

Both final models are tuned Decision Trees, chosen because they tied with Random Forest and XGBoost on cross-validation and are the simplest to explain. Scores are on the hidden test set, which was used once.

| Task | Target | Final model | Test result | Shipping-mode baseline |
|---|---|---|---|---|
| **Regression** | `Days for shipping (real)` (0–6) | `DecisionTreeRegressor(max_depth=3, min_samples_leaf=50)` | **MAE 0.937 days**, RMSE 1.248, R² 0.402 | MAE 0.963, R² 0.397 |
| Classification | `Late_delivery_risk` (0/1) | `DecisionTreeClassifier(max_depth=5, min_samples_leaf=20, class_weight="balanced")`, threshold 0.65 | **ROC-AUC 0.773**, precision 0.894, recall 0.592, F1 0.712 | ROC-AUC 0.743, F1 0.678 |

**Key findings**

- Shipping mode explains about 39 % of the variation in shipping time.
- First Class always takes 2 days against a 1-day promise, so 100 % of First Class orders are late.
- Same Day orders placed before 11:30 ship the same day; later orders ship the next day.
- Second and Standard Class take 2–6 days, and no order-time feature in the data explains that spread. This is the main limit on accuracy.

---

## Project rules

| Rule | Detail |
|---|---|
| **No leakage** | `Late_delivery_risk`, `Delivery Status`, `shipping date (DateOrders)` and `Order Status` are never used as features – each was proven to encode the answer or to be recorded after shipping. |
| **Grouped split** | All items of an order stay in the same partition: `StratifiedGroupKFold` grouped by `Order Id`, seed 42. Train and test share 0 orders. |
| **Fit on train only** | Every encoder and scaler lives inside a scikit-learn `Pipeline` and is fitted on training folds only. |
| **Exclude never-shipped orders** | `Order Status ∈ {CANCELED, SUSPECTED_FRAUD}` is removed per order (7,754 rows) before any analysis. |
| **Test set used once** | Only the final model is scored on the test set, in notebook 09 / C09. |

---

## Repository structure

```
dataco-late-delivery-predictor/
├── data/
│   ├── raw/DataCoSupplyChainDataset.csv   # source dataset (Latin-1)
│   └── processed/                         # shared train/test split + split metadata
├── notebooks/
│   ├── 01 … 09_*.ipynb                    # regression pipeline
│   └── c01 … c09_*.ipynb                  # classification pipeline
├── models/                                # final pipelines (.pkl, git-ignored) + model_info JSON
├── results/                               # experiment logs and tuned parameters per model
├── reports/
│   ├── figures/                           # every chart from the notebooks
│   └── Technical_Report_*.docx            # Stage 11 technical report
├── backend/app.py                         # FastAPI inference service
├── frontend-web/                          # React + Vite web application
├── frontend/app.py                        # early Streamlit prototype (superseded)
├── tests/test_no_leakage.py               # anti-leakage checks
├── Deliverables/                          # final submission, one folder per required deliverable
├── requirements.txt
└── Makefile
```

### Notebook pipeline

Run the notebooks in order. Each one reads the previous stage's output from `data/processed/` and `results/`.

| # | Regression | Classification | Owner | Purpose |
|---|---|---|---|---|
| 1 | `01_data_prep_m1` | `c01_data_prep_m1` | M1 | Load, prove leakage, clean, grouped split, baselines |
| 2 | `02_eda_features_m2` | `c02_eda_features_m2` | M2 | EDA on the training set, date features |
| 3 | `03_encoding_features_m3` | `c03_encoding_features_m3` | M3 | Encoding comparison, feature selection |
| 4 | `04_scaling_validation_m4` | `c04_validation_scaling_m4` | M4 | Validation scheme, metrics, scaler per model family |
| 5 | `05_model_ridge_m1` | `c05_model_logistic_m1` | M1 | Ridge / Logistic Regression |
| 6 | `06_model_random_forest_m2` | `c06_model_random_forest_m2` | M2 | Random Forest |
| 7 | `07_model_xgboost_m3` | `c07_model_xgboost_m3` | M3 | XGBoost |
| 8 | `08_model_tree_knn_m4` | `c08_model_tree_knn_m4` | M4 | Decision Tree and KNN |
| 9 | `09_model_comparison` | `c09_model_comparison` | Team | Compare, select, test once, save the final pipeline |

### Features

Eleven features, all known at checkout:

| Feature | Encoding |
|---|---|
| Shipping Mode, Market, Customer Segment | One-hot |
| Order Country (161 values), Category Name (50 values) | Target encoding (inside the pipeline) |
| Order Item Quantity | Numeric |
| `order_weekday`, `order_month`, `order_hour`, `order_quarter`, `is_weekend` | Derived from the order date |

---

## Getting started

### Requirements

- Python **3.11**
- Node.js **18+** (for the web app)

### 1. Python environment

```bash
make setup                      # creates .venv and installs requirements.txt
# or: python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

### 2. Trained models

The `.pkl` files in `models/` are git-ignored. Either copy the committed copies:

```bash
cp Deliverables/04_Trained_Final_Model/*.pkl models/
```

or regenerate them by running notebooks `09_model_comparison` and `c09_model_comparison`.

### 3. Start the API (port 8000)

```bash
make api
# or: .venv/bin/uvicorn backend.app:app --reload --port 8000
```

Interactive API documentation: <http://localhost:8000/docs>

### 4. Start the web app (port 5173)

```bash
cd frontend-web
npm install
npm run dev
```

Open <http://localhost:5173>. The Vite dev server forwards `/api/*` to the API on port 8000.

To build a production bundle: `npm run build` (output in `frontend-web/dist/`).

---

## API

| Method & path | Purpose | Response |
|---|---|---|
| `GET /health` | Liveness check | `{"status": "ok"}` |
| `POST /predict` | Regression | `predicted_days`, `scheduled_days`, `is_late`, `late_by`, `shipping_mode` |
| `POST /classify` | Classification | `is_late`, `probability`, `threshold`, `shipping_mode` |
| `POST /predict/combined` | Both models in one call | `{regression, classification}` |

Example request body:

```json
{
  "shipping_mode": "Second Class",
  "market": "LATAM",
  "order_country": "México",
  "category_name": "Cleats",
  "quantity": 2,
  "customer_segment": "Consumer",
  "order_date": "2026-10-05"
}
```

Country and category values use the dataset's original (Spanish) labels. Invalid input returns HTTP 422 with a message.

---

## Web application

| Page | Route | What it shows |
|---|---|---|
| Home | `#/` | DataCo Global background, mission, vision and main services |
| EDA | `#/eda` | 27 report charts in six sections, each with an explanation and key insight; click to enlarge |
| Logistics | `#/predict` | Full order form; separate classification (late-risk gauge) and regression (shipping days) results; model performance tables |
| Customer | `#/customer` | Simple form that returns only the estimated shipping days and date |

Built with React 18, Vite, Tailwind CSS and Framer Motion.

---

## Testing

```bash
make test
```

> **Known issue:** `tests/test_no_leakage.py` still imports a `src/` package that was replaced by the notebooks, so it fails at collection. Its checks (no Order Id overlap between train and test, no leakage columns in the processed files) were verified manually and pass. The test should be updated to read `data/processed/*.csv` directly.

---

## Known limitations

- Shipping time within Second and Standard Class (2–6 days) cannot be explained by order-time features, which caps R² at about 0.40.
- The API accepts a date without a time, so `order_hour` is 0 at inference and afternoon Same Day orders are predicted one day early.
- The `make split` and `make train-xgb*` targets refer to the removed `src/` package; use the notebooks instead.
- The raw dataset is about 91 MB, above GitHub's recommended 50 MB file size; consider Git LFS.

---

## Team

| Member | Responsibility |
|---|---|
| M1 | Data preparation, leakage control, split, Ridge / Logistic Regression |
| M2 | EDA, feature engineering, Random Forest |
| M3 | Encoding, feature selection, XGBoost, model comparison, frontend |
| M4 | Scaling and validation, Decision Tree, KNN, backend |

---

## Deliverables

The `Deliverables/` folder contains the final submission: dataset and citation, dataset proposal and validation evidence, pre-processing and modelling code, trained final models, integrated system source code, technical report, and experiment / evaluation evidence. `Deliverables/00_Deliverables_Index.docx` maps each requirement to its folder.
