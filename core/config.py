from pathlib import Path
import json

DEFAULT_CONFIG = {
    "tool_name": "Nexus Security Auditor",
    "version": "1.0.0-dev",
    "report_directory": "reports",
    "log_directory": "logs",
    "json_report": True,
    "html_report": True,
    "risk_engine": "default",
    "modules": {
        "system": True,
        "service": True,
        "network": True,
        "process": True,
        "users": True,
        "filesystem": True,
        "permissions": True,
        "password_policy": True,
        "patch": True
    }
}


class Config:
    def __init__(self, filename="config.json"):
        self.path = Path(filename)

        if not self.path.exists():
            self.save(DEFAULT_CONFIG)

        self.data = self.load()

    def load(self):
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data):
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def get(self, key, default=None):
        return self.data.get(key, default)
