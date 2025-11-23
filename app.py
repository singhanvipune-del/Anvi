import pandas as pd
import streamlit as st

from ai.autocorrect_hybrid import autocorrect_name
from ai.cleaning import clean_data, remove_duplicates
from detection.detect import detect_duplicates
from fixes.apply_fixes import apply_corrections
from utils.save_log import save_log
from utils.suggest_improvements import suggest_improvements


# ---------------------------
# Load File (Streamlit friendly)
# ---------------------------
def load_file(uploaded_file):
    if uploaded_file is None:
        raise ValueError("No file uploaded")

    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    elif uploaded_file.name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)

    else:
        raise ValueError("Unsupported file format. Upload CSV or Excel.")


# ---------------------------
# Fix names
# ---------------------------
def correct_names(df):
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(
                lambda x: autocorrect_name(x) if isinstance(x, str) else x
            )
    return df


# ---------------------------
# Main Processing Function
# ---------------------------
def process_file(uploaded_file):
    save_log("Starting processing...")

    df = load_file(uploaded_file)
    save_log("File loaded successfully.")

    before_df = df.copy()

    # STEP 1: Detect duplicates
    duplicate_info = detect_duplicates(df)
    save_log(f"Found duplicates: {duplicate_info}")

    # STEP 2: Clean & remove duplicates
    df = remove_duplicates(df)
    df = clean_data(df)
    save_log("Cleaned data & removed duplicates.")

    # STEP 3: Autocorrect names
    df = correct_names(df)
    save_log("Name corrections applied.")

    # STEP 4: Apply contextual fixes
    df = apply_corrections(df)
    save_log("Context-based corrections applied.")

    # STEP 5: Suggestions
    suggestions = suggest_improvements(df)
    save_log("Generated suggestions.")

    after_df = df.copy()

    return before_df, after_df, suggestions


# ---------------------------
# Streamlit App UI
# ---------------------------
def main():
    st.title("AI Data Cleaning App")
    st.write("Upload your CSV or Excel file to clean it automatically.")

    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file:
        st.success("File uploaded successfully!")

        before, after, suggestions = process_file(uploaded_file)

        st.subheader("Before Cleaning")
        st.dataframe(before)

        st.subheader("After Cleaning")
        st.dataframe(after)

        st.subheader("Suggestions")
        st.write(suggestions)


# Run Streamlit app
if __name__ == "__main__":
    main()