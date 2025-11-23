def suggest_improvements(before_df, after_df):
    """Suggest improvements comparing before and after results."""
    suggestions = []

    # Check duplicates removed
    removed = len(before_df) - len(after_df)
    if removed > 0:
        suggestions.append(f"{removed} duplicate rows were removed.")

    # Check if any columns changed
    for col in before_df.columns:
        if before_df[col].dtype == "object":
            changed = (before_df[col] != after_df[col]).sum()
            if changed > 0:
                suggestions.append(f"{changed} values were corrected in column '{col}'.")

    if not suggestions:
        suggestions.append("No major improvements needed.")

    return suggestions