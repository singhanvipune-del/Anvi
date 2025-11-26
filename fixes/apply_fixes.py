import pandas as pd

def apply_fixes(df):
    df = df.copy()

    for col in df.columns:
        df[col] = df[col].astype(str).fillna("")
        df[col] = (
            df[col]
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    return df
