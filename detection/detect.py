# detect/detect_duplicates.py
import pandas as pd
from rapidfuzz import fuzz
from typing import List, Dict

def fuzzy_duplicate_pairs(df: pd.DataFrame, threshold: int = 85, sample_limit: int = 2000) -> pd.DataFrame:
    """
    Return DataFrame with candidate fuzzy duplicate pairs:
    columns: row_i, row_j, score.
    Note: O(n^2) complexity. For large df, sample or use blocking.
    sample_limit: if len(df) > sample_limit, function will use blocking by fingerprint (first 3 letters).
    """
    df = df.reset_index(drop=True)
    n = len(df)
    if n < 2:
        return pd.DataFrame(columns=["row_i", "row_j", "score"])

    rows = []
    row_texts = [" ".join(map(str, df.iloc[i].astype(str).values)).lower() for i in range(n)]

    # Simple blocking for large datasets
    if n > sample_limit:
        # group indices by first 3 chars fingerprint to reduce comparisons
        buckets = {}
        for i, txt in enumerate(row_texts):
            key = txt[:3] if len(txt) >= 3 else txt
            buckets.setdefault(key, []).append(i)

        for key, idxs in buckets.items():
            for i in range(len(idxs)):
                for j in range(i + 1, len(idxs)):
                    a, b = idxs[i], idxs[j]
                    score = fuzz.WRatio(row_texts[a], row_texts[b])
                    if score >= threshold:
                        rows.append({"row_i": int(a), "row_j": int(b), "score": int(score)})
    else:
        for i in range(n):
            for j in range(i + 1, n):
                score = fuzz.WRatio(row_texts[i], row_texts[j])
                if score >= threshold:
                    rows.append({"row_i": int(i), "row_j": int(j), "score": int(score)})

    return pd.DataFrame(rows)
