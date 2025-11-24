import pandas as pd

def detect_issues(df: pd.DataFrame) -> dict:
    issues = {}

    # Detect empty cells
    empty = df.isnull().sum().sum()
    if empty > 0:
        issues['empty_cells'] = int(empty)

    # Detect numeric columns containing text
    text_in_numeric = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].astype(str).str.contains('[A-Za-z]').any():
                text_in_numeric.append(col)
    if text_in_numeric:
        issues['text_in_numeric_columns'] = text_in_numeric

    return issues