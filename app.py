import streamlit as st
import pandas as pd
from io import BytesIO
from openai import OpenAI
import concurrent.futures
import tiktoken  # for accurate token estimation

# ==================== 🧠 OpenAI Setup ====================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Token cost rates (USD per 1M tokens)
COST_INPUT = 0.15 / 1_000_000   # gpt-4o-mini input
COST_OUTPUT = 0.60 / 1_000_000  # gpt-4o-mini output

# ==================== ⚙️ Helper: Token Estimation ====================
def estimate_tokens(text):
    """Estimate token count for pricing."""
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

# ==================== 🧹 AI Correction Function ====================
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
.main {background-color: #ffffff; border-radius: 12px; padding: 25px 40px; box-shadow: 0px 4px 20px rgba(0,0,0,0.05);}
h1 {color: #5c4dff; text-align: center;}
.stButton button {background: linear-gradient(90deg, #6a11cb, #2575fc); color: white; font-weight: 600; border-radius: 8px;}
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
            df.columns = df.columns.str.lower().str.strip()
            df = df.applymap(lambda x: x.strip().title() if isinstance(x, str) else x)
            df = df.drop_duplicates()
            text_columns = df.select_dtypes(include=["object"]).columns

            cache = {}
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

            # Apply cleaned results back to DataFrame
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

            # 🧮 Estimate total cost
            for col in text_columns:
                for val in df[col]:
                    total_input_tokens += estimate_tokens(str(val))
                    total_output_tokens += estimate_tokens(str(val))

            estimated_cost = (total_input_tokens * COST_INPUT) + (total_output_tokens * COST_OUTPUT)

            progress.progress(100)
            st.success("✅ AI Cleaning Complete!")
            st.balloons()

            st.write("### 🧼 Cleaned Data Preview")
            st.dataframe(df.head(), use_container_width=True)

            # 💵 Show Estimated Cost
            st.markdown(f"### 💰 *Estimated OpenAI Cost: ${estimated_cost:.4f} USD*")

            # 🧾 Downloads
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
