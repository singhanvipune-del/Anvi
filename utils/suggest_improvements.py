import pandas as pd

def suggest_improvements(df: pd.DataFrame):
    """
    Generate basic improvement suggestions for the dataset.
    Can be expanded later with AI.
    """
    suggestions = []

    # Recommendation 1: Empty cells
    missing = df.isnull().sum().sum()
    if missing > 0:
        suggestions.append(f"Found {missing} empty values. Consider filling them.")

    # Recommendation 2: Column names
    for col in df.columns:
        if " " in col:
            suggestions.append(f"Column '{col}' contains spaces. Use underscore (_) instead.")

    # Recommendation 3: Data type warning
    for col in df.columns:
        if df[col].dtype == "object" and df[col].str.isnumeric().any():
            suggestions.append(f"Column '{col}' contains numbers but is stored as text.")

    if not suggestions:
        suggestions.append("No further improvements suggested. Data looks clean.")

    return suggestions