from src.bot import Config

from .handlers import add_console_handler, add_file_handler, add_json_handler

PRODUCTION_HANDLERS = [add_json_handler]
NON_PRODUCTION_HANDLERS = [
    add_console_handler,
    add_file_handler,
    # add_gcp_handler
]


def add_logging_handlers(config: Config) -> None:
    handlers = PRODUCTION_HANDLERS if config.PRODUCTION else NON_PRODUCTION_HANDLERS

    for handler in handlers:
        handler(config)
