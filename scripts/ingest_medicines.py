import pandas as pd
from sqlalchemy import create_engine, Integer, String, Column, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings
import os

# Define the base and model here for standalone script execution
# Or import from models.models if preferred, but defining here ensures script is self-contained for the table creation part if models.py changes vary.
# However, for consistency, we will attempt to import or redefine compatibly. 
# Let's import to ensure we use the same Base.
# Actually, since this is a script, we might want to use a synchronous engine for pandas `to_sql`.

DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1) # Sync driver for pandas usually prefers postgresql://

# We need a sync engine for pandas to_sql
# asyncpg is async. we need psycopg2 or similar for sync, or just use the async engine with some workarounds?
# Pandas `to_sql` supports sqlalchemy engine. If we have `asyncpg`, we can't use `to_sql` directly without an async adapter or just using `psycopg2`.
# Let's assume the user has `psycopg2` or `psycopg2-binary` installed or will install it.
# If not, we can try to use the async engine but `to_sql` is blocking.
# RECOMMENDATION: Add `psycopg2-binary` to requirements if not present.
# For now, I'll assume standard sync connection string works if driver is present. 
# If `asyncpg` is the only driver, we have to write a custom loop.
# Let's write a robust script that uses SQLAlchemy ORM for table creation and then raw inserts or pandas with a compatible driver.

# Workaround: Use `psycopg2` driver for ingestion.
# I will add `psycopg2-binary` to the requirements update in the next step if I can, or mention it. 
# The user asked for "Script to ingest". 

def merge_columns(row, prefix, start, end):
    values = []
    for i in range(start, end + 1):
        col_name = f"{prefix}{i}"
        if col_name in row and pd.notna(row[col_name]) and row[col_name] != "":
            values.append(str(row[col_name]))
    return ", ".join(values)

def ingest_data():
    csv_path = "medicine_dataset.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    print("Loading dataset...")
    df = pd.read_csv(csv_path)

    print("Cleaning and merging columns...")
    # Side Effects: sideEffect0 to sideEffect41
    df['side_effects'] = df.apply(lambda row: merge_columns(row, 'sideEffect', 0, 41), axis=1)

    # Substitutes: substitute0 to substitute4
    df['substitutes'] = df.apply(lambda row: merge_columns(row, 'substitute', 0, 4), axis=1)

    # Uses: use0 to use4
    df['uses'] = df.apply(lambda row: merge_columns(row, 'use', 0, 4), axis=1)

    # Rename columns
    rename_map = {
        'name': 'drug_name',
        'Chemical Class': 'chemical_class',
        'Habit Forming': 'habit_forming',
        'Therapeutic Class': 'therapeutic_class',
        'Action Class': 'action_class'
    }
    df = df.rename(columns=rename_map)

    # Select final columns
    final_cols = ['id', 'drug_name', 'substitutes', 'side_effects', 'uses', 
                  'chemical_class', 'habit_forming', 'therapeutic_class', 'action_class']
    
    # Ensure all columns exist (some might be missing in source, fill with None)
    for col in final_cols:
        if col not in df.columns:
            df[col] = None
            
    df_final = df[final_cols]

    print("Connecting to database...")
    # Use sync engine for pandas
    # Ensure the URL is for a sync driver (e.g., psycopg2)
    sync_db_url = DATABASE_URL.replace("+asyncpg", "") 
    if "postgresql" not in sync_db_url: # Basic check
         sync_db_url = "postgresql+psycopg2://" + sync_db_url.split("://")[-1]

    engine = create_engine(sync_db_url, echo=False)

    print("Ingesting data...")
    try:
        df_final.to_sql(
            'medicines', 
            engine, 
            if_exists='replace', # Or 'append' if we want to keep existing schemas, but 'replace' is safer for full ingest
            index=False, 
            method='multi', 
            chunksize=1000
        )
        # Add index on drug_name
        with engine.connect() as con:
            con.execute("CREATE INDEX IF NOT EXISTS idx_medicines_drug_name ON medicines (drug_name);")
            
        print("Ingestion complete!")
    except Exception as e:
        print(f"Error during ingestion: {e}")
        print("Note: Ensure `psycopg2` or `psycopg2-binary` is installed for synchronous operations.")

if __name__ == "__main__":
    ingest_data()
