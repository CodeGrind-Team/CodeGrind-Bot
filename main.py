"""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python
programming language.

Version: 6.1.0
"""

import logging
import os
import platform
from dataclasses import dataclass
from datetime import UTC, datetime

import discord
import topgg
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import find_dotenv, load_dotenv
from html2image import Html2Image

from constants import GLOBAL_LEADERBOARD_ID
from database.setup import init_mongodb_conn
from utils.dev_utils import ChannelLogger
from utils.notifications_utils import (
    send_daily_question_and_update_stats,
    send_daily_question_and_update_stats_schedule,
)
from utils.ratings_utils import Ratings

load_dotenv(find_dotenv())

logs_path = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.isdir(logs_path):
    os.makedirs(logs_path)

intents = discord.Intents.default()
intents.members = True


class LoggingFormatter(logging.Formatter):
    # Colours
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLOURS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_colour = self.COLOURS[record.levelno]
        format = "(black){asctime}(reset) (levelcolour){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolour)", log_colour)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

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

logger.addHandler(file_handler)


@dataclass
class Config:
    DISCORD_TOKEN: str
    MONGODB_URI: str
    TOPGG_TOKEN: str
    BROWSER_EXECUTABLE_PATH: str
    LOGGING_CHANNEL_ID: int
    SYNC_COMMANDS: bool
    PRODUCTION: bool
    MAINTENANCE: bool
    UPDATE_STATS_ON_START: bool
    DAILY_RESET_ON_START: bool
    WEEKLY_RESET_ON_START: bool
    MONTHLY_RESET_ON_START: bool


class DiscordBot(commands.Bot):
    def __init__(self, config: Config, logger: logging.Logger) -> None:
        super().__init__(
            command_prefix=",",
            intents=intents,
            help_command=None,
        )
        """
        This creates custom bot variables so that we can access these variables in cogs
        more easily.
        """
        self.config = config
        self.logger = logger
        self.html2image = Html2Image(browser_executable=config.BROWSER_EXECUTABLE_PATH)
        self.channel_logger = None
        self.topggpy = None

    async def on_autopost_success(self):
        """Runs when stats are posted to topgg"""
        self.logger.info(
            "Posted server count (%s), shard count (%s)",
            self.topggpy.guild_count,
            self.shard_count,
        )

        self.logger.info(
            "Total bot member count (%s)", len(set(self.get_all_members()))
        )

    async def init_topgg(self) -> None:
        if self.config.PRODUCTION:
            self.topggpy = topgg.DBLClient(
                self, self.config.TOPGG_TOKEN, autopost=True, post_shard_count=True
            )

    # async def on_guild_remove(self) -> None:
    #     # TODO: data removal
    #     pass

    # async def on_member_remove(self) -> None:
    #     # TODO: data removal
    #     pass

    # async def on_member_update(self) -> None:
    #     # TODO: data removal
    #     pass

    async def load_cogs(self) -> None:
        """
        The code in this function is executed whenever the bot will start.
        """
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to load extension {extension}\n{exception}"
                    )

    async def on_ready(self) -> None:
        self.logger.info("file: main.py ~ on_ready ~ start")

        if self.config.MAINTENANCE:
            await self.change_presence(
                status=discord.Status.do_not_disturb,
                activity=discord.Game(name="Under Maintenance"),
            )

        update_stats_on_start = self.config.UPDATE_STATS_ON_START
        daily_reset_on_start = self.config.DAILY_RESET_ON_START
        weekly_reset_on_start = self.config.WEEKLY_RESET_ON_START
        monthly_reset_on_start = self.config.MONTHLY_RESET_ON_START

        if update_stats_on_start or daily_reset_on_start or weekly_reset_on_start:
            await send_daily_question_and_update_stats(
                update_stats_on_start,
                daily_reset_on_start,
                weekly_reset_on_start,
                monthly_reset_on_start,
            )

    async def setup_hook(self) -> None:
        """
        This will just be executed when the bot starts the first time.
        """
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")

        await init_mongodb_conn(self.config.MONGODB_URI, GLOBAL_LEADERBOARD_ID)
        await self.load_cogs()
        await self.init_topgg()
        self.channel_logger = ChannelLogger(self, int(os.environ["LOGGING_CHANNEL_ID"]))
        self.ratings = await Ratings.create("ratings.txt")

        if self.config.SYNC_COMMANDS:
            # Sync commands globally
            await self.tree.sync()

        send_daily_question_and_update_stats_schedule.start()

    async def on_interaction(self, interaction: discord.Interaction) -> None:
        """
        The code in this event is executed every time a normal command has been
        *successfully* executed.

        :param context: The context of the command that has been executed.
        """
        if not interaction.command:
            return

        full_command_name = interaction.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if interaction.guild is not None:
            self.logger.info(
                f"Executed /{executed_command} command in {interaction.guild.name} (ID: {interaction.guild.id}) by {interaction.user.name} (ID: {interaction.user.id})"
            )
        else:
            self.logger.info(
                f"Executed /{executed_command} command by {interaction.user.name} (ID: {interaction.user.id}) in DMs"
            )


async def on_error(
    interaction: discord.Interaction, error: discord.app_commands.AppCommandError
) -> None:
    """
    The code in this event is executed every time a normal valid command catches an error.

    :param context: The context of the normal command that failed executing.
    :param error: The error that has been faced.
    """
    if isinstance(error, discord.app_commands.errors.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            description=f"**Please slow down** - You can use this command again in \
                {f'{round(hours)} hours' if round(hours) > 0 else ''} \
                    {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} \
                        {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
            colour=0xE02B2B,
        )
        await interaction.response.send_message(embed=embed)
    elif isinstance(error, discord.app_commands.errors.MissingPermissions):
        embed = discord.Embed(
            description="You are missing the permission(s) `"
            + ", ".join(error.missing_permissions)
            + "` to execute this command!",
            colour=0xE02B2B,
        )
        await interaction.response.send_message(embed=embed)
    elif isinstance(error, discord.app_commands.errors.BotMissingPermissions):
        embed = discord.Embed(
            description="I am missing the permission(s) `"
            + ", ".join(error.missing_permissions)
            + "` to fully perform this command!",
            colour=0xE02B2B,
        )
        await interaction.response.send_message(embed=embed)
    else:
        raise error


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

bot = DiscordBot(config, logger)
bot.tree.on_error = on_error
bot.run(config.DISCORD_TOKEN)
