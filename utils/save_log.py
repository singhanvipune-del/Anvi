import os
from datetime import datetime

LOG_FILE = os.path.join("logs", "app.log")

def save_log(message: str):
    """Save log messages to logs/app.log with timestamp."""
    os.makedirs("logs", exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")