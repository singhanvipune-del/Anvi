# cleaning.py
import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove spaces, normalize text, fix formatting."""
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Delete duplicated rows from dataset."""
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    print(f"Removed {before - after} duplicate rows.")
    return df