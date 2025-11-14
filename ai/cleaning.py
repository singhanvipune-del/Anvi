import re
import unidecode
import spacy
from nameparser import HumanName
from rapidfuzz import fuzz, process
import gender_guesser.detector as gender

nlp = spacy.load("en_core_web_sm")
gender_detector = gender.Detector()

# --------------------------------------------------------------------
# 1. CLEAN TEXT (spelling, punctuation, formatting)
# --------------------------------------------------------------------
def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return text

    text = unidecode.unidecode(text)              # remove accents
    text = re.sub(r'\s+', ' ', text).strip()      # normalize spaces

    doc = nlp(text)
    tokens = []

    for t in doc:
        if t.is_space:
            continue
        if t.like_url or t.like_email:
            tokens.append(t.text.lower())         # normalize emails + urls
        else:
            tokens.append(t.text)

    cleaned = " ".join(tokens)
    return cleaned


# --------------------------------------------------------------------
# 2. FIX NAME (capitalization, order, remove noise)
# --------------------------------------------------------------------
def fix_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        return name

    name = clean_text(name)
    parsed = HumanName(name)
    parsed.capitalize()
    fixed = str(parsed).strip()

    return fixed


# --------------------------------------------------------------------
# 3. GUESS GENDER FROM FIRST NAME (offline)
# --------------------------------------------------------------------
def detect_gender(name: str) -> str:
    name = fix_name(name)
    first = name.split(" ")[0]
    g = gender_detector.get_gender(first)

    if g in ["male", "mostly_male"]:
        return "Male"
    if g in ["female", "mostly_female"]:
        return "Female"
    return "Unknown"


# --------------------------------------------------------------------
# 4. FIX CITY NAMES USING FUZZY MATCH FROM A MASTER LIST
# --------------------------------------------------------------------
def fix_city(input_city: str, city_list: list) -> str:
    if not input_city:
        return input_city

    input_city = clean_text(input_city).title()

    best_match = process.extractOne(
        input_city,
        city_list,
        scorer=fuzz.WRatio
    )

    if best_match and best_match[1] >= 80:   # confidence threshold
        return best_match[0]

    return input_city


# --------------------------------------------------------------------
# 5. FIX COUNTRY NAMES
# --------------------------------------------------------------------
def fix_country(country: str, country_list: list) -> str:
    if not country:
        return country

    country = clean_text(country).title()

    best_match = process.extractOne(
        country,
        country_list,
        scorer=fuzz.WRatio
    )

    if best_match and best_match[1] >= 80:
        return best_match[0]

    return country


# --------------------------------------------------------------------
# 6. FINAL MASTER FUNCTION (used by Streamlit)
# --------------------------------------------------------------------
def clean_record(record: dict, city_list, country_list):
    return {
        "name": fix_name(record.get("name", "")),
        "gender": detect_gender(record.get("name", "")),
        "city": fix_city(record.get("city", ""), city_list),
        "country": fix_country(record.get("country", ""), country_list),
        "email": clean_text(record.get("email", "")),
        "bio": clean_text(record.get("bio", "")),
    }