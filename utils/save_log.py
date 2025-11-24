import json
from datetime import datetime


def save_log(action: str, details: dict, logfile="logs/app.log"):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    }

    with open(logfile, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")