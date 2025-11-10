# utils/cleaning.py
import os, json, time, requests
from rapidfuzz import process, fuzz

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # adjust if needed
MAPPINGS_PATH = os.path.join(BASE_DIR, "data", "user_mappings.json")
WHITELIST_PATH = os.path.join(BASE_DIR, "data", "whitelist.txt")
CHANGELOG_PATH = os.path.join(BASE_DIR, "data", "change_log.json")

PDL_API_KEY = os.environ.get("PDL_API_KEY", "<PUT_YOUR_KEY_HERE>")
PDL_URL = "https://api.peopledatalabs.com/cleaner"  # example endpoint — adapt to actual

# ---------------- storage helpers ----------------
def load_json(path, default):
    if os.path.exists(path):
        try:
            return json.load(open(path, "r", encoding="utf-8"))
        except:
            return default
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

def append_changelog(entry):
    log = load_json(CHANGELOG_PATH, [])
    log.append(entry)
    save_json(CHANGELOG_PATH, log)

# ---------------- whitelist / mappings ----------------
def load_whitelist():
    if not os.path.exists(WHITELIST_PATH):
        return set()
    with open(WHITELIST_PATH, "r", encoding="utf-8") as f:
        return set(l.strip() for l in f.readlines() if l.strip())

def save_whitelist_items(items):
    os.makedirs(os.path.dirname(WHITELIST_PATH), exist_ok=True)
    with open(WHITELIST_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(items)))

def load_user_mappings():
    return load_json(MAPPINGS_PATH, {})

def save_user_mapping(src, target):
    m = load_user_mappings()
    m[src.lower()] = target
    save_json(MAPPINGS_PATH, m)

# ---------------- PDL call (example) ----------------
def call_pdl_clean(value, field_hint=None):
    """
    Call PeopleDataLabs Cleaner API (example). Returns normalized string or None.
    field_hint can be 'city','country','company' to improve results.
    """
    if value is None:
        return None
    params = {
        "api_key": PDL_API_KEY,
        "value": str(value)
    }
    if field_hint:
        params["type"] = field_hint
    try:
        r = requests.get(PDL_URL, params=params, timeout=6)
        r.raise_for_status()
        data = r.json()
        # adapt to actual PDL response:
        # e.g. data['cleaned'] or data['result']['value']
        normalized = data.get("cleaned") or data.get("result") or data.get("value")
        if isinstance(normalized, dict):
            # if the API returns structured entity, pick human-friendly label
            return normalized.get("name") or normalized.get("value")
        return normalized
    except Exception as e:
        # network or API error — fail silently (we will fallback to fuzzy)
        # print("PDL error", e)
        return None

# ---------------- fuzzy fallback ----------------
def fuzzy_fallback(value, candidates, threshold=85):
    """Return best candidate or None"""
    if not value or not candidates:
        return None
    best = process.extractOne(str(value), candidates, scorer=fuzz.WRatio)
    if best and best[1] >= threshold:
        return best[0]
    return None

# ---------------- identifier detection ----------------
import pandas as pd
def is_identifier_column(df, col):
    """
    Simple heuristics to detect roll numbers / IDs / phone numbers which must be protected:
    - mostly numeric
    - short length (<12) and no alpha
    - column name contains 'roll','id','phone','adhar','emp'
    """
    name = col.lower()
    keywords = ["roll", "id", "emp", "phone", "mobile", "adhar", "aadhar", "ssn"]
    if any(k in name for k in keywords):
        return True
    s = df[col].dropna().astype(str)
    # percent numeric
    numeric_frac = (s.str.isnumeric()).mean() if len(s)>0 else 0
    avg_len = s.str.len().mean() if len(s)>0 else 0
    if numeric_frac > 0.8 and avg_len < 12:
        return True
    return False

# ---------------- suggestion pipeline ----------------
def suggest_corrections_for_value(value, col_hint=None, reference_list=None):
    """
    Returns tuple (suggestion, source)
    source in {"user", "pdl", "fuzzy", None}
    """
    v = "" if value is None else str(value).strip()
    if v == "":
        return None, None

    # 1) user mapping
    mappings = load_user_mappings()
    if v.lower() in mappings:
        return mappings[v.lower()], "user"

    # 2) PDL normalization (best for city/country/company)
    if col_hint in ("country","city","company","org","company_name"):
        p = call_pdl_clean(v, field_hint=col_hint)
        if p and p.lower() != v.lower():
            return p, "pdl"

    # 3) fuzzy fallback against reference list (if provided)
    if reference_list:
        f = fuzzy_fallback(v, reference_list)
        if f and f.lower() != v.lower():
            return f, "fuzzy"

    # nothing
    return None, None