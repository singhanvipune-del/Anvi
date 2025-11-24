import pandas as pd

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate rows."""
    if df is None or df.empty:
        return df
    return df.drop_duplicates().reset_index(drop=True)


def clean_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fix missing values intelligently."""
    if df is None:
        return df

    df = df.copy()

    for col in df.columns:

        # If numeric → fill with median
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())

        # If categorical → fill with mode
        else:
            if df[col].mode().empty:
                df[col] = df[col].fillna("Unknown")
            else:
                df[col] = df[col].fillna(df[col].mode()[0])

    return df


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace + normalize case for string columns."""
    df = df.copy()

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].str.replace(r"\s+", " ", regex=True)

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Master cleaning function used everywhere in the platform.
    Combines:
    - duplicate removal
    - missing value fixes
    - text cleanup
    """

    if df is None:
        return df

    df = df.copy()

    df = remove_duplicates(df)
    df = clean_missing_values(df)
    df = clean_text_columns(df)

    return df