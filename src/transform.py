import pandas as pd

def clean_data_chunk(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """
    Cleans chunks for bank transaction datasets: handles nulls, formats dates, 
    cleans description text, casts numeric columns, and tags the data source.
    """
    # 1. Drop exact duplicates
    df = df.drop_duplicates()
    
    # 2. Standardize column names (strip whitespace and lower case)
    df.columns = [col.strip().lower() for col in df.columns]
    
    # Handle possible spelling variation for withdrawals/withdrawls
    if 'withdrawls' in df.columns and 'withdrawals' not in df.columns:
        df = df.rename(columns={'withdrawls': 'withdrawals'})

    # 3. Clean Description (Fill missing with 'Other', strip spaces)
    if 'description' in df.columns:
        df['description'] = df['description'].fillna('Other').astype(str).str.strip()

    # 4. Parse Dates
    if 'date' in df.columns:
        df['transaction_date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.drop(columns=['date']) # drop old date column
        df['transaction_date'] = df['transaction_date'].dt.date # Keep date only

    # 5. Clean Numeric Columns (Deposits, Withdrawals, Balance)
    numeric_cols = [col for col in ['deposits', 'withdrawals', 'balance'] if col in df.columns]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.00)

    # 6. Drop rows where critical transaction date is missing
    if 'transaction_date' in df.columns:
        df = df.dropna(subset=['transaction_date'])

    # 7. Add source dataset tag for auditing/tracking
    df['source_dataset'] = source_name

    return df