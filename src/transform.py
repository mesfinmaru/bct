import pandas as pd

def clean_data_chunk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans an individual chunk of data: drops duplicates, handles nulls, 
    and standardizes data types.
    """
    # Remove exact duplicate rows
    df = df.drop_duplicates()
    
    # Example cleaning steps (customize based on your specific columns):
    # 1. Fill missing numerical values with 0 or median
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # 2. Fill missing categorical values with 'Unknown'
    cat_cols = df.select_dtypes(include=['object']).columns
    df[cat_cols] = df[cat_cols].fillna('Unknown')
    
    # 3. Standardize text data (e.g., lowercase strip strings)
    for col in cat_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
            
    # 4. Ensure correct datetime formatting if date columns exist
    # df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    
    return df