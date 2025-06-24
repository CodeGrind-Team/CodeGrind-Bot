from src.bot import Config

from .handlers import add_console_handler, add_file_handler, add_gcp_handler


def add_logging_handlers(config: Config) -> None:
    add_console_handler(config)
    add_file_handler(config)
    add_gcp_handler(config)
