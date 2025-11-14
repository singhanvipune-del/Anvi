import streamlit as st
import pandas as pd
from io import BytesIO
from cleaning import clean_dataframe

st.set_page_config(page_title="AI Data Cleaning", page_icon="🧹", layout="wide")

st.title("🧠 AI Data Cleaning App")
st.write("Upload your dataset and get AI-based name & spelling corrections instantly!")

uploaded_file = st.file_uploader("📤 Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ File uploaded successfully!")
        st.subheader("📋 Original Data Preview")
        st.dataframe(df.head())

        # Clean the data
        with st.spinner("🧠 Cleaning data... please wait..."):
            cleaned_df, corrections = clean_dataframe(df.copy())

        # Show cleaned data
        st.subheader("✅ Cleaned Data")
        st.dataframe(cleaned_df)

        # Show corrections made
        if corrections:
            st.subheader("🔍 Corrections Made")
            st.json(corrections)
        else:
            st.info("✨ No spelling or name corrections were required!")

        # Download buttons
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name="Cleaned Data")
            return output.getvalue()

        excel_data = to_excel(cleaned_df)
        csv_data = cleaned_df.to_csv(index=False).encode('utf-8')

        st.download_button("📥 Download Cleaned Excel", data=excel_data, file_name="cleaned_data.xlsx")
        st.download_button("📥 Download Cleaned CSV", data=csv_data, file_name="cleaned_data.csv")

    except Exception as e:
        st.error(f"❌ Error while processing file: {str(e)}")

else:
    st.info("👆 Please upload a CSV or Excel file to get started.")