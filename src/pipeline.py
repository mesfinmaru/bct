import time
from extract import extract_data
from transform import clean_data_chunk
from load import load_chunk_to_postgres, get_database_engine
from sqlalchemy import text

def run_pipeline():
    start_time = time.time()
    print("=== Starting Unified Financial ETL Pipeline ===")
    
    # Define your two datasets pointing to the same target table
    datasets = [
        {"path": "data/raw/BT_15.csv", "name": "BT_15"},
        {"path": "data/raw/BT_20.csv", "name": "BT_20"}
    ]
    
    target_table = "bank_transactions"
    engine = get_database_engine()
    
    is_first_load = True

    for item in datasets:
        file_path = item["path"]
        source_name = item["name"]
        print(f"\n--- Extracting and Loading: {source_name} ---")
        
        chunk_count = 0
        try:
            for chunk in extract_data(file_path, chunk_size=50000):
                cleaned_chunk = clean_data_chunk(chunk, source_name)
                
                # 'replace' table on the very first chunk of dataset one, 'append' for all subsequent chunks
                if is_first_load:
                    mode = 'replace'
                    is_first_load = False
                else:
                    mode = 'append'
                
                load_chunk_to_postgres(cleaned_chunk, target_table, if_exists=mode)
                chunk_count += 1
                print(f"[+] Loaded chunk {chunk_count} from {source_name} into {target_table} table.")
                
        except Exception as e:
            print(f"[!] Error processing {file_path}: {e}")

    print("\n=== ETL Pipeline Completed Successfully ===")
    print(f"Total time taken: {time.time() - start_time:.2f} seconds")
    
    # Verification Query showing total rows combined and breakdown by source
    with engine.connect() as conn:
        total_res = conn.execute(text(f"SELECT COUNT(*) FROM {target_table};"))
        total_count = total_res.scalar()
        print(f"\n[VERIFICATION] Total rows combined in '{target_table}': {total_count:,}")
        
        breakdown_res = conn.execute(text(f"SELECT source_dataset, COUNT(*) FROM {target_table} GROUP BY source_dataset;"))
        print("[VERIFICATION] Breakdown by dataset:")
        for row in breakdown_res:
            print(f" - {row[0]}: {row[1]:,} rows")

if __name__ == "__main__":
    run_pipeline()