import re

def normalize_text_case(text):
    if not isinstance(text, str):
        return text
    return text.strip().title()

def fill_missing_values(record):
    return {k: ("" if v is None else v) for k, v in record.items()}

def remove_duplicates(record):
    return record  # record-level dedupe not needed here

def convert_data_types(record):
    return record  # safe placeholder

def clean_record(record, city_list, country_list):

    record = fill_missing_values(record)

    cleaned = {}

    for key, value in record.items():
        if not isinstance(value, str):
            cleaned[key] = value
            continue

        # Basic cleaning
        v = normalize_text_case(value)

        # City correction
        if "city" in key.lower():
            matches = [c for c in city_list if c.lower() == v.lower()]
            if matches:
                v = matches[0]

        # Country correction
        if "country" in key.lower():
            matches = [c for c in country_list if c.lower() == v.lower()]
            if matches:
                v = matches[0]

        cleaned[key] = v

    return cleaned