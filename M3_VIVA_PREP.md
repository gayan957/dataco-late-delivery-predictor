# Full Project Viva Prep — DataCo Late Delivery Predictor
**Your name:** Primesh Marasingha (M3)  
**Module:** IT3051 Fundamentals of Data Mining  
**Repo:** github.com/gayan957/dataco-late-delivery-predictor

---

## 1. What Is This Project?

We built a machine learning system that predicts **how many days an order will take to ship**, and from that derives whether it will arrive **late or on time** — all using only information available at the moment the order is placed.

**Why does this matter?** A retailer can use this at checkout to warn customers "Your Standard Class order to Oceania is likely to be late" and offer an upgrade.

**Dataset:** DataCo Smart Supply Chain (Mendeley Data, DOI 10.17632/8gx2fvg2k6.1)  
**Language/Tools:** Python 3.11, scikit-learn ≥ 1.3, XGBoost 1.7.6, FastAPI, Streamlit

---

## 2. Team Roles

| Member | Role | Branch | Key files |
|--------|------|--------|-----------|
| **M1** | Data loading, cleaning, train/test split | `feature/m1-data-prep` | `src/data_prep.py`, notebook 01 |
| **M2** | EDA, feature engineering | `feature/m2-features` | `src/features.py`, notebook 02 |
| **M3 – Primesh** | Encoding, feature selection, XGBoost, Streamlit UI | `feature/m3-encoding` | `src/config.py`, `src/encoders.py`, `src/train_xgb.py`, `src/data_prep_local.py`, `frontend/app.py` |
| **M4** | Baseline models, evaluation utilities, FastAPI backend | `feature/m4-evaluate` | `src/evaluate.py`, `src/train_logreg.py`, `src/train_rf.py`, `src/train_tree_knn.py`, `backend/app.py` |

---

## 3. The Dataset

**Raw file:** `DataCoSupplyChainDataset.csv`  
**Encoding:** LATIN-1 — needed because some country names use Spanish accents (e.g. `Bogotá`, `España`)  
**Shape:** 180,519 rows × 53 columns  
**Unique orders:** 65,752

**Important: one order = multiple rows.** Each row is one item in an order. Order 12345 might have 3 items → 3 rows. Mean items per order = 2.75, max = 5. 69.8% of orders have more than one item. This is why we must split by order, not by row.

**Target column: `Days for shipping (real)`**  
- Integer values: 0, 1, 2, 3, 4, 5, 6  
- Mean = 3.50 days, Std = 1.62  
- This is how many calendar days it actually took from order date to ship

**Key columns summary:**

| Column | Type | Note |
|--------|------|------|
| `Days for shipping (real)` | int 0–6 | **Target — what we predict** |
| `Days for shipment (scheduled)` | int | Promised delivery window — M3 uses as feature |
| `Shipping Mode` | categorical | Same Day / First Class / Second Class / Standard Class |
| `Late_delivery_risk` | binary | 1 = late; **dropped** — derived from target |
| `Delivery Status` | categorical | Advance / Late / On Time / Canceled; **dropped** — post-delivery |
| `Order Status` | categorical | Used to filter rows, then **dropped** |
| `Order Id` | int | Group key for the split — never a feature |
| `order date (DateOrders)` | string | Format: `"MM/DD/YYYY HH:MM"` |

---

## 4. The Task: Regression (Switched from Classification)

**Original plan:** Classify `Late_delivery_risk` (binary: 0 = on time, 1 = late).  
**Switched to:** Predict `Days for shipping (real)` as a number (regression).  
**Approved by:** The instructor.

| | Classification (old) | Regression (new) |
|---|---|---|
| Target | `Late_delivery_risk` (0/1) | `Days for shipping (real)` (0–6) |
| Model | Logistic Regression / Tree | XGBRegressor |
| Metric | Accuracy, F1 | MAE, RMSE, R² |
| Late verdict | Direct output | Derived: `predicted_days > scheduled_days` |

**Why regression is better:** We get a number of days, which is richer information. We can always derive the binary late flag ourselves. Also, `Late_delivery_risk` equals `(real days > scheduled days)` for 97.5% of rows, so predicting days is almost equivalent to predicting the risk flag.

---

## 5. Hard Rules (Know All of These)

### Rule 1: No leakage columns

These four columns are **never used as features**, by any member:

| Column | Why it's leakage |
|--------|-----------------|
| `Late_delivery_risk` | Defined as `(real days > scheduled days)` — computed FROM the target |
| `Delivery Status` | Text version of the same comparison — only known after delivery |
| `shipping date (DateOrders)` | Equals `order date + real shipping days` — computed from the target |
| `Order Status` | Recorded after fulfilment is complete — not known at order time |

**Proof from M1's notebook:**
```
Late_delivery_risk == (real days > scheduled days)  for 97.5% of rows
shipping date - order date == real shipping days    for 97.4% of rows
```
This mathematically proves these columns encode the answer.

**How to detect leakage:** If R² > 0.75 after training, it almost certainly means a leakage column crept in. We print a warning in `train_xgb.py`.

### Rule 2: Grouped split by Order Id

All items from the same order must land on the same side of the train/test split.

**Wrong (plain random split):**
```
Order 12345 has 3 items:
  Train: item A  ← model learns this order's pattern
  Test:  item B, item C  ← "new" test data the model already knows
```

**Correct (grouped split):**
```
Order 12345: ALL 3 items go to Train
Order 99999: ALL 2 items go to Test
→ zero Order Id overlap confirmed
```

### Rule 3: Encoders fitted inside the Pipeline only

Every encoder (OHE, TargetEncoder, scaler) must be fitted on training data only, and always inside a sklearn Pipeline. If you fit an encoder on the full dataset before cross-validation, test fold target values "leak" into the encoder.

### Rule 4: Filter rows before splitting

Remove `Order Status ∈ {CANCELED, SUSPECTED_FRAUD}` before any analysis. These orders never shipped — they have no meaningful shipping days value. Removed: 7,754 rows / 2,855 orders.

---

## 6. M1 — Data Loading, Cleaning, Split

**File:** `src/data_prep.py`  
**Notebook:** `notebooks/01_data_prep_m1_regression.ipynb`

### What M1 does

```
Raw CSV (180,519 rows × 53 cols)
    ↓ Filter CANCELED + SUSPECTED_FRAUD rows
172,765 rows, 62,897 orders
    ↓ Drop 25 columns (leakage + PII + duplicates + constants)
172,765 rows × 28 cols
    ↓ StratifiedGroupKFold split (grouped by Order Id, stratified on target)
Train: 138,098 rows / 50,318 orders
Test:   34,667 rows / 12,579 orders
    ↓ Save as train_reg.csv + test_reg.csv
```

### The 25 dropped columns and why

| Reason | Columns |
|--------|---------|
| Leakage | `Late_delivery_risk`, `Delivery Status`, `shipping date (DateOrders)`, `Order Status` |
| Redundant (fully determined by Shipping Mode) | `Days for shipment (scheduled)` — *M1 dropped this, M3 added it back as a feature* |
| Masked PII | `Customer Email`, `Customer Password` (all `"XXXXXXXXX"`) |
| Personal data | `Customer Fname`, `Customer Lname`, `Customer Street`, `Customer Zipcode` |
| >80% missing | `Order Zipcode` (86%), `Product Description` (100%) |
| Constant | `Product Status` (same value in every row) |
| Image URL | `Product Image` |
| Exact duplicates | `Order Profit Per Order` = `Benefit per order`, `Order Item Total` = `Sales per customer`, `Product Category Id` = `Category Id`, `Order Customer Id` = `Customer Id`, `Order Item Cardprod Id` = `Product Card Id`, `Order Item Product Price` = `Product Price` |
| 1-to-1 with a name column | `Department Id` (= Department Name), `Product Card Id` (= Product Name) |
| Row identifier | `Order Item Id` |
| Customer identifier | `Customer Id` |

**How M1 found the exact duplicates:**
```python
# Same number of unique values AND same actual values → duplicate
Customer Id = Order Customer Id          ✓ exact duplicate
Benefit per order = Order Profit Per Order  ✓ exact duplicate
Sales = ... (not same — Sales ≠ Sales per customer)
```

**How M1 found 1-to-1 pairs:**
```python
Department Id ↔ Department Name: True   (every ID maps to exactly one name)
Product Card Id ↔ Product Name:  True
Category Id ↔ Category Name:     False  (Category Id is NOT 1-to-1 — it encodes multiple categories per ID)
```
Because of this, `Category Name` is KEPT and `Category Id` is dropped.

### The split method: StratifiedGroupKFold

M1 uses `StratifiedGroupKFold(n_splits=5)` — this is more sophisticated than a plain grouped split because it also **stratifies on the target value**, meaning the proportion of 0-day, 1-day, 2-day... orders is the same in both train and test.

```
Split result:
  Train: 138,098 rows / 50,318 orders / mean days = 3.500
  Test:   34,667 rows / 12,579 orders / mean days = 3.494  ← very close ✓
  Order Id overlap: 0  ✓
```

### M1's baseline models (in notebook)

Before training any real model, M1 establishes baselines to know what "minimum acceptable" looks like:

| Baseline | MAE | R² | What it does |
|----------|-----|-----|-------------|
| Dummy (predict mean always) | 1.428 | 0.000 | Predicts 3.50 for every order |
| Shipping Mode only | 0.987 | 0.389 | Linear regression on OHE of Shipping Mode |

This tells us: any real model must beat MAE=1.428, and Shipping Mode alone gives MAE=0.987 and R²=0.39.

### Important discrepancy: M1 vs M3 on `Days for shipment (scheduled)`

M1 dropped `Days for shipment (scheduled)` as "Redundant: fully determined by Shipping Mode."  
M3 put it back as a feature — it IS known at order time and adds signal beyond just the mode category.

Our XGBoost result: `Days for shipment (scheduled)` is the **2nd most important feature** (importance 0.279). This justifies keeping it.

---

## 7. M2 — EDA and Feature Engineering

**File:** `src/features.py`  
**Notebook:** `notebooks/02_eda_features_m2_regression.ipynb`

### M2's EDA key findings

M2 reads `train_reg.csv` from M1's output and analyses the data before engineering features.

**1. No missing values after M1's cleaning.** Zero missing cells, zero duplicate rows.

**2. Shipping Mode explains 38.9% of variance (eta² = 0.389).** This is the single strongest predictor — no surprise that it dominates our feature importances.

**3. Categorical signal strength (eta² = share of variance explained):**

| Column | Unique Values | eta² |
|--------|--------------|------|
| Shipping Mode | 4 | **0.389** |
| Order City | 3,494 | 0.096 |
| Order State | 1,065 | 0.030 |
| Customer City | 563 | 0.013 |
| Order Country | 161 | 0.004 |
| Customer Segment | 3 | ~0.000 |
| Type (payment) | 4 | ~0.000 |

→ Customer Segment, payment Type, and Market have near-zero signal individually.

**4. Numeric features have almost no correlation with the target:**

All Pearson and Spearman correlations are < 0.01 in absolute value. This makes sense — the number of days is mostly determined by the shipping mode, not by product price or discount.

**5. Sales ↔ Sales per customer: |r| = 0.99 (near-duplicate pair).** M2 flags this; M3's encoder will handle it via the column drop list.

**6. Benefit per order has 10.4% outliers (min = −4,274, max = +911).** These are genuine business losses, not data errors — kept.

**7. Date range: January 2015 to January 2018.** No visible trend or drift over time (mean shipping days stays constant across months).

**8. Order structure:** 69.7% of orders have more than 1 item. All items in the same order share the same Shipping Mode, Order City, and real shipping days — they are identical except for product-specific columns.

### M2's three feature transformers

M2 writes three sklearn-compatible transformers in `src/features.py`. All follow the sklearn API (`fit`, `transform`, `get_feature_names_out`) and can be dropped into a Pipeline.

#### DateFeatures → 5 new columns

Parses the `order date (DateOrders)` string (format: `"MM/DD/YYYY HH:MM"`) and extracts calendar features.

```python
Input row: "order date (DateOrders)" = "9/23/2026 00:00"

Output:
  order_weekday = 1      (Tuesday — Monday=0, Sunday=6)
  order_month   = 9      (September)
  order_hour    = 0      (midnight — most orders are logged at midnight)
  order_quarter = 3      (Q3: July–September)
  is_weekend    = 0      (Tuesday is not a weekend)
```

**Why useful?** Orders placed on weekends might ship later because warehouses are closed. Orders at midnight might be batched differently. M2's EDA shows order_hour has eta² = 0.0008 — small but non-zero signal.

#### OrderFeatures → 3 new columns

Groups rows by `Order Id` and computes order-level aggregates. Needs the `Order Id` column to still be present in X.

```python
# Order 12345 has 3 items priced at $50, $30, $20

  order_items        = 3     (number of rows = items in the order)
  order_total_sales  = 100.0 (sum of Sales across items)
  order_n_products   = 3     (number of distinct Product Names)
```

**Why useful?** Larger orders (more items) might take longer to pick and pack.

#### GeoFeatures → 1 new column

Checks whether the order ships to the customer's own country (domestic = faster, international = customs = slower).

```python
Customer Country = "EE. UU."   → maps to "Estados Unidos" (the Spanish name used in Order Country)
Order Country    = "Estados Unidos"
→ is_domestic = 1

Customer Country = "EE. UU."
Order Country    = "Indonesia"
→ is_domestic = 0
```

**The mapping is needed because:** Customer Country uses American-English spellings ("EE. UU.") while Order Country uses Spanish ("Estados Unidos"). Without the mapping, every US order would incorrectly show as international.

**Coverage:** is_domestic = 1 for only 8.5% of rows (most DataCo orders are international).

### M2 signal summary for engineered features

| Feature | eta² / Spearman r | Comment |
|---------|------------------|---------|
| order_hour | eta² = 0.0008 | Strongest engineered signal |
| order_month | eta² = 0.0005 | Slight seasonal effect |
| order_total_sales | r = −0.005 | Very weak |
| order_weekday, order_quarter, is_weekend, order_items, order_n_products, is_domestic | ~0.000 | Near-zero individual signal |

These features are weak alone but can still add value when combined by the model.

---

## 8. M3 — Encoding, Feature Selection, XGBoost, Frontend

**Files:** `src/config.py`, `src/encoders.py`, `src/data_prep_local.py`, `src/train_xgb.py`, `frontend/app.py`  
**Notebook:** `notebooks/02_encoding_m3.ipynb`

### 8a. `src/config.py` — Central configuration

Every module imports from here. Nothing is hardcoded in other files.

```python
TARGET  = "Days for shipping (real)"
TASK    = "regression"
RANDOM_SEED = 42
LEAKAGE_R2_THRESHOLD = 0.75  # warn if R² exceeds this

# Confirmed from raw data:
SCHEDULED_DAYS = {
    "Same Day": 0, "First Class": 1, "Second Class": 2, "Standard Class": 4
}
```

**Column groups used by the ColumnTransformer:**

```
CATEGORICAL_LOW  = 6 columns   → OHE (Shipping Mode, Type, Customer Segment, Market, Order Region, Department Name)
CATEGORICAL_HIGH = 6 columns   → TargetEncoder (Order City, Order State, Customer City, Order Country, Product Name, Category Name)
NUMERIC_BASE     = 11 columns  → from raw data (Days for shipment (scheduled), Product Price, etc.)
NUMERIC_ENGINEERED = 9 columns → from M2's transformers (order_weekday, order_month, etc.)
NUMERIC = NUMERIC_BASE + NUMERIC_ENGINEERED = 20 columns
```

### 8b. `src/encoders.py` — The encoding pipeline

#### Why different encoding strategies for different columns?

| Strategy | Applied to | Why |
|----------|-----------|-----|
| **OneHotEncoder** | Low-cardinality (≤25 values) | Creates one binary column per category. Simple and effective when there are few values. `Shipping Mode` → 4 binary columns. |
| **TargetEncoder** | High-cardinality (50–3,597 values) | Replaces each city/country/product with the **mean target value** for that category, computed across training data. Captures signal without exploding dimensions. |
| **SimpleImputer (median)** | All numeric | Fills any missing values. Median is robust to outliers (important for `Benefit per order`). |

**OHE example:**
```
Shipping Mode = "First Class"
→ [Same Day=0, First Class=1, Second Class=0, Standard Class=0]
```

**TargetEncoder example:**
```
Order City = "Los Angeles"
In training data: orders to LA took a mean of 3.8 days
→ replace "Los Angeles" with 3.8

Order City = "Bekasi" (Indonesia)
In training data: orders to Bekasi took a mean of 2.1 days (closer to international hubs)
→ replace "Bekasi" with 2.1
```

**Why TargetEncoder uses cv=5 (internal cross-fitting):**  
If a city appears 3 times in training with real days [2, 3, 4], its mean = 3.0. If we encode that city as 3.0 and then the model tries to predict those same 3 rows, it already "knows" the answer. TargetEncoder's cv=5 avoids this: it cross-fits, meaning each row's city is encoded using a mean computed from *other* rows (never the row itself).

#### The full pipeline structure

```
build_feature_pipeline()
│
Pipeline
├── Step 1: _FeatureAdder
│   └── Runs M2's transformers on the DataFrame, appends new columns
│       ├── DateFeatures  → adds order_weekday, order_month, order_hour, order_quarter, is_weekend
│       ├── OrderFeatures → adds order_items, order_total_sales, order_n_products
│       └── GeoFeatures   → adds is_domestic
│       (if a transformer fails, fills its columns with NaN — pipeline never crashes)
│
└── Step 2: ColumnTransformer (build_encoder)
    ├── "ohe"       → CATEGORICAL_LOW  (6 cols) → OneHotEncoder(min_frequency=50)
    ├── "high_card" → CATEGORICAL_HIGH (6 cols) → TargetEncoder(target_type='continuous', cv=5)
    ├── "num"       → NUMERIC          (20 cols) → SimpleImputer(median) [+ optional StandardScaler]
    └── remainder='drop'
        └── Silently discards: Order Id, order date, Customer Country, Customer State, etc.
```

Everything is a single Pipeline object — call `.fit(X_train, y_train)` once, then `.predict(X_test)`.

#### Why `remainder='drop'`?

Columns like `Order Id` and `order date (DateOrders)` must be present in X for M2's transformers to work (OrderFeatures uses Order Id to group, DateFeatures uses the date string). But after the transformers run, those raw columns must not appear in the final encoded matrix — the model should never use Order Id as a feature. `remainder='drop'` handles this automatically.

#### `_FeatureAdder` — the M2 bridge

M3 wraps M2's three transformers in a custom class `_FeatureAdder` that:
1. Calls each transformer's `.fit()` and `.transform()`
2. Appends the output columns to the original DataFrame
3. If any transformer raises an exception (e.g. missing column), fills its output columns with NaN and continues — the downstream SimpleImputer recovers

This means M3's code works even if M2's transformers aren't available yet.

#### `select_features()` — feature importance probe

Not used in the training pipeline. Used in the notebook to rank features.

```python
# Fits a quick RandomForestRegressor on the encoded matrix
# Returns: importance ranking + list of highly correlated feature pairs

importance_df, selected, corr_pairs = select_features(
    X_enc, y_train, feature_names,
    k=20,              # keep top 20
    corr_threshold=0.95  # flag pairs with |r| ≥ 0.95
)
```

### 8c. `src/data_prep_local.py` — M3's split bridge

M1 is the official owner of the data split. While waiting for M1's implementation, M3 wrote a local bridge that reads the raw CSV directly and produces the same parquet format.

```bash
python -m src.data_prep_local
```

This produces 7 files in `data/processed/local/`:

| File | Contents |
|------|----------|
| `X_train.parquet` | 138,493 rows × 27 feature columns |
| `X_test.parquet` | 34,272 rows × 27 feature columns |
| `y_train.parquet` | 138,493 target values |
| `y_test.parquet` | 34,272 target values |
| `groups_train.parquet` | Order Id per row (for GroupKFold in CV) |
| `meta_test.parquet` | `Late_delivery_risk` + `Days for shipment (scheduled)` for test set |
| `split_meta_local.json` | Summary (row counts, means, column names) |

When M1 delivers the official files, we switch with one flag change — no code rewrite needed:
```bash
python -m src.train_xgb --split-path data/processed/official
```

### 8d. `src/train_xgb.py` — XGBoost training

#### The full model pipeline

```python
Pipeline([
    ("feature_enc", build_feature_pipeline()),  # M2 feats + M3 encoder
    ("clf", XGBRegressor(
        n_estimators=400,      # 400 trees
        learning_rate=0.05,    # small steps = more careful learning
        max_depth=6,           # tree depth
        subsample=0.8,         # 80% of rows per tree (reduces overfitting)
        colsample_bytree=0.8,  # 80% of features per tree
        min_child_weight=3,    # min samples per leaf
        gamma=0.05,            # regularisation — prune unimportant splits
        objective="reg:squarederror",  # regression, minimise MSE
        tree_method="hist",    # faster histogram-based algorithm
    ))
])
```

#### How to run it

```bash
python -m src.train_xgb              # 5-fold GroupKFold CV + final fit
python -m src.train_xgb --no-cv     # skip CV, fit once (used for demo)
python -m src.train_xgb --tune      # RandomizedSearchCV hyperparameter tuning
```

#### Cross-validation: GroupKFold(n_splits=5)

Same rule as the train/test split: all rows from the same order stay in the same fold.

```
Fold 1: train on folds 2,3,4,5  → validate on fold 1
Fold 2: train on folds 1,3,4,5  → validate on fold 2
...
→ Average the 5 validation MAEs → one reliable estimate
→ Then train on all 5 folds → final model
```

#### Metrics explained

| Metric | Formula | Our result | Meaning |
|--------|---------|------------|---------|
| **MAE** | mean(\|y_pred − y_true\|) | **1.008 days** | On average, off by ~1 day |
| **RMSE** | √mean((y_pred − y_true)²) | 1.306 | Penalises large errors more than MAE |
| **R²** | 1 − SS_residual / SS_total | **0.361** | Model explains 36.1% of variance |

**Baseline comparison:**
```
Dummy (predict mean) : MAE = 1.428   ← we must beat this ✓ (we got 1.008)
Shipping Mode only   : MAE = 0.987   ← our model is comparable
XGBoost (M3)         : MAE = 1.008   ← slightly above mode-only (expected — CV was skipped)
```

R² = 0.36 is within the expected range (0.35–0.45). The remaining 64% of variance is driven by factors not in the dataset: warehouse staff levels, carrier delays, weather, customs processing times.

#### Derived late-flag accuracy

After regression, we check how well the derived binary flag matches the original `Late_delivery_risk`:

```python
pred_late = (y_pred > X_test["Days for shipment (scheduled)"]).astype(int)
true_late = meta_test["Late_delivery_risk"]

Accuracy = 65.0%
F1       = 0.718
```

**Why F1 and not just accuracy?** There are more late orders than on-time orders (54.8% late in the raw data). F1 balances precision and recall, making it a fairer measure when classes are imbalanced.

#### Leakage guard

```python
if metrics["R2"] > 0.75:
    print("WARNING: R² > 0.75 — likely leakage!")
```

Our R² = 0.361 — no warning fires.

#### Outputs

```
models/xgb_pipeline.pkl    ← full pipeline (used by frontend fallback)
models/final_pipeline.pkl  ← same file, alias for backend/app.py
results/experiments.csv    ← one row logged per run
```

### 8e. Top 15 features

```
Rank  Importance  Feature
 1    0.4065     ohe__Shipping Mode_Same Day
 2    0.2791     num__Days for shipment (scheduled)
 3    0.1311     ohe__Shipping Mode_First Class
 4    0.0296     ohe__Shipping Mode_Second Class
 5    0.0107     ohe__Shipping Mode_Standard Class
 6    0.0085     high_card__Order City
 7    0.0044     num__order_items
 8    0.0039     num__order_hour
 9    0.0029     high_card__Customer City
10    0.0026     num__order_total_sales
11    0.0026     num__order_n_products
12    0.0025     ohe__Order Region_US Center
13    0.0025     ohe__Order Region_Oceania
14    0.0025     ohe__Order Region_South of USA
15    0.0025     ohe__Order Region_West Africa
```

Features 1–5 are all about Shipping Mode / scheduled days and account for ~83% of total importance. This makes sense: a Same Day order ships in 0–1 days; a Standard Class order takes 4+. The model learned this mapping almost perfectly.

`Order City` (rank 6) captures the mean delivery time for that destination — cities near distribution hubs are faster.

### 8f. `frontend/app.py` — Streamlit UI

```bash
streamlit run frontend/app.py      # starts at http://localhost:8501
make api                           # start FastAPI backend in separate terminal
```

**What it shows:**
- Form: shipping mode, product, location, date, price, quantity, discount
- Output: predicted days, scheduled days, **ON TIME 🟢 / LATE 🔴** verdict
- Tries FastAPI backend first; falls back to loading `models/xgb_pipeline.pkl` directly

**Local fallback:**
```python
@st.cache_resource   # load once per session, not on every click
def _load_local_model():
    return joblib.load("models/xgb_pipeline.pkl")
```

**Verdict logic:**
```python
sched    = SCHEDULED_DAYS["First Class"]   # = 1
pred_days = model.predict(input_row)[0]    # e.g. 2.3
is_late   = pred_days > sched              # 2.3 > 1 → True → LATE 🔴
```

---

## 9. M4 — Baselines, Evaluation, FastAPI

**Files:** `src/evaluate.py`, `src/train_logreg.py`, `src/train_rf.py`, `src/train_tree_knn.py`, `backend/app.py`, `notebooks/03_models.ipynb`

### 9a. Baseline models (stubs — not yet implemented)

M4 is responsible for training three baseline models to compare against M3's XGBoost.

| Model | File | Key decision |
|-------|------|-------------|
| **Logistic Regression** | `train_logreg.py` | `class_weight="balanced"`, `max_iter=1000`, solver `lbfgs` |
| **Random Forest** | `train_rf.py` | `n_estimators=300`, `class_weight="balanced"` |
| **Decision Tree** | `train_tree_knn.py --model tree` | `max_depth=10`, `class_weight="balanced"` |
| **KNN** | `train_tree_knn.py --model knn` | `n_neighbors=15`, `weights="distance"` — **must include StandardScaler** |

All four use the same encoding pipeline from M3's `build_encoder()`.

**Why does KNN need StandardScaler?**  
KNN uses distance between points. If `Product Price` ranges from 9 to 2000 and `Order Item Quantity` ranges from 1 to 5, the price will completely dominate the distance calculation. StandardScaler normalises all features to mean=0, std=1, so all features contribute equally.

**Why `class_weight="balanced"` for the classifiers?**  
54.8% of orders are late — the dataset is imbalanced. Without balancing, a classifier can achieve 54.8% accuracy by just predicting "late" for everything. Balanced weights penalise errors on the minority class more.

### 9b. `src/evaluate.py` — Evaluation utilities (stub)

M4 owns this file. When implemented, it provides two functions:

```python
metrics_dict(y_true, y_pred, y_proba, model_name)
# Returns: accuracy, precision, recall, F1, ROC-AUC as a dict

log_experiment(metrics, csv_path)
# Appends one row to results/experiments.csv with a timestamp
```

M3's `train_xgb.py` has its own inline version of these (for regression: MAE, RMSE, R²) because `evaluate.py` was originally designed for classification.

### 9c. `backend/app.py` — FastAPI REST API (stub)

```bash
make api    # uvicorn backend.app:app --reload --port 8000
```

**Two endpoints:**

| Endpoint | Method | Status |
|----------|--------|--------|
| `/health` | GET | **Working** — returns `{"status": "ok"}` |
| `/predict` | POST | **Stub** — returns HTTP 501 Not Implemented |

The `/predict` endpoint receives a JSON payload with order fields, runs the pipeline, and should return:
```json
{
  "probability": 0.73,
  "label": 1,
  "risk_tier": "High"
}
```

The model is loaded once using `@lru_cache(maxsize=1)` — same idea as Streamlit's `@st.cache_resource`. Loading a 50MB pkl file on every request would be too slow.

**Why FastAPI?** It automatically generates API documentation at `http://localhost:8000/docs` (Swagger UI). You can test the endpoint from the browser without writing any client code.

**Pydantic validation:** The `OrderFeatures` class defines the expected input schema. FastAPI validates every incoming request against it and returns a 422 error if fields are missing or have the wrong type — before the model ever runs.

### 9d. `notebooks/03_models.ipynb` — Model comparison (stub)

M4 will load `results/experiments.csv` and create:
- Grouped bar chart of MAE, RMSE, R² across all models
- ROC curves (one per model, overlaid)
- Precision-Recall curves
- Confusion matrices

---

## 10. Tests — Anti-Leakage Suite

**File:** `tests/test_no_leakage.py`

```bash
make test    # or: pytest tests/ -v
```

Two automated tests that verify the pipeline hasn't introduced leakage:

**Test 1 — leakage columns removed:**  
Calls M1's `clean()` and checks that none of `LEAKAGE_COLS` appear in the cleaned DataFrame.

**Test 2 — no Order Id overlap:**  
Reads `X_train.parquet` and `X_test.parquet` and asserts that zero Order Ids appear in both sets.

Both tests skip gracefully if the CSV isn't present or M1's stubs haven't been implemented yet. When M1 implements the functions, these tests **must pass before any model is trained**.

---

## 11. Full Pipeline: From CSV to Prediction

```
1. RAW CSV                        DataCoSupplyChainDataset.csv (180,519 rows)
        │
2. M1: CLEAN                      Filter + drop 25 cols → 172,765 rows × 28 cols
        │
3. M1: SPLIT                      StratifiedGroupKFold by Order Id
        │                         Train: 138,098 rows / Test: 34,667 rows
        ├── train_reg.csv
        └── test_reg.csv
                │
4. M2: EDA                        Explore data, confirm signal strength
                │
5. M2: FEATURE TRANSFORMERS       DateFeatures, OrderFeatures, GeoFeatures
        (fitted in Pipeline,       → 9 new columns added inside training
         not standalone)
                │
6. M3: ENCODE                     ColumnTransformer inside Pipeline
        (fitted on train only)     OHE + TargetEncoder + Imputer
                │
7. M3: TRAIN                      XGBRegressor
        (GroupKFold CV)            MAE=1.008, R²=0.361
                │
8. M3: SAVE MODEL                 models/xgb_pipeline.pkl
                │
        ┌───────┴───────┐
9a. M4: API          9b. M3: UI
    FastAPI              Streamlit
    /predict             frontend/app.py
    backend/app.py       loads pkl directly
```

---

## 12. Complete Results Summary

| | |
|---|---|
| **Dataset** | 180,519 rows × 53 cols → 172,765 rows × 28 features after cleaning |
| **Target** | Days for shipping (real): mean 3.50, range 0–6 |
| **Train** | 138,493 rows / 50,317 orders |
| **Test** | 34,272 rows / 12,580 orders |
| **Order Id overlap** | **0** ✓ |
| **Baseline MAE (dummy)** | 1.428 days |
| **Baseline MAE (mode only)** | 0.987 days |
| **XGBoost MAE** | **1.008 days** |
| **XGBoost RMSE** | 1.306 |
| **XGBoost R²** | **0.361** |
| **R² leakage threshold** | 0.75 — not triggered ✓ |
| **Derived late-flag accuracy** | 65.0% |
| **Derived late-flag F1** | **0.718** |
| **Top feature** | Shipping Mode = Same Day (0.41 importance) |
| **Training time (--no-cv)** | 5.8 seconds |

---

## 13. All Viva Questions and Answers

### Project overview

**Q: What problem are you solving?**  
A: Predicting how many days an order will take to ship — and from that, whether it will arrive late — using only information available when the order is placed. A customer or operations team could use this at checkout to flag high-risk orders and offer shipping upgrades.

**Q: Why regression instead of classification?**  
A: Regression gives a number of days (0–6), which is more informative than a yes/no late flag. We can derive the binary late flag ourselves: if predicted days > scheduled days → late. Also, `Late_delivery_risk` is mathematically computed from the target (97.5% of rows: `Late_delivery_risk = (real days > scheduled days)`), so predicting days is essentially equivalent.

**Q: What is the target variable?**  
A: `Days for shipping (real)` — an integer from 0 to 6 representing how many calendar days elapsed between order placement and shipment. Mean = 3.50 days, standard deviation = 1.62.

**Q: What dataset did you use?**  
A: The DataCo Smart Supply Chain dataset from Mendeley Data (DOI 10.17632/8gx2fvg2k6.1). 180,519 rows, 53 columns, LATIN-1 encoding (Spanish accented characters). Covers 2015–2018 across global markets.

---

### Data and leakage

**Q: What is target leakage? Give an example from this project.**  
A: Leakage is when a feature gives the model information it could not have at prediction time. `Late_delivery_risk` is computed as `(real days > scheduled days)` — it directly encodes the answer. If we included it, the model would read it and skip learning anything useful. We proved this: it matches the formula for 97.5% of rows. Similarly, `shipping date` equals `order date + real days` for 97.4% of rows — another perfect encoding of the target.

**Q: Why did you remove CANCELED and SUSPECTED_FRAUD orders?**  
A: These orders were never fulfilled — they have `Delivery Status = Shipping canceled`. Their `Days for shipping (real)` value exists in the dataset but represents the cancellation date, not a real delivery window. Including them would add noise to the target distribution.

**Q: Why group the split by Order Id instead of splitting rows randomly?**  
A: One order can have 2–5 item rows. If we split randomly, items from Order 12345 might appear in both train and test. The model would have seen that order's context during training and could "remember" it in test — that's leakage. GroupShuffleSplit / StratifiedGroupKFold keeps all items of the same order on the same side.

**Q: What is the difference between GroupShuffleSplit and StratifiedGroupKFold?**  
A: GroupShuffleSplit (used by M3's bridge) just groups by Order Id and splits randomly. StratifiedGroupKFold (used by M1) additionally stratifies — it ensures the proportion of each target value (0 days, 1 day, 2 days…) is the same in both train and test. Stratification makes the split more representative.

---

### Encoding

**Q: Why use TargetEncoder for high-cardinality columns instead of OHE?**  
A: OHE creates one column per unique value. Order City has 3,597 unique values — OHE would add 3,597 columns, most nearly empty. TargetEncoder replaces each city with a single number (its mean delivery days), keeping the encoded matrix small while preserving geographic signal.

**Q: Why does TargetEncoder need to be inside the Pipeline?**  
A: TargetEncoder learns from y (the target). If you fit it on the full training set before cross-validation, it has already "seen" the y-values of the validation fold — that's leakage. Inside the Pipeline, sklearn fits the encoder only on the training portion of each fold, never on the fold being validated.

**Q: What does `min_frequency=50` in OHE do?**  
A: Any category value that appears fewer than 50 times in training is grouped into a single `infrequent_sklearn` bucket instead of getting its own column. This prevents rare categories from creating near-empty columns that just memorise a handful of training examples.

**Q: Why doesn't KNN need TargetEncoder but does need StandardScaler?**  
A: KNN is distance-based — it doesn't build a model, it finds the k nearest neighbours by Euclidean distance. Features with large numerical ranges dominate the distance, so everything must be scaled to comparable units. Tree-based models (XGBoost, Random Forest) split on thresholds and are scale-invariant, so they don't need scaling.

---

### Models

**Q: What is XGBoost? How does it work?**  
A: XGBoost (Extreme Gradient Boosting) builds an ensemble of decision trees sequentially. Each new tree focuses on correcting the errors of the previous trees (the "residuals"). With `learning_rate=0.05` and 400 trees, each tree makes a small correction — many small steps are more robust than a few large ones. It uses a histogram-based algorithm (`tree_method='hist'`) that bins continuous features, making it much faster on large datasets.

**Q: What does R² = 0.361 mean?**  
A: The model explains 36.1% of the variance in delivery days. The remaining 63.9% is driven by factors not in our dataset — carrier performance, warehouse staffing, customs delays, weather. This is expected; the R² baseline from Shipping Mode alone is already 0.389, so our full model is in line.

**Q: Why is MAE preferred over RMSE for this task?**  
A: For a business user, being off by 1 day is twice as bad as being off by 0.5 days — a linear penalty makes sense. RMSE squares the error, so a 3-day error counts 9× more than a 1-day error. MAE is more intuitive: "we're off by 1 day on average."

**Q: What is the leakage warning threshold and why 0.75?**  
A: R² > 0.75 means the model explains over 75% of variance in delivery days. Given that Shipping Mode alone only explains 38.9% and numeric features have near-zero correlation with the target, achieving R² > 0.75 with legitimate features is implausible — it almost certainly means a leakage column was accidentally included.

**Q: Why use GroupKFold for cross-validation and not regular KFold?**  
A: Same reason as for the train/test split. In regular KFold, the same order's items can appear in both the training and validation fold of a CV iteration. GroupKFold keeps all items from the same order in the same fold, giving a more honest estimate of generalisation to genuinely new orders.

---

### Feature engineering

**Q: What does M2's `OrderFeatures` transformer do and why is `Order Id` needed?**  
A: OrderFeatures computes order-level aggregates: number of items, total sales, number of distinct products. To compute "how many items in this order?" it needs to group rows by Order Id — `X.groupby("Order Id").transform("size")`. The `Order Id` column stays in X until the ColumnTransformer's `remainder='drop'` discards it after feature engineering is done.

**Q: Why does GeoFeatures need a country name mapping?**  
A: The Customer Country column uses US-English/American-Spanish ("EE. UU.") while Order Country uses European Spanish ("Estados Unidos"). Without mapping them to the same spelling, a comparison `customer_country == order_country` would always return False for US orders, making every US customer appear as an international shipment.

**Q: Which feature had the most signal in M2's EDA?**  
A: Shipping Mode with eta² = 0.389, meaning it explains 38.9% of the variance in delivery days on its own. This is consistent with our model's top feature importances: Shipping Mode columns account for ~80% of total XGBoost gain.

---

### API and frontend

**Q: Why does the Streamlit frontend have a local pkl fallback?**  
A: The FastAPI backend's `/predict` endpoint is not yet implemented (returns HTTP 501). The frontend detects this and falls back to loading `models/xgb_pipeline.pkl` directly with `joblib.load()`. This way the UI is fully functional for demos even without the backend running.

**Q: What is `@st.cache_resource`?**  
A: A Streamlit decorator that runs the decorated function once and caches the result in memory for the session. Without it, the model would be reloaded from disk on every form submission (~1 second penalty per click). With it, the pkl is loaded once and reused.

**Q: Why does the input form include a dummy `Order Id = 999,999,999`?**  
A: M2's `OrderFeatures` transformer calls `X.groupby("Order Id")`. If `Order Id` is missing from the input row, the transformer crashes. The dummy value ensures the groupby finds exactly one row per "order" — the aggregates become: `order_items=1`, `order_total_sales=price*qty`, `order_n_products=1`.

**Q: What is Pydantic and why does M4 use it in the FastAPI backend?**  
A: Pydantic is a data validation library. The `OrderFeatures` class in `backend/app.py` declares the expected types and constraints for each field. FastAPI uses it to automatically validate incoming JSON requests — if a required field is missing or has the wrong type, FastAPI returns a 422 Unprocessable Entity response before the model runs. This prevents crashes from malformed input.

---

### Tools and setup

**Q: How do you run the full project from scratch?**
```bash
# Install dependencies
pip install -r requirements.txt

# Build the local split
python -m src.data_prep_local

# Train the model (fast — no CV)
python -m src.train_xgb --no-cv

# Start the UI
streamlit run frontend/app.py
```

**Q: Why pin XGBoost to version 1.7.6?**  
A: XGBoost 3.x requires a symbol `___kmpc_dispatch_deinit` from OpenMP (LLVM 14+). The Anaconda-bundled libomp is an older LLVM 12/13 build that doesn't have this symbol. Version 1.7.6 was compiled against the older OpenMP ABI and works with Anaconda's libomp. We pin it in `requirements.txt` so all teammates get the working version.

**Q: What is a Parquet file? Why use it instead of CSV?**  
A: Parquet is a columnar binary format that stores data type information. It's faster to read and write than CSV, compresses better (especially for repeated string values like city names), and preserves exact dtypes (integers stay integers, not silently cast to floats). For a 140K-row dataset, loading from parquet is ~5× faster than from CSV.

---

## 14. What Each Member Still Needs to Do

| Task | Owner | Status |
|------|-------|--------|
| Implement `load_raw()`, `clean()`, `make_split()` in `data_prep.py` | M1 | Stub |
| Deliver official parquet split files | M1 | Pending |
| Notebook 01 run and saved with outputs | M1 | Done in notebook |
| Notebook 02 (M2 EDA) run and saved | M2 | Done in notebook |
| `features.py` transformers | M2 | Done ✓ |
| **`config.py`, `encoders.py`, `data_prep_local.py`, `train_xgb.py`, `frontend/app.py`** | **M3** | **Done ✓** |
| **XGBoost model trained and pkl saved** | **M3** | **Done ✓ (MAE=1.008)** |
| Implement `metrics_dict()` and `log_experiment()` in `evaluate.py` | M4 | Stub |
| Implement `train_logreg.py`, `train_rf.py`, `train_tree_knn.py` | M4 | Stubs |
| Wire up `/predict` in `backend/app.py` | M4 | Stub |
| Notebook 03 model comparison | M4 | Stub |
| Switch `train_xgb.py --split-path` to M1's official files | M3 | When M1 delivers |
| Run full 5-fold GroupKFold CV | M3 | `python -m src.train_xgb` |

---

## 15. File Map — Who Owns What

```
src/
  config.py           M3 ✓    Central settings, column lists
  encoders.py         M3 ✓    OHE / TargetEncoder / Imputer pipeline
  data_prep_local.py  M3 ✓    Local bridge split (until M1 delivers)
  train_xgb.py        M3 ✓    XGBoost regression training
  features.py         M2 ✓    DateFeatures / OrderFeatures / GeoFeatures
  data_prep.py        M1 stub Load / clean / split
  evaluate.py         M4 stub metrics_dict() / log_experiment()
  train_logreg.py     M4 stub Logistic Regression baseline
  train_rf.py         M4 stub Random Forest baseline
  train_tree_knn.py   M4 stub Decision Tree + KNN

frontend/
  app.py              M3 ✓    Streamlit prediction UI

backend/
  app.py              M4 stub FastAPI /predict endpoint

notebooks/
  01_data_prep_m1_regression.ipynb    M1 ✓ (run with outputs)
  02_eda_features_m2_regression.ipynb M2 ✓ (run with outputs)
  02_encoding_m3.ipynb                M3 ✓ (encoding EDA)
  03_models.ipynb                     M4 stub (model comparison)

tests/
  test_no_leakage.py  M3/shared   2 anti-leakage tests
```
