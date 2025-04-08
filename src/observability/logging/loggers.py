from .handlers import add_console_handler, add_file_handler, add_gcp_handler
from src.bot import Config


def add_logging_handlers(config: Config) -> None:
    add_console_handler()
    add_file_handler()
    add_gcp_handler(config)
