import re
import os
import pandas as pd
from spellchecker import SpellChecker
from langdetect import detect, DetectorFactory
from ai.autocorrect_hybrid import hybrid_text_clean

# Make language detection stable
DetectorFactory.seed = 0


def safe_context_ai_clean(text):
    """
    Lightweight context-aware cleaner.
    Fixes spacing, unwanted characters, and common typos without NLP models.
    """
    if not isinstance(text, str):
        return text

    # Remove unwanted punctuation
    text = re.sub(r"[^a-zA-Z0-9\s,.-]", "", text)
    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()
    # Capitalize properly
    text = text.capitalize()

    return text

# Preload spellcheckers for top global languages
SPELL_CHECKERS = {
    "en": SpellChecker(language='en'),
    "fr": SpellChecker(language='fr'),
    "es": SpellChecker(language='es'),
    "de": SpellChecker(language='de'),
    "it": SpellChecker(language='it')
}

# ✅ Common word corrections (cross-language friendly)
COMMON_REPLACEMENTS = {
    "counrty": "country",
    "adress": "address",
    "hte": "the",
    "teh": "the",
    "recieve": "receive",
    "collge": "college",
    "technlogy": "technology",
    "enviroment": "environment",
    "reserch": "research",
    "inndia": "India",
    "imndfia": "India"
}


def detect_language_safe(text):
    """Detects language safely with fallback."""
    try:
        return detect(text)
    except:
        return "en"


def is_named_entity(word):
    """Heuristic name/place detector without NLP."""
    if not isinstance(word, str) or len(word.strip()) == 0:
        return False

    # Protect common proper nouns and location-style words
    name_like = any(
        word.lower().endswith(suffix)
        for suffix in ["city", "town", "university", "college", "tech", "inc", "ltd"]
    )
    # Protect capitalized single words (like names)
    if word.istitle() and len(word) > 2:
        return True
    return name_like


def correct_word(word, lang):
    """Fix one word while protecting names and language context."""
    clean_word = re.sub(r'[^\w\s]', '', word.lower())

    # Skip names, brands, etc.
    if is_named_entity(word):
        return word

    # Common replacements
    if clean_word in COMMON_REPLACEMENTS:
        corrected = COMMON_REPLACEMENTS[clean_word]
        if word.istitle():
            corrected = corrected.capitalize()
        elif word.isupper():
            corrected = corrected.upper()
        return corrected

    # Spellcheck if available
    spell = SPELL_CHECKERS.get(lang, SPELL_CHECKERS["en"])
    if clean_word and clean_word not in spell:
        suggestion = spell.correction(clean_word)
        if suggestion and suggestion != clean_word:
            if word.istitle():
                suggestion = suggestion.capitalize()
            elif word.isupper():
                suggestion = suggestion.upper()
            return suggestion

    return word


def gpt_context_correction(text):
    """
    Context-aware multilingual correction.
    Detects language per row, protects names, corrects real typos.
    """
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    text = text.strip()
    if text.isdigit() or len(text) <= 2:
        return text

    lang = detect_language_safe(text)
    words = text.split()
    corrected_words = [correct_word(w, lang) for w in words]
    corrected_text = " ".join(corrected_words)
    return re.sub(r'\s+', ' ', corrected_text).strip()


def context_ai_correct(df):
    """
    Multilingual, name-aware, context AI cleaning.
    Auto-skips numeric columns and uses hybrid base clean first.
    """
    try:
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col]):
                continue

            df[col] = df[col].astype(str).fillna("")
            df[col] = df[col].apply(lambda x: gpt_context_correction(hybrid_text_clean(x)))
        return df
    except Exception as e:
        print(f"❌ Context AI correction failed: {e}")
        return df