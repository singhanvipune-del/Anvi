import pandas as pd

def apply_fixes (df):
    df = df.copy()

    # Convert all columns to string safely
    for col in df.columns:
        df[col] = df[col].astype(str).fillna("")

        # Safe string operations
        df[col] = (
            df[col]
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    return df
