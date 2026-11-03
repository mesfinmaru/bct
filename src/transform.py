"""Transformation layer for the financial transaction ETL pipeline.

All functions operate on one chunk at a time so memory usage stays flat for
multi-million row files. The output of every function is a tidy DataFrame
ready to be handed to the load layer.
"""

from __future__ import annotations

import re
from typing import Iterable

import pandas as pd

REQUIRED_NUMERIC = ("deposits", "withdrawals", "balance")
SOURCE_TAG = "BT_20"  # overwritten per chunk by the caller


def _normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace, lowercase names and fix common spelling slips."""
    df = df.copy()
    df.columns = [str(col).strip().lower() for col in df.columns]
    if "withdrawls" in df.columns and "withdrawals" not in df.columns:
        df = df.rename(columns={"withdrawls": "withdrawals"})
    return df


def _clean_description(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing descriptions with 'Other' and strip surrounding whitespace."""
    df = df.copy()
    if "description" not in df.columns:
        df["description"] = "Other"
        return df
    df["description"] = df["description"].fillna("Other").astype(str).str.strip()
    df.loc[df["description"].str.len() == 0, "description"] = "Other"
    return df


def _standardize_date(df: pd.DataFrame) -> pd.DataFrame:
    """Parse the raw 'DD-Mon-YYYY' ledger date into a timezone-free date only."""
    df = df.copy()
    if "date" not in df.columns:
        return df

    parsed = pd.to_datetime(df["date"], format="mixed", errors="coerce")
    bad_mask = parsed.isna()
    bad_values = df.loc[bad_mask, "date"].astype(str).tolist()
    if bad_values:
        print(f"[!] Unparseable dates replaced with NaT: {bad_values[:5]}")

    # Keep as a real datetime64 column. pandas .dt.date/.dt.to_pydatetime()
    # produces Python date/datetime objects (dtype object), which pandas
    # to_sql cannot map to PostgreSQL DATE. We extract the underlying
    # numpy datetime64 values so the column keeps datetime64[us] dtype.
    df["transaction_date"] = parsed.dt.tz_localize(None).to_numpy()
    return df.drop(columns=["date"])


def _clean_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Strip thousands separators, cast to numeric and fall back to 0.00."""
    df = df.copy()
    for col in REQUIRED_NUMERIC:
        if col in df.columns:
            cleaned = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("$", "", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(cleaned, errors="coerce").fillna(0.00)
    return df


def _validate_required_dates(df: pd.DataFrame) -> pd.DataFrame:
    if "transaction_date" in df.columns:
        df = df.dropna(subset=["transaction_date"])
        if "transaction_date" in df.columns:
            # Re-parse to datetime64 without collapsing to Python date objects.
            df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
            df = df.dropna(subset=["transaction_date"])
    return df


def clean_data_chunk(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """Run the full cleaning chain over a single chunk and return a tidy copy."""
    if df.empty:
        return df

    df = _normalize_column_names(df)
    df = _clean_description(df)
    df = _standardize_date(df)
    df = _clean_numeric(df)
    df = _validate_required_dates(df)

    df["source_dataset"] = source_name
    return df
