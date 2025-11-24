# detection/detect.py
import pandas as pd

def detect_duplicates(df: pd.DataFrame):
    """Return simple info about duplicates so we can log or show to user."""
    total = len(df)
    dup_bool = df.duplicated()
    dup_count = dup_bool.sum()
    # per-column duplicates idea: count unique per col
    col_uniques = {col: int(df[col].nunique(dropna=True)) for col in df.columns}
    return {"total_rows": int(total), "duplicate_rows": int(dup_count), "col_uniques": col_uniques}