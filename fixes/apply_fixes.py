# apply_fixes.py
import pandas as pd

def apply_corrections(df: pd.DataFrame, corrections: dict) -> pd.DataFrame:
    """
    Apply corrections (like autocorrect results or cleaned values)
    corrections format → {column: {old_value: new_value}}
    """
    for col in corrections:
        df[col] = df[col].replace(corrections[col])
    return df