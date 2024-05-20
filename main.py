"""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python
programming language.

Version: 6.1.0
"""

import logging
import os
from datetime import UTC, datetime

import discord
from dotenv import find_dotenv, load_dotenv

from bot import Config, DiscordBot, LoggingFormatter, on_error

if __name__ == "__main__":
    load_dotenv(find_dotenv())

    logs_path = os.path.join(os.path.dirname(__file__), "logs")
    if not os.path.isdir(logs_path):
        os.makedirs(logs_path)

    intents = discord.Intents.default()
    intents.members = True

    logger = logging.getLogger("discord_bot")
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(LoggingFormatter())

    # File handler
    file_handler = logging.FileHandler(
        filename=f"logs/{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}.log",
        encoding="utf-8",
        mode="w",
    )
    file_handler_formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
    )
    file_handler.setFormatter(file_handler_formatter)

    logger.addHandler(console_handler)
    logging.getLogger().addHandler(file_handler)

    config = Config(
        os.getenv("DISCORD_TOKEN"),
        os.getenv("MONGODB_URI"),
        os.getenv("TOPGG_TOKEN"),
        os.getenv("BROWSER_EXECUTABLE_PATH"),
        int(os.getenv("LOGGING_CHANNEL_ID")),
        os.getenv("SYNC_COMMANDS", "False") == "True",
        os.getenv("PRODUCTION", "False") == "True",
        os.getenv("MAINTENANCE", "False") == "True",
        os.getenv("UPDATE_STATS_ON_START", "False") == "True",
        os.getenv("DAILY_RESET_ON_START", "False") == "True",
        os.getenv("WEEKLY_RESET_ON_START", "False") == "True",
        os.getenv("MONTHLY_RESET_ON_START", "False") == "True",
    )

    bot = DiscordBot(intents, config, logger)
    bot.tree.on_error = on_error
    bot.run(config.DISCORD_TOKEN)
