from datadog import initialize

from src.bot import Config


def setup_datadog(config: Config) -> None:
    initialize(api_key=config.DD_API_KEY, app_key=config.DD_APP_KEY)
