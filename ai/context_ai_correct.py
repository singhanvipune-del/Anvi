import pandas as pd
from dateutil import parser
from ai.autocorrect_hybrid import hybrid_text_clean
from ai.gpt_context import gpt_context_correction

def is_probable_date(value):
    """Check if a cell value looks like a date."""
    if not isinstance(value, str):
        return False
    try:
        parser.parse(value, fuzzy=False)
        return True
    except:
        return False


def standardize_date(value):
    """Convert detected date strings to YYYY-MM-DD format."""
    try:
        dt = parser.parse(value, fuzzy=True, dayfirst=True)
        return dt.strftime("%Y-%m-%d")
    except:
        return value


def safe_context_ai_clean(df):
    """
    Multilingual, name-aware, context AI cleaning.
    Cleans text columns, standardizes dates, skips numeric columns.
    """
    try:
        for col in df.columns:
            # Handle datetime or mixed date columns
            if any(df[col].astype(str).apply(is_probable_date)):
                df[col] = df[col].astype(str).apply(lambda x: standardize_date(x))
                continue

            # Skip numeric columns
            if pd.api.types.is_numeric_dtype(df[col]):
                continue

            # Clean only text-based columns
            df[col] = df[col].astype(str).fillna("")
            df[col] = df[col].apply(lambda x: gpt_context_correction(hybrid_text_clean(x)))

        return df

    except Exception as e:
        print(f"❌ Context AI correction failed: {e}")
        return df