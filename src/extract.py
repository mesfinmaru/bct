import pandas as pd
import os

def extract_data(file_path: str, chunk_size: int = 100000):
    """
    Generator function to extract large CSV files in manageable chunks.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at: {file_path}")
    
    print(f"[*] Starting extraction from {file_path} in chunks of {chunk_size}...")
    try:
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            yield chunk
    except Exception as e:
        print(f"[!] Error reading file {file_path}: {e}")
        raise