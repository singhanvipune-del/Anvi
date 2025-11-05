import re
from ai.autocorrect_hybrid import hybrid_text_clean  # ✅ Import hybrid layer safely

def gpt_context_correction(text):
    """
    Context-based AI text correction (light version).
    Detects simple spelling and domain-level issues and fixes them.
    Safe conversion for numeric and non-string inputs included.
    """

    # ✅ Safety check (prevents float/object errors)
    if not isinstance(text, str):
        text = str(text) if text is not None else ""

    # Simple normalization
    text = text.strip()

    # Common word corrections — you can expand this dictionary anytime
    replacements = {
        "counrty": "country",
        "adress": "address",
        "imndfia": "India",
        "rooll": "roll",
        "rool": "roll",
        "correctionn": "correction",
        "hte": "the",
        "teh": "the",
        "recieve": "receive",
        "adresss": "address",
        "studnt": "student",
        "collge": "college",
        "technlogy": "technology",
        "enviroment": "environment",
        "reserch": "research",
        "drishti": "Drishti"  # protect proper noun
    }

    # Apply the corrections
    def correct_word(word):
        clean_word = re.sub(r'[^\w\s]', '', word.lower())  # strip punctuation for match
        if clean_word in replacements:
            corrected = replacements[clean_word]
            # Preserve capitalization style
            if word.istitle():
                corrected = corrected.capitalize()
            elif word.isupper():
                corrected = corrected.upper()
            return corrected
        return word

    words = text.split()
    corrected_words = [correct_word(word) for word in words]
    corrected_text = " ".join(corrected_words)

    # Optional: remove extra spaces
    corrected_text = re.sub(r'\s+', ' ', corrected_text).strip()

    return corrected_text


def safe_context_ai_clean(df):
    """
    Safely runs hybrid and context-aware cleaning on a DataFrame.
    Converts all non-string cells to string and handles errors gracefully.
    """
    try:
        for col in df.select_dtypes(include=['object', 'string']).columns:
            df[col] = df[col].astype(str).fillna("")
            df[col] = df[col].apply(lambda x: gpt_context_correction(hybrid_text_clean(x)))
        return df
    except Exception as e:
        print(f"❌ Context AI correction failed: {e}")
        return df