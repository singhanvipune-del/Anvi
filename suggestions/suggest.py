def suggest_cleaning_actions(issues: dict) -> list:
    suggestions = []

    if 'empty_cells' in issues:
        suggestions.append("Fill missing values or remove rows with too many nulls.")

    if 'text_in_numeric_columns' in issues:
        suggestions.append("Remove text from numeric columns or convert column type.")

    return suggestions