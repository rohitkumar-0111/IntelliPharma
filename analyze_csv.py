import pandas as pd

try:
    df = pd.read_csv('data/medicine_dataset.csv', nrows=5)
    print("Columns:", df.columns.tolist())
    print("-" * 20)
    print(df.head(1).T)
except ImportError:
    import csv
    with open('data/medicine_dataset.csv', 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        print("Columns:", headers)
        print("-" * 20)
        first_row = next(reader)
        for h, v in zip(headers, first_row):
            print(f"{h}: {v}")
