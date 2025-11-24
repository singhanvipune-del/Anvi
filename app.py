# app.py
import streamlit as st
import pandas as pd
from utils.save_log import save_log
from utils.storage import save_file_bytes
from ai.cleaning import clean_data, remove_duplicates
from ai.autocorrect_hybrid import autocorrect_name
from detection.detect import detect_duplicates
from fixes.apply_fixes import apply_corrections
from utils.suggest_improvements import suggest_improvements

st.set_page_config(page_title="AI Data Cleaning App", layout="wide")

def load_file_streamlit(uploaded_file):
    """Load uploaded_file (Streamlit UploadedFile) into pandas DataFrame safely."""
    if uploaded_file is None:
        raise ValueError("No file uploaded")
    name = uploaded_file.name.lower()
    raw = uploaded_file.read()
    # optionally save the upload for debugging
    save_file_bytes(raw, f"uploads/{uploaded_file.name}")
    if name.endswith(".csv"):
        return pd.read_csv(pd.io.common.BytesIO(raw))
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(pd.io.common.BytesIO(raw), engine="openpyxl")
    raise ValueError("Unsupported file type. Upload .csv or .xlsx")

def correct_names(df):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda x: autocorrect_name(x) if isinstance(x, str) else x)
    return df

def process_file(uploaded_file):
    save_log("Starting processing...")
    df = load_file_streamlit(uploaded_file)
    save_log("Loaded file")
    before_df = df.copy()

    # detect
    dup_info = detect_duplicates(df)
    save_log(f"Detect duplicates: {dup_info}")

    # clean
    df = remove_duplicates(df)
    df = clean_data(df)
    save_log("Cleaned & removed duplicates")

    # names
    df = correct_names(df)
    save_log("Autocorrect applied")

    # contextual fixes
    df = apply_corrections(df)
    save_log("Applied contextual corrections")

    suggestions = suggest_improvements(df)
    after_df = df.copy()

    return before_df, after_df, suggestions

def main():
    st.title("AI Data Cleaning App")
    st.write("Upload CSV or Excel file to clean it automatically.")
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])
    if not uploaded_file:
        st.info("Upload a CSV or Excel file to start.")
        return

    st.success("File uploaded successfully!")
    try:
        before, after, suggestions = process_file(uploaded_file)
    except Exception as e:
        save_log(f"process_file error: {repr(e)}")
        st.error("Processing failed — check logs. " + str(e))
        return

    # sanity checks
    if before is None or not hasattr(before, "columns"):
        st.error("'before' is not a DataFrame")
        return

    st.subheader("Before Cleaning")
    st.dataframe(before)

    st.subheader("After Cleaning")
    st.dataframe(after)

    st.subheader("Suggestions")
    for s in suggestions:
        st.write("- ", s)

    # download cleaned CSV
    csv = after.to_csv(index=False).encode("utf-8")
    st.download_button("Download cleaned CSV", data=csv, file_name="cleaned.csv", mime="text/csv")

if __name__ == "__main__":
    main()