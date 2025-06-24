import logging
import os
from datetime import UTC, datetime

from src.bot import Config


def add_file_handler(config: Config) -> None:
    os.makedirs("src/logs", exist_ok=True)

    file_handler = logging.FileHandler(
        filename=f"logs/{datetime.now(UTC).strftime('%d%m%Y-%H%M%S')}.log",
        encoding="utf-8",
        mode="w",
    )
    file_handler_formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", "%d-%m-%Y %H:%M:%S", style="{"
    )
    file_handler.setFormatter(file_handler_formatter)

    logging.getLogger().addHandler(file_handler)
