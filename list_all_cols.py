import pandas as pd
import sys

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

try:
    df = pd.read_csv('data/medicine_dataset.csv', nrows=0) # Just read header
    cols = df.columns.tolist()
    print("ALL COLUMNS:")
    for c in cols:
        print(c)
except ImportError:
    import csv
    with open('data/medicine_dataset.csv', 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        print("ALL COLUMNS:")
        for h in headers:
            print(h)
