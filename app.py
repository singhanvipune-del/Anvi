import pandas as pd
from ai.cleaning import clean_data, remove_duplicates
from ai.context_ai_correct import fix_names
from ai.gpt_context import generate_ai_notes
from detection.detect import detect_issues
from fixes.apply_fixes import apply_basic_fixes
from suggestions.suggest import suggest_cleaning_actions
from utils.suggest_improvements import advanced_improvements
from utils.storage import load_csv, save_csv
from utils.save_log import save_log


def process_file(filepath: str, name_columns=None, output="cleaned_output.csv"):
    df = load_csv(filepath)

    save_log("load", {"file": filepath})

    df = clean_data(df)
    df = apply_basic_fixes(df)

    if name_columns:
        df = fix_names(df, name_columns)

    issues = detect_issues(df)
    suggestions = suggest_cleaning_actions(issues)
    improvements = advanced_improvements(df)

    summary = f"Rows: {len(df)}, Columns: {len(df.columns)}. Issues: {issues}."
    ai_note = generate_ai_notes(summary)

    save_csv(df, output)
    save_log("processed", {"output": output, "issues": issues})

    return {
        "summary": summary,
        "ai_note": ai_note,
        "issues": issues,
        "suggestions": suggestions,
        "improvements": improvements,
        "output_file": output
    }


if __name__ == "__main__":
    result = process_file("sample.csv", name_columns=["Name"])
    print(result)