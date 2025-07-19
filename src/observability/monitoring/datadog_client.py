from datadog import initialize

from src.bot import Config

DD_STATSD_HOST = "datadog"
DD_STATSD_PORT = 8125


def setup_datadog(config: Config) -> None:
    initialize(
        api_key=config.DD_API_KEY,
        app_key=config.DD_APP_KEY,
        statsd_host=DD_STATSD_HOST,
        statsd_port=DD_STATSD_PORT,
    )
