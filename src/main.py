import asyncio
import logging
import os
import signal
from os import environ

import discord
from dotenv import find_dotenv, load_dotenv

from src.bot import Config, DiscordBot
from src.observability.logging import add_logging_handlers
from src.observability.monitoring import setup_datadog


async def shutdown(
    signal: signal.Signals, loop: asyncio.AbstractEventLoop, bot: DiscordBot
) -> None:
    logging.info(f"Received exit signal {signal.name}.")
    await bot.close()
    logging.info("Bot has been shut down gracefully.")
    loop.stop()


async def main() -> None:
    load_dotenv(find_dotenv())

    google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    config = Config(
        environ["DISCORD_TOKEN"],
        environ["MONGODB_URI"],
        int(environ["LOGGING_CHANNEL_ID"]),
        int(environ["DEVELOPER_DISCORD_ID"]),
        os.getenv("PRODUCTION", "False") == "True",
        os.getenv("TOPGG_TOKEN"),
        (
            google_application_credentials
            if google_application_credentials is not None
            and os.path.isfile(google_application_credentials)
            else None
        ),
        os.getenv("DD_API_KEY"),
        os.getenv("DD_APP_KEY"),
    )

    logs_path = os.path.join(os.path.dirname(__file__), "logs")
    if not os.path.isdir(logs_path):
        os.makedirs(logs_path)

    intents = discord.Intents.default()
    intents.members = True

    discord_bot_logger = logging.getLogger("discord_bot")
    discord_bot_logger.setLevel(logging.INFO)

    add_logging_handlers(config)

    if config.PRODUCTION:
        setup_datadog(config)

    bot = DiscordBot(intents, config, discord_bot_logger)

    # Gracefully handle shutdown signals.
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, lambda s=sig: asyncio.create_task(shutdown(s, loop, bot))
        )

    try:
        await bot.start(config.DISCORD_TOKEN)
    except discord.errors.LoginFailure as e:
        logging.critical(f"Login failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
