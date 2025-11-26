# autocorrect_hybrid.py
import pandas as pd
from rapidfuzz import process, fuzz
from functools import lru_cache
from typing import Dict, List

DATA_DIR = "data"  # adjust if your folder differs

@lru_cache(maxsize=1)
def load_reference_sets() -> Dict[str, List[str]]:
    """
    Load reference lists once (cached).
    Expects files:
      - data/name_gender.csv  (has column 'name' or first column of names)
      - data/world_cities.csv (has column 'city' or first column)
      - data/countries.csv
    """
    refs = {"names": [], "cities": [], "countries": []}
    try:
        df_names = pd.read_csv(f"{DATA_DIR}/name_gender.csv", encoding="utf-8", dtype=str, low_memory=False)
        # find first column that looks like a name
        if not df_names.empty:
            refs["names"] = df_names.iloc[:, 0].dropna().astype(str).str.strip().str.title().unique().tolist()
    except Exception:
        refs["names"] = []

    try:
        df_cities = pd.read_csv(f"{DATA_DIR}/world_cities.csv", encoding="utf-8", dtype=str, low_memory=False)
        if not df_cities.empty:
            refs["cities"] = df_cities.iloc[:, 0].dropna().astype(str).str.strip().str.title().unique().tolist()
    except Exception:
        refs["cities"] = []

    try:
        df_countries = pd.read_csv(f"{DATA_DIR}/countries.csv", encoding="utf-8", dtype=str, low_memory=False)
        if not df_countries.empty:
            refs["countries"] = df_countries.iloc[:, 0].dropna().astype(str).str.strip().str.title().unique().tolist()
    except Exception:
        refs["countries"] = []

    return refs

def fuzzy_map_value(value: str, choices: List[str], threshold: int = 85):
    """
    Map a value to closest choice using rapidfuzz; return best match if above threshold,
    otherwise return original (but normalized).
    """
    if value is None:
        return value

    s = str(value).strip()
    if s == "":
        return s

    best = process.extractOne(s, choices, scorer=fuzz.WRatio)
    if best and best[1] >= threshold:
        return best[0]
    # fallback: title-case small strings
    return " ".join(p.capitalize() for p in s.split())

def autocorrect_column_with_refs(series: pd.Series, choices: List[str], threshold: int = 88) -> pd.Series:
    return series.astype(str).apply(lambda v: fuzzy_map_value(v, choices, threshold=threshold))

def hybrid_autocorrect(df: pd.DataFrame, refs: Dict[str, List[str]] = None) -> pd.DataFrame:
    """
    Autocorrect common columns using reference sets:
      - name-like columns -> refs['names']
      - city-like columns -> refs['cities']
      - country-like columns -> refs['countries']
    """
    df = df.copy()
    if refs is None:
        refs = load_reference_sets()

    name_refs = refs.get("names", [])
    city_refs = refs.get("cities", [])
    country_refs = refs.get("countries", [])

    for col in df.columns:
        col_low = col.lower()
        if "name" in col_low or col_low in ("full_name", "firstname", "first_name", "last_name"):
            if name_refs:
                df[col] = autocorrect_column_with_refs(df[col], name_refs, threshold=85)
            else:
                df[col] = df[col].astype(str).apply(lambda s: " ".join(p.capitalize() for p in str(s).strip().split()))
        elif "city" in col_low:
            if city_refs:
                df[col] = autocorrect_column_with_refs(df[col], city_refs, threshold=85)
            else:
                df[col] = df[col].astype(str).apply(lambda s: s.title())
        elif "country" in col_low:
            if country_refs:
                df[col] = autocorrect_column_with_refs(df[col], country_refs, threshold=85)
            else:
                df[col] = df[col].astype(str).apply(lambda s: s.title())
        else:
            # For other text columns keep them trimmed and title cased for readability (optional)
            if df[col].dtype == "object":
                df[col] = df[col].astype(str).str.strip()
    return df
