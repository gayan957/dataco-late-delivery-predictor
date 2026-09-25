from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

DATE_COL = "order date (DateOrders)"
DATE_FMT = "%m/%d/%Y %H:%M"

# 'Customer Country' (where the customer lives) and 'Order Country' (where the order is
# shipped) are spelled differently in the raw data, so map one spelling onto the other
# before comparing them.
CUSTOMER_TO_ORDER_COUNTRY = {"EE. UU.": "Estados Unidos", "Puerto Rico": "Puerto Rico"}


class DateFeatures(BaseEstimator, TransformerMixin):
    """Calendar features from the order timestamp."""

    names = ["order_weekday", "order_month", "order_hour", "order_quarter", "is_weekend"]

    def __init__(self, date_col=DATE_COL, date_format=DATE_FMT):
        self.date_col = date_col
        self.date_format = date_format

    def fit(self, X, y=None):
        return self  # nothing to learn

    def transform(self, X):
        d = pd.to_datetime(X[self.date_col], format=self.date_format, errors="coerce")
        return pd.DataFrame(
            {
                "order_weekday": d.dt.weekday,  # 0 = Monday
                "order_month": d.dt.month,
                "order_hour": d.dt.hour,
                "order_quarter": d.dt.quarter,
                "is_weekend": (d.dt.weekday >= 5).astype(int),
            },
            index=X.index,
        )

    def get_feature_names_out(self, input_features=None):
        return np.array(self.names)


class OrderFeatures(BaseEstimator, TransformerMixin):
    """Size of the order, computed from the rows (items) of the same order only."""

    names = ["order_items", "order_total_sales", "order_n_products"]

    def __init__(self, group_col="Order Id", sales_col="Sales", product_col="Product Name"):
        self.group_col = group_col
        self.sales_col = sales_col
        self.product_col = product_col

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        g = X.groupby(self.group_col)
        return pd.DataFrame(
            {
                "order_items": g[self.group_col].transform("size"),
                "order_total_sales": g[self.sales_col].transform("sum"),
                "order_n_products": g[self.product_col].transform("nunique"),
            },
            index=X.index,
        )

    def get_feature_names_out(self, input_features=None):
        return np.array(self.names)


class GeoFeatures(BaseEstimator, TransformerMixin):
    """is_domestic = 1 when the order is shipped to the customer's own country."""

    names = ["is_domestic"]

    def __init__(self, customer_country_col="Customer Country", order_country_col="Order Country"):
        self.customer_country_col = customer_country_col
        self.order_country_col = order_country_col

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        cust = X[self.customer_country_col]
        cust = cust.map(CUSTOMER_TO_ORDER_COUNTRY).fillna(cust)
        return pd.DataFrame(
            {"is_domestic": (cust == X[self.order_country_col]).astype(int)},
            index=X.index,
        )

    def get_feature_names_out(self, input_features=None):
        return np.array(self.names)
