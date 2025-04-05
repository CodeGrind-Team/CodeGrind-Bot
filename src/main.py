"""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python
programming language.

Version: 6.1.0

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
file except in compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an " AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
ANY KIND, either express or implied. See the License for the specific language
governing permissions and limitations under the License.
"""

import logging
import os
from datetime import UTC, datetime

import discord
import google.cloud.logging
from dotenv import find_dotenv, load_dotenv


from src.bot import Config, DiscordBot, LoggingFormatter


if __name__ == "__main__":
    load_dotenv(find_dotenv())

    config = Config(
        os.getenv("DISCORD_TOKEN"),
        os.getenv("MONGODB_URI"),
        os.getenv("TOPGG_TOKEN"),
        os.getenv("BROWSER_EXECUTABLE_PATH"),
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        int(os.getenv("LOGGING_CHANNEL_ID")),
        int(os.getenv("DEVELOPER_DISCORD_ID")),
        os.getenv("PRODUCTION", "False") == "True",
    )

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
        filename=f"logs/{datetime.now(UTC).strftime('%d%m%Y-%H%M%S')}.log",
        encoding="utf-8",
        mode="w",
    )
    file_handler_formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", "%d-%m-%Y %H:%M:%S", style="{"
    )
    file_handler.setFormatter(file_handler_formatter)

    logger.addHandler(console_handler)
    logging.getLogger().addHandler(file_handler)

    if config.GOOGLE_APPLICATION_CREDENTIALS:
        google_cloud_client = google.cloud.logging.Client()
        google_cloud_client.setup_logging()

    bot = DiscordBot(intents, config, logger)
    bot.run(config.DISCORD_TOKEN)
    try:
        bot.run(config.DISCORD_TOKEN)
    except discord.errors.LoginFailure as e:
        print(f"Login failed: {e}")
