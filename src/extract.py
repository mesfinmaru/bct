"""Extraction layer: a memory-bounded CSV generator."""

from __future__ import annotations

import os

import pandas as pd


def extract_data(file_path: str, chunk_size: int = 50_000) -> Iterable[pd.DataFrame]:
    """Yield chunks of *chunk_size* rows from the source CSV without loading it fully."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at: {file_path}")

    print(f"[*] Extracting {file_path} in chunks of {chunk_size:,}...")
    try:
        reader = pd.read_csv(file_path, chunksize=chunk_size)
        for chunk in reader:
            yield chunk
    except Exception as exc:
        print(f"[!] Error reading file {file_path}: {exc}")
        raise
