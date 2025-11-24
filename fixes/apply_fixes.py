# fixes/apply_fixes.py
import pandas as pd
import re

def apply_corrections(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # example: normalize phone-like columns
    for col in df.columns:
        if "phone" in col or "contact" in col:
            df[col] = df[col].apply(lambda x: _normalize_phone(x) if isinstance(x, str) else x)
        # example numeric fix: strings that look numeric -> numeric
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda x: _to_number_if_possible(x))
    return df

def _normalize_phone(s: str) -> str:
    digits = re.sub(r"\D", "", s)
    if len(digits) == 10:
        return f"+{digits}"
    if len(digits) >= 7:
        return digits
    return s

def _to_number_if_possible(v):
    if isinstance(v, str):
        v2 = v.strip().replace(",", "")
        try:
            if "." in v2:
                return float(v2)
            return int(v2)
        except Exception:
            return v
    return v