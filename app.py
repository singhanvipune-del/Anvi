import streamlit as st
import pandas as pd
from io import BytesIO

# Import your hybrid & context AI modules
from ai.autocorrect_hybrid import hybrid_text_suggestions
from ai.context_ai_correct import gpt_context_correction

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Data Cleaner", page_icon="🧠", layout="wide")

st.title("🧠 AI Data Cleaner Platform")
st.write("Upload your dataset and let AI clean and correct it intelligently!")

# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader("📂 Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Load file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success(f"✅ File loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns.")

        st.subheader("📊 Preview of your data")
        st.dataframe(df.head())

        # ---------- HYBRID AI CORRECTION ----------
        if st.button("🤖 Run Hybrid AI Text Correction"):
            st.info("Running Hybrid AI correction... Please wait ⏳")

            new_df = df.copy()
            for col in new_df.select_dtypes(include=["object"]).columns:
                new_df[col] = new_df[col].astype(str).apply(
                    lambda x: " ".join([sug[1] for sug in hybrid_text_suggestions(x)])
                )

            st.success("✅ Hybrid AI correction completed!")
            st.dataframe(new_df.head())

            # Download option
            buffer = BytesIO()
            new_df.to_csv(buffer, index=False)
            st.download_button(
                label="📥 Download Cleaned Data (Hybrid AI)",
                data=buffer.getvalue(),
                file_name="hybrid_ai_cleaned.csv",
                mime="text/csv"
            )

        # ---------- CONTEXT AI CORRECTION ----------
        if st.button("🧠 Run Context-Aware AI Correction"):
            st.info("Analyzing text with Context AI logic... Please wait ⏳")

            new_df = df.copy()
            for col in new_df.select_dtypes(include=["object"]).columns:
                new_df[col] = new_df[col].astype(str).apply(gpt_context_correction)

            st.success("✅ Context AI correction completed!")
            st.dataframe(new_df.head())

            # Download option
            buffer = BytesIO()
            new_df.to_csv(buffer, index=False)
            st.download_button(
                label="📥 Download Cleaned Data (Context AI)",
                data=buffer.getvalue(),
                file_name="context_ai_cleaned.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"⚠️ Error processing file: {e}")

else:
    st.warning("Please upload a CSV or Excel file to begin.")