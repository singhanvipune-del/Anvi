# ai/autocorrect_hybrid.py
import re
import os
from spellchecker import SpellChecker

# Optional semantic correction (only if OPENAI_API_KEY set)
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception:
    client = None

# ----------------------------------------------------------------
# 1️⃣  Domain whitelist (words you NEVER want to autocorrect)
# ----------------------------------------------------------------
WHITELIST = {
    "Drishti", "Kali", "Bharat", "India", "AI", "DataFrame",
    "Streamlit", "Github", "Python", "Maharashtra", "Mumbai",
    "Anvi", "ChatGPT", "NLP"
}

# ----------------------------------------------------------------
# 2️⃣  Initialize local spellchecker
# ----------------------------------------------------------------
spell = SpellChecker(distance=1)
# Optional: load a file of domain terms if you create one
if os.path.exists("custom_words.txt"):
    spell.word_frequency.load_text_file("custom_words.txt")


# ----------------------------------------------------------------
# 3️⃣  Core hybrid correction function
# ----------------------------------------------------------------
def hybrid_text_clean(text: str, use_gpt=True):
    """
    Clean text using a hybrid of local spellchecker + optional GPT.
    Preserves domain words, only changes confident mistakes.
    """
    if not isinstance(text, str) or not text.strip():
        return text

    words = re.findall(r"\b\w+\b", text)
    corrected_words = []

    for word in words:
        # Skip whitelisted or all-caps acronyms
        if word in WHITELIST or word.isupper():
            corrected_words.append(word)
            continue

        # Skip numbers
        if word.isdigit():
            corrected_words.append(word)
            continue

        # Local suggestion
        corrected = spell.correction(word)
        if corrected != word and corrected is not None:
            # Check confidence threshold
            candidates = spell.candidates(word)
            if len(candidates) > 1:
                corrected_words.append(corrected)
            else:
                corrected_words.append(word)
        else:
            corrected_words.append(word)

    corrected_text = re.sub(
        r"\b\w+\b",
        lambda m, cw=iter(corrected_words): next(cw),
        text
    )

    # ----------------------------------------------------------------
    # 4️⃣  GPT semantic layer (optional)
    # ----------------------------------------------------------------
    if use_gpt and client:
        try:
            prompt = (
                "Correct only clear spelling mistakes in this text. "
                "Keep names, technical, or domain words unchanged.\n\n"
                f"Text:\n{corrected_text}"
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a careful proofreader."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            final_text = response.choices[0].message.content.strip()
            return final_text
        except Exception:
            pass  # fallback to local version if API fails

    return corrected_text


# ----------------------------------------------------------------
# 5️⃣  Batch version (for entire dataframe column)
# ----------------------------------------------------------------
def hybrid_text_clean_column(df, column, use_gpt=False):
    if column not in df.columns:
        return df
    df[column] = df[column].astype(str).apply(lambda x: hybrid_text_clean(x, use_gpt=use_gpt))
    return df