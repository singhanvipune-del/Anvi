# cleaning.py
import pandas as pd

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove completely identical duplicate rows and return new df."""
    return df.drop_duplicates(ignore_index=True)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning:
       - strip strings
       - convert empty strings to NaN
       - standardize column names to snake_case (simple)
    """
    df = df.copy()
    # strip string columns
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
            df[col] = df[col].replace("", pd.NA)
    # simple column normalization
    new_cols = []
    for c in df.columns:
        nc = (
            c.strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )
        new_cols.append(nc)
    df.columns = new_cols
    return df