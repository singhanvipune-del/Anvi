# fixes/apply_fixes.py
import pandas as pd
from autocorrect_hybrid import hybrid_autocorrect, load_reference_sets

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )
    return df

def trim_strings(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in df.select_dtypes(include=["object"]).columns:
        df[c] = df[c].astype(str).str.strip()
    return df

def titlecase_name_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # heuristics: columns with 'name' or 'first' or 'last'
    name_cols = [c for c in df.columns if "name" in c or "first" in c or "last" in c]
    for c in name_cols:
        df[c] = df[c].astype(str).apply(lambda s: " ".join(p.capitalize() for p in s.split()))
    return df

def replace_obvious_missing(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "none": pd.NA}, inplace=True)
    return df

def remove_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    before = len(df)
    df = df.drop_duplicates(ignore_index=True)
    df.attrs["exact_duplicates_removed"] = before - len(df)
    return df

def apply_basic_fixes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Conservative automatic cleaning:
    - normalize columns
    - trim whitespace
    - replace obvious missing values
    - title-case name columns
    - run hybrid autocorrect (names, cities)
    - remove exact duplicates
    """
    df = df.copy()
    df = clean_column_names(df)
    df = trim_strings(df)
    df = replace_obvious_missing(df)
    df = titlecase_name_columns(df)

    # load reference sets (cached inside hybrid_autocorrect)
    refs = load_reference_sets()

    # run hybrid autocorrect using provided reference lists
    df = hybrid_autocorrect(df, refs=refs)

    df = remove_exact_duplicates(df)

    return df
