# utils/storage.py
import os

def save_file_bytes(file_bytes, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(file_bytes)
    return dest_path