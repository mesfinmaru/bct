"""Loading layer: streams cleaned chunks into PostgreSQL without blowing memory."""

from __future__ import annotations

import os
from typing import Iterable

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

load_dotenv()

REQUIRED_ENV = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")


def _resolve_env(var: str, default: str = "") -> str:
    """Read an environment variable, failing fast when a required one is missing."""
    value = os.getenv(var, default)
    if value == "":
        raise RuntimeError(f"Missing required environment variable: {var}")
    return value


def get_database_url() -> str:
    """Build the PostgreSQL connection string from the project's .env file."""
    return (
        f"postgresql://{_resolve_env('DB_USER')}:{quote_plus(_resolve_env('DB_PASSWORD'))}"
        f"@{_resolve_env('DB_HOST')}:{_resolve_env('DB_PORT')}/{_resolve_env('DB_NAME')}"
    )


def get_database_engine() -> create_engine:
    """Return a SQLAlchemy engine for the configured PostgreSQL connection."""
    return create_engine(get_database_url(), pool_pre_ping=True, pool_recycle=3600)


def validate_dataframe(df: pd.DataFrame) -> None:
    """Fail fast on obviously broken chunks so we never write bad data."""
    if df.empty:
        return
    missing_columns = [c for c in ("transaction_date", "source_dataset") if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Chunk is missing required columns: {missing_columns}")
    if df["transaction_date"].isna().any():
        raise ValueError("Chunk contains null transaction_date values.")


def load_chunk_to_postgres(df: pd.DataFrame, table_name: str, if_exists: str = "append") -> int:
    """Write one chunk into the table using server-side multi-row execution."""
    from pandas import DataFrame

    if not isinstance(df, DataFrame):
        raise TypeError("load_chunk_to_postgres expects a pandas DataFrame.")

    validate_dataframe(df)

    engine = get_database_engine()
    try:
        df.to_sql(
            table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            method="multi",
            chunksize=10_000,
            dtype={
                "transaction_date": "DATE",
                "source_dataset": "VARCHAR(50)",
                "description": "VARCHAR(100)",
                "deposits": "NUMERIC(15, 2)",
                "withdrawals": "NUMERIC(15, 2)",
                "balance": "NUMERIC(15, 2)",
            },
        )
    except Exception as exc:
        print(f"[!] Failed to load table {table_name}: {exc}")
        raise
    return len(df)


def run_partitioned_import(
    chunks: Iterable[pd.DataFrame],
    table_name: str,
    if_exists: str = "append",
) -> int:
    """Load an iterable of cleaned chunks into PostgreSQL and return the total row count."""
    total_rows = 0
    for chunk in chunks:
        if chunk.empty:
            continue
        load_chunk_to_postgres(chunk, table_name, if_exists=if_exists)
        total_rows += len(chunk)
    return total_rows
