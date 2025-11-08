import pandas as pd
from fuzzywuzzy import process
import re

# ==========================================
# 🔹 Smart AI + Fuzzy Context Correction
# ==========================================

PROTECTED_NAMES = {
    "Anvi", "Drishti", "Rahul", "Aarav", "Priya", "Neha", "Riya",
    "Saanvi", "Aditya", "Rohan", "Sarthak", "Krishna", "Amit",
    "Arjun", "Ishita", "Sneha", "Raj", "Rakesh", "Kiran", "Pooja",
    "Tanvi", "Manish", "Nisha", "India", "USA", "Google", "Microsoft",
    "Apple", "Amazon"
}

COMMON_FIXES = {
    "counrty": "Country",
    "adress": "Address",
    "roll no": "Roll Number",
    "rollno": "Roll Number",
    "naem": "Name",
    "studnt": "Student",
    "collge": "College",
    "brnach": "Branch",
    "technlogy": "Technology",
    "departmnt": "Department",
    "univercity": "University",
    "facluty": "Faculty",
    "instiute": "Institute"
}


def is_protected_name(value):
    if not isinstance(value, str):
        return False
    clean_val = re.sub(r'[^A-Za-z]', '', value).strip().title()
    return clean_val in PROTECTED_NAMES


def apply_common_fixes(text):
    lower = text.lower().strip()
    if lower in COMMON_FIXES:
        return COMMON_FIXES[lower]
    return text


def clean_text_with_fuzzy(value, reference_list):
    try:
        if not isinstance(value, str):
            return str(value)
        text = value.strip()
        if not text:
            return value

        # Skip numbers or short codes
        if text.isdigit() or len(text) <= 2:
            return value

        # Protect proper names
        if is_protected_name(text):
            return text

        # Apply known corrections
        fixed = apply_common_fixes(text)
        if fixed != text:
            return fixed

        # Fuzzy match correction
        best_match = process.extractOne(text, reference_list)
        if best_match and best_match[1] > 85:
            return best_match[0].title()

        return text.title()
    except Exception:
        return value


def correct_headers(df: pd.DataFrame) -> pd.DataFrame:
    """Fix column names using common fixes and fuzzy matching."""
    corrected_columns = []
    all_known = list(COMMON_FIXES.values())

    for col in df.columns:
        clean_col = col.strip()
        lower_col = clean_col.lower()

        # Apply known corrections
        if lower_col in COMMON_FIXES:
            corrected_columns.append(COMMON_FIXES[lower_col])
            continue

        # Fuzzy match column name
        best_match = process.extractOne(clean_col, all_known)
        if best_match and best_match[1] > 85:
            corrected_columns.append(best_match[0])
        else:
            corrected_columns.append(clean_col.title())

    df.columns = corrected_columns
    return df


def safe_context_ai_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Applies hybrid AI correction on all text columns, skipping numeric/date ones."""
    df_clean = df.copy()

    # ✅ Step 1: Fix headers
    df_clean = correct_headers(df_clean)

    # ✅ Step 2: Fix text values
    for col in df_clean.columns:
        if df_clean[col].dtype == object:
            ref = df_clean[col].dropna().unique().tolist()
            df_clean[col] = df_clean[col].apply(lambda x: clean_text_with_fuzzy(x, ref))
        else:
            continue
    return df_clean