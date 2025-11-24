def autocorrect_name(name: str) -> str:
    """
    Simple name autocorrect:
    - strips spaces
    - title-cases
    - removes digits
    """
    cleaned = ''.join([c for c in name if not c.isdigit()]).strip().title()
    return cleaned