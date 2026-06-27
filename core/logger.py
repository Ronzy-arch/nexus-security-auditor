import logging
from pathlib import Path

class NexusLogger:
    def __init__(self, log_dir="logs", filename="nexus.log"):
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("Nexus")

        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)

            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s"
            )

            file_handler = logging.FileHandler(
                Path(log_dir) / filename,
                encoding="utf-8"
            )
            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
