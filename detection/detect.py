# detect.py
import pandas as pd

def detect_duplicates(df: pd.DataFrame):
    """
    Detect duplicate rows and duplicate values in columns.
    Returns a dictionary with details.
    """
    duplicates = {
        "duplicate_rows": df[df.duplicated()].index.tolist(),
        "duplicate_columns": [],
        "duplicate_values": {}
    }

    # Check duplicate columns (same data)
    for col1 in df.columns:
        for col2 in df.columns:
            if col1 != col2 and df[col1].equals(df[col2]):
                duplicates["duplicate_columns"].append((col1, col2))

    # Check duplicate values inside each column
    for col in df.columns:
        if df[col].dtype == "object":
            dup_vals = df[df[col].duplicated()][col].unique().tolist()
            if dup_vals:
                duplicates["duplicate_values"][col] = dup_vals

    return duplicates