# ai/autocorrect_hybrid.py
import os
import re
from spellchecker import SpellChecker
from fuzzywuzzy import fuzz

CUSTOM_WORDS_PATH = "custom_words.txt"
SIMILARITY_THRESHOLD = 70  # only accept suggestion if similarity >= this

def load_custom_words():
    """Return a set of lowercase whitelist words (no surrounding whitespace)."""
    if os.path.exists(CUSTOM_WORDS_PATH):
        with open(CUSTOM_WORDS_PATH, "r", encoding="utf-8") as f:
            return set(line.strip().lower() for line in f if line.strip())
    return set()

def preserve_casing(original, replacement):
    """Preserve capitalization style of original word when applying replacement."""
    if original.isupper():
        return replacement.upper()
    if original[0].isupper():
        return replacement.capitalize()
    return replacement

def hybrid_text_clean_single(text, debug=False):
    """
    Clean a single text string with whitelist + spellchecker + fuzzy fallback.
    Returns cleaned string.
    """
    if not isinstance(text, str) or not text.strip():
        return text

    spell = SpellChecker()
    whitelist = load_custom_words()

    # split but keep punctuation attached to words
    tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
    cleaned_tokens = []

    for tok in tokens:
        # if token is pure punctuation or single-char punctuation, keep it
        if re.fullmatch(r"[^\w\s]", tok):
            cleaned_tokens.append(tok)
            continue

        original = tok
        clean_lower = re.sub(r"[^\w]", "", original).lower()  # letters+digits only

        # Skip empty after cleaning
        if clean_lower == "":
            cleaned_tokens.append(original)
            continue

        # If in whitelist --> keep original unchanged
        if clean_lower in whitelist:
            if debug: print(f"[WHITELIST] keep '{original}'")
            cleaned_tokens.append(original)
            continue

        # If already likely correct (in spell dictionary), keep original
        if clean_lower in spell:
            if debug: print(f"[OK] word '{original}' recognized")
            cleaned_tokens.append(original)
            continue

        # Try spellchecker
        suggestion = spell.correction(clean_lower) or clean_lower
        sim = fuzz.ratio(clean_lower, suggestion)

        # If suggestion too different, try candidates + best fuzzy
        if suggestion and sim < SIMILARITY_THRESHOLD:
            candidates = list(spell.candidates(clean_lower)) or []
            if candidates:
                # pick candidate with highest fuzzy ratio
                suggestion = max(candidates, key=lambda c: fuzz.ratio(clean_lower, c))
                sim = fuzz.ratio(clean_lower, suggestion)

        # Final decision:
        # - Accept suggestion only if similarity >= threshold
        # - AND suggestion not in whitelist (protect words that appear as suggestions!)
        if suggestion and sim >= SIMILARITY_THRESHOLD and suggestion.lower() not in whitelist:
            final = preserve_casing(original, suggestion)
            if debug: print(f"[REPL] '{original}' -> '{final}' (sim={sim})")
            cleaned_tokens.append(final)
        else:
            if debug:
                print(f"[KEEP] '{original}' kept (best='{suggestion}', sim={sim})")
            cleaned_tokens.append(original)

    # Reconstruct string (simple join: keep no-space before punctuation)
    out = ""
    for i, t in enumerate(cleaned_tokens):
        if i > 0 and not re.fullmatch(r"[^\w\s]", t):  # not punctuation => prefix space
            out += " "
        out += t
    return out

def hybrid_text_clean(df, debug=False):
    """Apply hybrid_text_clean_single to all object/string columns of dataframe."""
    for col in df.select_dtypes(include=['object', 'string']).columns:
        df[col] = df[col].astype(str).apply(lambda x: hybrid_text_clean_single(x, debug=debug))
    return df