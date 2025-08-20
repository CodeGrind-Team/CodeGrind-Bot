import logging

import json_log_formatter

from src.bot import Config


def add_json_handler(config: Config) -> None:
    formatter = json_log_formatter.VerboseJSONFormatter()
    json_handler = logging.StreamHandler()
    json_handler.setFormatter(formatter)
    logging.getLogger().addHandler(json_handler)
