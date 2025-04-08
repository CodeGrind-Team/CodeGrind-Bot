import google.cloud.logging

from src.bot import Config


def add_gcp_handler(config: Config) -> None:
    if not config.GOOGLE_APPLICATION_CREDENTIALS:
        return

    google_cloud_client = google.cloud.logging.Client()
    google_cloud_client.setup_logging()
