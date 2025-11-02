import pandas as pd
from spellchecker import SpellChecker
import openai
import os

# Optional: set your API key via environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

spell = SpellChecker()


def local_spell_fix(word):
    if not isinstance(word, str) or word.strip() == "":
        return word
    corrected = spell.correction(word)
    return corrected if corrected else word


def gpt_smart_fix(word):
    if not isinstance(word, str) or word.strip() == "":
        return word
    try:
        prompt = f"Correct the following text for spelling or meaning, but keep it short and relevant: '{word}'"
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )
        return response.choices[0].message["content"].strip()
    except Exception:
        return word  # fallback


def hybrid_text_clean(df: pd.DataFrame, text_cols=None):
    if text_cols is None:
        text_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()

    for col in text_cols:
        cleaned_col = []
        for val in df[col]:
            val_str = str(val)
            local_fixed = local_spell_fix(val_str)
            if local_fixed != val_str:  # local fix worked
                cleaned_col.append(local_fixed)
            else:
                ai_fixed = gpt_smart_fix(val_str)
                cleaned_col.append(ai_fixed)
        df[col] = cleaned_col
    return df