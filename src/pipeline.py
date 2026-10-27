import time
from src.extract import extract_data
from src.transform import clean_data_chunk
from src.load import load_chunk_to_postgres, get_database_engine
from sqlalchemy import text

def run_pipeline():
    start_time = time.time()
    print("=== Starting ETL Pipeline Execution ===")
    
    # File paths for your two datasets (>1M rows each)
    dataset_1_path = "data/raw/dataset_one.csv"
    table_name_1 = "fact_transactions"
    
    # Process Dataset 1 in chunks
    chunk_count = 0
    for chunk in extract_data(dataset_1_path, chunk_size=50000):
        cleaned_chunk = clean_data_chunk(chunk)
        # Use 'replace' on the first chunk, 'append' thereafter
        mode = 'replace' if chunk_count == 0 else 'append'
        load_chunk_to_postgres(cleaned_chunk, table_name_1, if_exists=mode)
        chunk_count += 1
        print(f"[+] Loaded chunk {chunk_count} for {table_name_1}")

    print("=== ETL Pipeline Completed Successfully ===")
    print(f"Total time taken: {time.time() - start_time:.2f} seconds")
    
    # Verification query
    engine = get_database_engine()
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name_1};"))
        row_count = result.scalar()
        print(f"[VERIFICATION] Total rows loaded in '{table_name_1}': {row_count:,}")

if __name__ == "__main__":
    run_pipeline()