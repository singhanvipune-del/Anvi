import streamlit as st
import pandas as pd
from io import BytesIO
from openai import OpenAI
import concurrent.futures
import re
import tiktoken  # for accurate token estimation

# ==================== 🧠 OpenAI Setup ====================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Token cost rates (USD per 1M tokens)
COST_INPUT = 0.15 / 1_000_000  # gpt-4o-mini input
COST_OUTPUT = 0.60 / 1_000_000  # gpt-4o-mini output


# ==================== ⚙️ Helper: Token Estimation ====================
def estimate_tokens(text):
    """Estimate token count for pricing."""
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


# ==================== ⚙️ Local Header Cleaning ====================
def locally_clean_header(name: str):
    """Perform fast local cleaning before using GPT."""
    if not isinstance(name, str):
        return name
    name = name.strip().lower()
    name = re.sub(r'[_\-]+', ' ', name)  # replace _ or - with space
    name = re.sub(r'\s+', ' ', name)  # remove double spaces
    name = name.replace('.', '').strip()
    common_corrections = {
        "fname": "first name",
        "lname": "last name",
        "phn": "phone",
        "phn no": "phone number",
        "rollno": "roll no",
        "rool no": "roll no",
        "empname": "employee name",
        "emp id": "employee id",
        "counntry": "country"
    }
    return common_corrections.get(name, name)


# ==================== 🧠 GPT Header Correction ====================
def correct_column_name(name: str):
    """Use GPT only if local cleaning didn't fix it."""
    if not isinstance(name, str) or not name.strip():
        return name
    local = locally_clean_header(name)

    # Skip GPT if the cleaned version is short and contains only letters/spaces
    if re.match(r'^[a-z ]+$', local) and len(local) > 2:
        return local

    try:
        prompt = f"""
You are a data cleaning assistant. Correct any spelling, spacing, or casing mistakes in this column name.
Return only the corrected column name without explanations.

Examples:
Input: rooll no → Output: roll no
Input: counntry → Output: country
Input: emp name → Output: employee name
Input: phn no → Output: phone number

Now correct this:
"{name}"
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        print("⚠️ Column correction error:", e)
        return local


# ==================== 🧹 AI Cell Correction ====================
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
st.set_page_config(page_title="CleanChain AI", page_icon="✨", layout="wide")

st.markdown("""
<style>
.main {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 25px 40px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.05);
}
h1 {color: #5c4dff; text-align: center;}
.stButton button {
    background: linear-gradient(90deg, #6a11cb, #2575fc);
    color: white;
    font-weight: 600;
    border-radius: 8px;
}
.stButton button:hover {transform: scale(1.05);}
</style>
""", unsafe_allow_html=True)

# ==================== 🧾 Header ====================
st.title("✨ CleanChain AI — Smart Data Cleaner")
st.caption("🚀 Instantly clean, correct & format your data using OpenAI GPT")

# ==================== 📤 File Upload ====================
uploaded_file = st.file_uploader("📤 Upload CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    st.write("### 🧾 Original Data Preview")
    st.dataframe(df.head(), use_container_width=True)

    if st.button("✨ Clean & Correct Data"):
        progress = st.progress(0)
        with st.spinner("AI is cleaning your data... ⏳"):

            # Step 1️⃣ — Correct Column Headers (Local + GPT fallback)
            st.write("🧭 Correcting column headers...")
            new_columns = []
            for col in df.columns:
                corrected = correct_column_name(col)
                new_columns.append(corrected)
            df.columns = new_columns  # ✅ actually updates DataFrame headers

            # Step 2️⃣ — Local Cleaning
            progress.progress(25)
            df = df.applymap(lambda x: x.strip().title() if isinstance(x, str) else x)
            df = df.drop_duplicates()

            # Step 3️⃣ — GPT Cleaning for Text Columns
            progress.progress(50)
            cache = {}
            text_columns = df.select_dtypes(include=["object"]).columns
            total_input_tokens, total_output_tokens = 0, 0

            # Process in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for col in text_columns:
                    st.write(f"🧹 Cleaning column: {col}")
                    for i, val in enumerate(df[col]):
                        key = (col, str(val).strip().lower())
                        if key not in cache:
                            futures.append(executor.submit(correct_entity_openai, val, col))
                results = [f.result() for f in futures]

            # Step 4️⃣ — Apply Results Back
            idx = 0
            for col in text_columns:
                new_col = []
                for val in df[col]:
                    key = (col, str(val).strip().lower())
                    if key not in cache:
                        cache[key] = results[idx]
                        idx += 1
                    new_col.append(cache[key])
                df[col] = new_col

            # Step 5️⃣ — Cost Estimation
            progress.progress(90)
            for col in text_columns:
                for val in df[col]:
                    total_input_tokens += estimate_tokens(str(val))
                    total_output_tokens += estimate_tokens(str(val))
            estimated_cost = (total_input_tokens * COST_INPUT) + (total_output_tokens * COST_OUTPUT)

            # Step 6️⃣ — Display & Download
            progress.progress(100)
            st.success("✅ AI Cleaning Complete!")
            st.balloons()

            st.write("### 🧼 Cleaned Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            st.markdown(f"### 💰 *Estimated OpenAI Cost: ${estimated_cost:.4f} USD*")

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
