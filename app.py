import streamlit as st
import pandas as pd
from io import BytesIO
from openai import OpenAI
import time

# ==================== 🧠 OpenAI Setup ====================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.write("🔑 Testing OpenAI API...")

try:
    response = client.responses.create(model="gpt-4o-mini", input="Hello!")
    st.success("✅ OpenAI API key works fine!")
except Exception as e:
    st.error(f"❌ OpenAI API test failed: {e}")


# ==================== ⚙️ AI Correction Function ====================
def correct_entity_openai(value: str, column_name: str = ""):
    """Use GPT to correct names, cities, or countries intelligently."""
    if not isinstance(value, str) or not value.strip():
        return value
    try:
        prompt = f"""
You are a data cleaner AI. Correct any spelling mistakes, spacing issues, or capitalization in this {column_name} value.
Return only the corrected text. Do not add explanations or extra words.

Examples:
Input: Imndfia → Output: India
Input: mahendrasingh → Output: Mahendra Singh
Input: pune → Output: Pune

Now correct this:
"{value}"
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("⚠️ OpenAI error:", e)
        return value


# ==================== 🌟 Streamlit Page Config ====================
st.set_page_config(
    page_title="CleanChain AI",
    page_icon="✨",
    layout="wide",
)

# ==================== 🎨 Styles ====================
st.markdown("""
<style>
body {background-color: #f8f9fa; color: #212529;}
.main {background-color: #ffffff; border-radius: 12px; padding: 25px 40px; box-shadow: 0px 4px 20px rgba(0,0,0,0.05);}
h1 {color: #5c4dff; text-align: center; font-family: 'Poppins', sans-serif; font-weight: 700;}
.stButton button {
    background: linear-gradient(90deg, #6a11cb, #2575fc);
    color: white; font-weight: 600; border: none; border-radius: 8px;
    padding: 0.6rem 1.2rem; transition: all 0.3s ease-in-out;
}
.stButton button:hover {transform: scale(1.05);}
.stDownloadButton button {
    background: linear-gradient(90deg, #43cea2, #185a9d);
    color: white; border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# ==================== 🧾 App Header ====================
st.title("✨ CleanChain AI — Smart Data Cleaner")
st.caption("🚀 Instantly clean, correct & format your data using OpenAI GPT")

# ==================== 📤 File Upload ====================
uploaded_file = st.file_uploader("📤 Upload CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file:
    file_name = uploaded_file.name.lower()
    df = pd.read_csv(uploaded_file) if file_name.endswith(".csv") else pd.read_excel(uploaded_file)

    st.write("### 🧾 Original Data Preview")
    st.dataframe(df.head(), use_container_width=True)

import concurrent.futures

if st.button("✨ Clean & Correct Data"):
    progress = st.progress(0)
    status_text = st.empty()
    with st.spinner("AI is cleaning your data... ⏳"):

        # Step 1️⃣ Normalize Data
        progress.progress(10)
        status_text.text("🔧 Preprocessing data...")
        df.columns = df.columns.str.lower().str.strip()
        df = df.applymap(lambda x: x.strip().title() if isinstance(x, str) else x)
        df = df.drop_duplicates()

        # Step 2️⃣ Parallel AI Correction
        text_columns = df.select_dtypes(include=["object"]).columns
        total_cells = len(df) * len(text_columns)
        done = 0
        cache = {}


        def process_value(val, col):
            key = (col, str(val).strip().lower())
            if key not in cache:
                cache[key] = correct_entity_openai(val, col)
            return cache[key]


        for col in text_columns:
            st.write(f"🧹 Cleaning column: {col}")
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(process_value, val, col): i for i, val in enumerate(df[col])}
                cleaned_values = []
                for future in concurrent.futures.as_completed(futures):
                    cleaned_values.append(future.result())
                    done += 1
                    if done % 10 == 0:
                        progress.progress(min(95, int((done / total_cells) * 100)))
                        status_text.text(f"✨ Cleaning {col}: {min(95, int((done / total_cells) * 100))}% complete...")
            df[col] = cleaned_values

        # Step 3️⃣ Finalize
        progress.progress(100)
        st.success("✅ AI Cleaning Complete!")
        st.balloons()

        st.write("### 🧼 Cleaned Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        # Step 4️⃣ Downloads
        csv_data = df.to_csv(index=False).encode("utf-8")
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="CleanedData")
        excel_data = excel_buffer.getvalue()

        col1, col2 = st.columns(2)
        with col1:
            st.download_button("⬇️ Download CSV", csv_data, "cleaned_data.csv", "text/csv")
        with col2:
            st.download_button(
                "📊 Download Excel",
                excel_data,
                "cleaned_data.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
