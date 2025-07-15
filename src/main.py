import logging
import os
from os import environ

import discord
from dotenv import find_dotenv, load_dotenv

from src.bot import Config, DiscordBot
from src.observability.logging import add_logging_handlers
from src.observability.monitoring import setup_datadog

if __name__ == "__main__":
    load_dotenv(find_dotenv())

    config = Config(
        environ["DISCORD_TOKEN"],
        environ["MONGODB_URI"],
        int(environ["LOGGING_CHANNEL_ID"]),
        int(environ["DEVELOPER_DISCORD_ID"]),
        os.getenv("PRODUCTION", "False") == "True",
        os.getenv("TOPGG_TOKEN"),
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
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
    setup_datadog(config)

    try:
        bot = DiscordBot(intents, config, discord_bot_logger)
        bot.run(config.DISCORD_TOKEN)
    except discord.errors.LoginFailure as e:
        print(f"Login failed: {e}")
