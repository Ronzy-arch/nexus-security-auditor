from datetime import datetime
from pathlib import Path
import json
import hashlib
import os


def utc_now():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def ensure_directory(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def save_json(path, data):
    ensure_directory(Path(path).parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def sha256_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()


def file_size(path):
    return os.path.getsize(path)


def bytes_to_human(size):
    units = ["B", "KB", "MB", "GB", "TB"]

    value = float(size)

    for unit in units:
        if value < 1024:
            return f"{value:.2f} {unit}"
        value /= 1024

    return f"{value:.2f} PB"
