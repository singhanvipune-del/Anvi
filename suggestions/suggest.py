# suggestions/suggest.py
import pandas as pd

def suggest_improvements(df: pd.DataFrame) -> list:
    suggestions = []
    if df is None or not hasattr(df, "columns"):
        return ["No dataframe provided"]
    # missing values per column
    na_counts = df.isna().sum().to_dict()
    for col, c in na_counts.items():
        if c > 0:
            suggestions.append(f"Column '{col}' has {int(c)} missing values.")
    # recommend key columns
    if "email" not in df.columns and "name" in df.columns:
        suggestions.append("Consider adding an 'email' column for user identification.")
    # suggest type conversions
    for col in df.columns:
        if df[col].dtype == object and df[col].str.len().mean() < 6:
            suggestions.append(f"Column '{col}' may be categorical/short strings. Consider encoding or fixing typos.")
    if not suggestions:
        suggestions.append("No suggestions — dataset looks OK at a glance.")
    return suggestions