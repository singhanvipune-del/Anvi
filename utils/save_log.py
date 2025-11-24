# utils/save_log.py
import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)

def save_log(msg: str):
    ensure_log_dir()
    ts = datetime.utcnow().isoformat(timespec="seconds")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ts} - {msg}\n")