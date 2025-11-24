import pandas as pd

def apply_basic_fixes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.replace(['None', 'null', 'Null', 'NA', 'N/A', 'na'], pd.NA)
    return df