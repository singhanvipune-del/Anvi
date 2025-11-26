import streamlit as st
import pandas as pd
import json
from fixes.apply_fixes import apply_fixes
from detection.detect import fuzzy_duplicate_pairs
from utils.save_log import save_log

# --------------------------
# Helper functions (ADD HERE)
# --------------------------

def download_button_for_df(df, filename="output.csv"):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download File",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )

def run_clean():
    return st.button("Run Cleaning", key="run_clean")

def detect_duplicates_btn():
    return st.button("Detect Duplicates", key="dup_btn")

# --- Upload Section ---
st.title("AI Data Cleaner — PyCharm / Streamlit")

uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

df_raw = None
cleaned_df = None

if uploaded_file is not None:
    file_ext = uploaded_file.name.split(".")[-1].lower()

    if file_ext == "csv":
        df_raw = pd.read_csv(uploaded_file)
    else:
        df_raw = pd.read_excel(uploaded_file)

    st.subheader("Raw Data (first 200 rows)")
    st.dataframe(df_raw.head(200))
else:
    st.warning("Upload a file to begin.")

# ... earlier in app.py setup remain ...

# Manual corrections input (safe)
st.markdown("### Optional: Manual corrections (JSON format)")
corrections_input = st.text_area(
    "Example: {\"city\": {\"mumbay\": \"Mumbai\"}, \"gender\": {\"femlae\": \"female\"}}",
    value="",
    height=90
)

# button actions
if run_clean:
    with st.spinner("Running cleaning pipeline..."):
        cleaned_df = apply_fixes(df_raw)
        st.success("Cleaning complete")
        st.dataframe(cleaned_df.head(200))
        download_button_for_df(cleaned_df, filename="cleaned_data.csv")
        try:
            save_path = save_log("clean", {"rows_before": len(df_raw), "rows_after": len(cleaned_df)})
            st.write(f"Saved log: `{save_path}`")
        except Exception:
            st.info("Logging failed (check logs dir).")

run_clean = st.button("Run Automated Cleaning")

detect_duplicates_btn = st.button("Detect Fuzzy Duplicates")

if corrections_input.strip():
    try:
        corrections = json.loads(corrections_input)
        if not isinstance(corrections, dict):
            raise ValueError("Top-level JSON must be an object/dictionary mapping column->mapping")
        # Validate inner structure: each value must be a dict mapping old->new
        for k, v in corrections.items():
            if not isinstance(v, dict):
                raise ValueError(f"Value for column '{k}' must be a mapping (old->new)")




        # Apply corrections to the appropriate DataFrame (cleaned if exists else raw)
        target_df = cleaned_df.copy() if 'cleaned_df' in locals() and cleaned_df is not None else df_raw.copy()
        for col, mapping in corrections.items():
            if col in target_df.columns:
                target_df[col] = target_df[col].astype(str).replace(mapping)
        st.success("Manual corrections applied")
        st.dataframe(target_df.head(200))
        download_button_for_df(target_df, filename="corrected_data.csv")
    except json.JSONDecodeError as e:
        st.error(f"Could not parse JSON: {e.msg} at pos {e.pos}")
    except Exception as e:
        st.error(f"Manual corrections validation error: {e}")

# Fuzzy duplicates detection
if detect_duplicates_btn:
    with st.spinner("Detecting fuzzy duplicates..."):
        source_df = cleaned_df if 'cleaned_df' in locals() and cleaned_df is not None else df_raw
        dup_df = fuzzy_duplicate_pairs(source_df, threshold=85, sample_limit=1500)
        if dup_df.empty:
            st.info("No fuzzy duplicates found with the current threshold.")
        else:
            st.subheader("Fuzzy Duplicate Pairs")
            st.dataframe(dup_df)
            if st.checkbox("Show sample duplicate row pairs"):
                for _, r in dup_df.head(50).iterrows():
                    i, j = int(r['row_i']), int(r['row_j'])
                    st.markdown(f"**Pair ({i}, {j}) — score: {r['score']}**")
                    st.write("Row i:")
                    st.write(source_df.iloc[i].to_dict())
                    st.write("Row j:")
                    st.write(source_df.iloc[j].to_dict())
                    st.markdown("---")
