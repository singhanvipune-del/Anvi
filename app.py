import streamlit as st
import pandas as pd
import json

# ---- Import your cleaning logic ----
from cleaning import clean_record

# ---- Load master data (cities, countries) ----
@st.cache_data
def load_city_list():
    try:
        df = pd.read_csv("world_cities.csv")
        return df["city"].dropna().unique().tolist()
    except:
        return []

@st.cache_data
def load_country_list():
    try:
        df = pd.read_csv("countries.csv")
        return df["country"].dropna().unique().tolist()
    except:
        return []

city_list = load_city_list()
country_list = load_country_list()


# -----------------------------------------------------
#                   STREAMLIT UI
# -----------------------------------------------------
st.set_page_config(page_title="AI Data Cleaning", page_icon="🤖", layout="wide")
st.title("🤖 AI Data Cleaning App")
st.markdown("Upload your file and get perfectly cleaned data using AI-enhanced rules.")

uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])


if uploaded_file is not None:

    # --- Read file ---
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, dtype=str)
    else:
        df = pd.read_excel(uploaded_file, dtype=str)

    st.write("### 📌 Original Data (top rows)")
    st.dataframe(df.head())

    # ---- CLEAN THE DATA ----
    cleaned_rows = []

    for _, row in df.iterrows():
        cleaned_row = clean_record(row.to_dict(), city_list, country_list)
        cleaned_rows.append(cleaned_row)

    cleaned_df = pd.DataFrame(cleaned_rows)

    st.success("✅ Data cleaned successfully!")
    st.write("### 🧹 Cleaned Data Preview")
    st.dataframe(cleaned_df.head())

    # ---- DOWNLOAD OPTIONS ----
    cleaned_csv = cleaned_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Cleaned CSV",
        cleaned_csv,
        "cleaned_data.csv",
        "text/csv"
    )

    cleaned_df.to_excel("cleaned_data.xlsx", index=False)
    with open("cleaned_data.xlsx", "rb") as f:
        st.download_button(
            "📘 Download Cleaned Excel",
            f,
            file_name="cleaned_data.xlsx"
        )

else:
    st.info("👆 Upload a CSV or Excel file to begin.")