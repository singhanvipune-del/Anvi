# autocorrect_hybrid.py
import re

# Basic dictionary for autocorrect (you can expand)
CORRECTIONS = {
    "mumbay": "Mumbai",
    "delhy": "Delhi",
    "newyorkk": "New York",
    "inder": "India",
}

def autocorrect_name(name: str) -> str:
    """
    Automatically corrects names of people, cities, countries, things.
    Uses rule-based & dictionary-based correction.
    """
    if not isinstance(name, str):
        return name

    cleaned = name.strip().title()

    # Dictionary correction
    if cleaned.lower() in CORRECTIONS:
        return CORRECTIONS[cleaned.lower()]

    # Remove extra spaces / special chars
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned