import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

def get_database_engine():
    user = os.getenv("DB_USER", "")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "")
    port = os.getenv("DB_PORT", "")
    db_name = os.getenv("DB_NAME", "")

    # URL-encode the password so special characters like '@' don't break the connection string
    encoded_password = quote_plus(password)
    
    connection_string = f"postgresql://{user}:{encoded_password}@{host}:{port}/{db_name}"
    return create_engine(connection_string)

def load_chunk_to_postgres(df: pd.DataFrame, table_name: str, if_exists: str = 'append'):
    """
    Loads a Pandas DataFrame chunk directly into PostgreSQL.
    """
    engine = get_database_engine()
    try:
        df.to_sql(table_name, con=engine, if_exists=if_exists, index=False, method='multi', chunksize=10000)
    except Exception as e:
        print(f"[!] Error loading chunk to table {table_name}: {e}")
        raise