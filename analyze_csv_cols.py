import pandas as pd

try:
    df = pd.read_csv('data/medicine_dataset.csv', nrows=2)
    print("Columns:", df.columns.tolist())
    # print detailed info about columns that look like they are split (use, sideEffect)
    use_cols = [c for c in df.columns if 'use' in c.lower()]
    side_effect_cols = [c for c in df.columns if 'side' in c.lower() and 'effect' in c.lower()]
    print(f"Use columns: {use_cols}")
    print(f"Side Effect columns: {side_effect_cols}")
    
    # Check if there is a single column for these as well
    print(f"Values in row 0 for 'use' related cols:")
    print(df.iloc[0][use_cols])
except ImportError:
    print("pandas not found")
