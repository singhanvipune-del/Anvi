import pandas as pd
from ai.autocorrect_hybrid import autocorrect_name
from ai.cleaning import clean_data, remove_duplicates
from detection.detect import detect_duplicates
from fixes.apply_fixes import apply_corrections
from utils.save_log import save_log
from utils.storage import save_file
from utils.suggest_improvements import suggest_improvements



def load_file(file_path):
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)

    elif file_path.endswith(".xlsx"):
        return pd.read_excel(file_path)

    else:
        raise ValueError("Unsupported file format. Use CSV or Excel.")


def correct_names(df):
    for col in df.columns:
        if df[col].dtype == "object":  # only fix text columns
            df[col] = df[col].apply(lambda x: autocorrect_name(x) if isinstance(x, str) else x)
    return df


def process_file(file_path):
    save_log("Starting processing...")

    df = load_file(file_path)
    save_log("File loaded successfully.")

    before_df = df.copy()

    # STEP 1: Detect duplicates
    duplicate_info = detect_duplicates(df)
    save_log(f"Found duplicates: {duplicate_info}")

    # STEP 2: Clean & remove duplicates
    df = remove_duplicates(df)
    df = clean_data(df)
    save_log("Cleaned data & removed duplicates.")

    # STEP 3: Autocorrect names (people, cities, countries, products etc)
    df = correct_names(df)
    save_log("Name corrections applied.")

    # STEP 4: Apply contextual fixes
    df = apply_corrections(df)
    save_log("Context-based corrections applied.")

    # STEP 5: Suggest improvements
    suggestions = suggest_improvements(df)
    save_log("Generated suggestions.")

    after_df = df.copy()

    return before_df, after_df, suggestions


if __name__ == "__main__":
    file_path = input("Enter the CSV/Excel file path: ")

    before, after, suggestions = process_file(file_path)

    print("\n--- BEFORE CLEANING ---")
    print(before)

    print("\n--- AFTER CLEANING ---")
    print(after)

    print("\n--- SUGGESTIONS ---")
    print(suggestions)