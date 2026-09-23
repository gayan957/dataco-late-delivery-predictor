# Owner: M2
"""
Feature engineering: date decomposition, geo-derived features,
and order-level aggregates.

Call build_features(df) to apply all transformations in sequence.
New column names added here should also be registered in src/config.py
(NUMERIC or CATEGORICAL_LOW) so the ColumnTransformer picks them up.
"""
from __future__ import annotations

import pandas as pd
import numpy as np


def add_date_features(
    df: pd.DataFrame,
    date_col: str = "order date (DateOrders)",
) -> pd.DataFrame:
    """
    Extract temporal signals from the order date.

    Adds columns:
        order_month       (1–12)
        order_dayofweek   (0=Mon … 6=Sun)
        order_quarter     (1–4)
        is_weekend        (0/1 — Sat/Sun orders may behave differently)

    Parameters
    ----------
    df       : DataFrame containing date_col
    date_col : name of the datetime column

    Returns
    -------
    pd.DataFrame  with new columns appended (original column kept)
    """
    # TODO M2:
    #   df = df.copy()
    #   dt = pd.to_datetime(df[date_col], errors="coerce")
    #   df["order_month"]     = dt.dt.month
    #   df["order_dayofweek"] = dt.dt.dayofweek
    #   df["order_quarter"]   = dt.dt.quarter
    #   df["is_weekend"]      = dt.dt.dayofweek.isin([5, 6]).astype(int)
    #   return df
    raise NotImplementedError("TODO M2 — parse date and extract temporal features")


def add_geo_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer location-derived features from Latitude/Longitude.

    Suggested additions:
        lat_bin   — discretised latitude band (e.g. 10° bins)
        lon_bin   — discretised longitude band
        dist_to_equator — abs(Latitude)

    Parameters
    ----------
    df : DataFrame with 'Latitude' and 'Longitude' columns

    Returns
    -------
    pd.DataFrame  with new columns appended
    """
    # TODO M2:
    #   df = df.copy()
    #   df["dist_to_equator"] = df["Latitude"].abs()
    #   df["lat_bin"] = pd.cut(df["Latitude"], bins=18, labels=False)
    #   df["lon_bin"] = pd.cut(df["Longitude"], bins=36, labels=False)
    #   return df
    raise NotImplementedError("TODO M2 — add geo-derived features from Lat/Lon")


def add_order_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute order-level aggregates and item-level derived ratios.

    Suggested additions:
        items_per_order       — count of line items sharing the same Order Id
        discount_to_price     — Order Item Discount / Order Item Product Price
        effective_price       — Order Item Product Price * (1 - Order Item Discount Rate)

    Parameters
    ----------
    df : cleaned DataFrame (with 'Order Id', price, discount columns)

    Returns
    -------
    pd.DataFrame  with new columns appended
    """
    # TODO M2:
    #   df = df.copy()
    #   items_count = df.groupby("Order Id")["Order Id"].transform("count")
    #   df["items_per_order"] = items_count
    #   denom = df["Order Item Product Price"].replace(0, np.nan)
    #   df["discount_to_price"] = df["Order Item Discount"] / denom
    #   df["effective_price"]   = df["Order Item Product Price"] * (1 - df["Order Item Discount Rate"])
    #   return df
    raise NotImplementedError("TODO M2 — add order-level aggregate features")


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all feature engineering transformations in sequence.

    Parameters
    ----------
    df : cleaned DataFrame (output of data_prep.clean())

    Returns
    -------
    pd.DataFrame  fully feature-engineered, ready for make_split()
    """
    # TODO M2:
    #   df = add_date_features(df)
    #   df = add_geo_features(df)
    #   df = add_order_features(df)
    #   return df
    raise NotImplementedError(
        "TODO M2 — chain add_date_features → add_geo_features → add_order_features"
    )
