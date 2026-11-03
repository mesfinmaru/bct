"""Entry point for the unified financial ETL pipeline.

Runs the Extract -> Transform -> Load workflow over two bank ledger files
and verifies the final row count and per-source breakdown in PostgreSQL.
"""

import os
import time
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_CHUNK_SIZE = 50_000

# (filename, logical source tag) - the filename is what appears on disk.
DATASETS = [
    ("BT_15.csv", "BT_15"),
    ("BT_20.csv", "BT_20"),
]

TARGET_TABLE = "bank_transactions"


def _discover_dataset_files() -> list[tuple[str, str]]:
    """Return (disk_path, source_tag) for every configured dataset present on disk."""
    found: list[tuple[str, str]] = []
    for filename, source_tag in DATASETS:
        candidate = RAW_DIR / filename
        if candidate.is_file():
            found.append((str(candidate), source_tag))
        else:
            print(f"[!] Dataset not found on disk: {candidate}")
    return found


def run_pipeline(chunk_size: int = DEFAULT_CHUNK_SIZE) -> None:
    """Extract, clean and load all discovered datasets into one table."""
    start_time = time.time()
    print("=== Starting Unified Financial ETL Pipeline ===")
    print(f"[I] Project root: {PROJECT_ROOT}")
    print(f"[I] Raw data directory: {RAW_DIR}")
    print(f"[I] Target table: {TARGET_TABLE}")
    print(f"[I] Chunk size: {chunk_size:,} rows")

    datasets = _discover_dataset_files()
    if not datasets:
        raise FileNotFoundError("No raw dataset files were found in data/raw/.")
    print(f"[I] Datasets to process: {[name for _, name in datasets]}")

    from extract import extract_data
    from transform import clean_data_chunk
    from load import load_chunk_to_postgres, get_database_engine

    engine = get_database_engine()

    loaded_any = False
    for file_path, source_name in datasets:
        print(f"\n--- Extracting and Loading: {source_name} ---")
        chunk_count = 0

        for chunk in extract_data(file_path, chunk_size=chunk_size):
            cleaned_chunk = clean_data_chunk(chunk, source_name)
            if cleaned_chunk.empty:
                print(f"[!] No rows to load from chunk in {source_name}.")
                continue

            if not loaded_any:
                load_chunk_to_postgres(cleaned_chunk, TARGET_TABLE, if_exists="replace")
                loaded_any = True
            else:
                load_chunk_to_postgres(cleaned_chunk, TARGET_TABLE, if_exists="append")
            chunk_count += 1
            print(f"[+] Loaded chunk {chunk_count} from {source_name} ({len(cleaned_chunk):,} rows).")

        if chunk_count == 0:
            print(f"[!] No rows were loaded from {source_name}.")

    if not loaded_any:
        raise RuntimeError("Pipeline failed: no data was loaded into the target table.")

    _verify(engine, TARGET_TABLE)
    print(f"\n=== ETL Pipeline Completed Successfully ===")
    elapsed = time.time() - start_time
    print(f"Total time taken: {elapsed:.2f} seconds")


def _verify(engine, table_name: str) -> None:
    """Run verification queries after the load has finished."""
    with engine.connect() as conn:
        total_res = conn.execute(text(f"SELECT COUNT(*) FROM {table_name};"))
        total_count = total_res.scalar()
        print(f"\n[VERIFICATION] Total rows combined in '{table_name}': {total_count:,}")

        breakdown_res = conn.execute(
            text(f"SELECT source_dataset, COUNT(*) FROM {table_name} GROUP BY source_dataset;")
        )
        print("[VERIFICATION] Breakdown by dataset:")
        for row in breakdown_res:
            print(f" - {row[0]}: {row[1]:,} rows")

        expected = sum(1 for _ in open("data/raw/BT_15.csv")) + sum(1 for _ in open("data/raw/BT_20.csv"))
        expected -= 2  # source + header lines
        ok = total_count >= 2_000_000
        print(f"[VERIFICATION] Expected rows: {expected:,}")
        print(f"[VERIFICATION] Threshold met (>= 2,000,000): {'YES' if ok else 'NO'}")


if __name__ == "__main__":
    run_pipeline()
