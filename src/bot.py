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
import platform
from dataclasses import dataclass
from typing import Any

import aiohttp
import discord
import topgg
from beanie.odm.operators.update.general import Set
from discord.ext import commands
from html2image import Html2Image

from src.constants import GLOBAL_LEADERBOARD_ID
from src.database.models import Profile, Server
from src.database.setup import initialise_mongodb_connection
from src.utils.dev import ChannelLogger, dev_commands
from src.utils.http_client import HttpClient
from src.utils.neetcode import NeetcodeSolutions
from src.utils.ratings import Ratings
from src.utils.schedules import (
    schedule_prune_members_and_guilds,
    schedule_question_and_stats_update,
    schedule_update_neetcode_solutions,
    schedule_update_zerotrac_ratings,
)
from src.utils.users import delete_user, unlink_user_from_server


@dataclass
class Config:
    DISCORD_TOKEN: str
    MONGODB_URI: str
    BROWSER_EXECUTABLE_PATH: str
    LOGGING_CHANNEL_ID: int
    DEVELOPER_DISCORD_ID: int
    PRODUCTION: bool
    TOPGG_TOKEN: str | None
    GOOGLE_APPLICATION_CREDENTIALS: str | None


class DiscordBot(commands.Bot):
    def __init__(
        self, intents: discord.Intents, config: Config, logger: logging.Logger
    ) -> None:
        super().__init__(
            command_prefix=",",
            intents=intents,
            help_command=None,
        )
        """
        Creates custom bot variables so that we can access these variables in cogs
        more easily.
        """
        self.tree.on_error = self.tree_on_error
        self.config = config
        self.logger = logger
        self.html2image = Html2Image(browser_executable=config.BROWSER_EXECUTABLE_PATH)
        self.channel_logger = ChannelLogger(self, self.config.LOGGING_CHANNEL_ID)
        self.ratings = Ratings(self)
        self.neetcode = NeetcodeSolutions(self)
        self._http_client: HttpClient | None = None
        self._topggpy: topgg.client.DBLClient | None = None

    @property
    def http_client(self) -> HttpClient:
        if self._http_client is None:
            raise RuntimeError("setup_hook() must be called first")
        return self._http_client

    @property
    def topggpy(self) -> topgg.client.DBLClient:
        if self._topggpy is None:
            raise RuntimeError("setup_hook() must be called first")
        return self._topggpy

    async def on_autopost_success(self) -> None:
        """
        Runs when stats are posted to topgg
        """
        self.logger.info(
            f"Posted server count ({self.topggpy.guild_count}), shard count "
            f"({self.shard_count})",
        )

        self.logger.info(f"Total bot member count ({len(set(self.get_all_members()))})")

    async def init_topgg(self) -> None:
        """
        Initialises the topgg client.
        """
        if self.config.PRODUCTION and self.config.TOPGG_TOKEN:
            self._topggpy = topgg.client.DBLClient(
                self, self.config.TOPGG_TOKEN, autopost=True, post_shard_count=True
            )

    async def load_cogs(self) -> None:
        """
        The code in this function is executed whenever the bot will start.
        """
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"src.cogs.{extension}")
                    self.logger.info(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to load extension {extension}\n{exception}"
                    )

    async def on_ready(self) -> None:
        """
        Called when the client is done preparing the data received from Discord.
        """
        self.logger.info("Ready")

    async def setup_hook(self) -> None:
        """
        Called only once to setup the bot.
        """
        self.logger.info(f"Logged in as {self.user.name if self.user else 'Unknown'} ")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")

        self._http_client = HttpClient(self, aiohttp.ClientSession())
        await initialise_mongodb_connection(
            self.config.MONGODB_URI, GLOBAL_LEADERBOARD_ID
        )
        await self.load_cogs()
        await self.init_topgg()

        schedule_update_zerotrac_ratings.start(self)
        schedule_update_neetcode_solutions.start(self)
        schedule_question_and_stats_update.start(self)
        schedule_prune_members_and_guilds.start(self)

    async def on_interaction(self, interaction: discord.Interaction) -> None:
        """
        The code in this event is executed every time a normal command has been
        *successfully* executed.
        """
        if not interaction.command:
            return

        full_command_name = interaction.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if interaction.guild is not None:
            self.logger.info(
                f"Executed /{executed_command} command in {interaction.guild.name} "
                f"(ID: {interaction.guild.id}) by {interaction.user.name} "
                f"(ID: {interaction.user.id})"
            )
        else:
            self.logger.info(
                f"Executed /{executed_command} command by {interaction.user.name} "
                f"(ID: {interaction.user.id}) in DMs"
            )

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """
        Called when a guild gets deleted.
        Delete the server and all it's profiles.
        """
        self.logger.info(
            f"Guild {guild.name} (ID: {guild.id}) discord account removed",
        )
        await Profile.find_many(Profile.server_id == guild.id).delete()
        await Server.find_one(Server.id == guild.id).delete()

    async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent) -> None:
        """
        Called when a member leaves a guild.
        Delete the profile of the user.
        """
        self.logger.info(
            f"Member {payload.user.name} (ID: {payload.user.id}) in Guild "
            f"(ID: {payload.guild_id}) discord account removed",
        )
        await unlink_user_from_server(payload.guild_id, payload.user.id)

        profiles = await Profile.find_many(
            Profile.user_id == payload.user.id,
            Profile.server_id != GLOBAL_LEADERBOARD_ID,
        ).to_list()

        if len(profiles) == 0:
            await delete_user(payload.user.id)

    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        """
        Called when a member updates their guild specific information, such as nickname.
        Update the user profile's preference name to the new nickname.
        """
        if before.display_name == after.display_name:
            return

        await Profile.find_one(
            Profile.user_id == before.id,
            Profile.server_id == before.guild.id,
        ).update(
            Set({Profile.preference.name: after.display_name})
        )  # type: ignore

    async def on_user_update(self, before: discord.User, after: discord.User) -> None:
        """
        Called a user updated their account information, such as username.
        Update the user global profile's preference name to the new username.
        """
        if before.display_name == after.display_name:
            return

        await Profile.find_one(
            Profile.user_id == before.id,
            Profile.server_id == GLOBAL_LEADERBOARD_ID,
        ).update(
            Set({Profile.preference.name: after.display_name})
        )  # type: ignore

    async def on_message(self, message: discord.Message) -> None:
        """
        Called whenever a message is sent. However, due to not having messages intent,
        only messages that mention the bot will give us access to the message's
        contents.
        """
        if not self.user or not (
            (message.author.id == self.config.DEVELOPER_DISCORD_ID)
            and self.user.mentioned_in(message)
        ):
            return

        await dev_commands(self, message)

    async def close(self) -> None:
        """
        Closes the connection to Discord, gracefully closes the session, and reboots
        the device.
        """
        try:
            await self.http_client.session.close()
            await super().close()
        finally:
            if self.config.PRODUCTION:
                os.system("sudo reboot")

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        """
        Event raised errors.

        Currently this causes an outage, and therefore will log the error and restart
        the bot.
        """
        self.logger.critical(
            "Critical error in %s.\nBot is closing/restarting.", event_method
        )
        await self.close()

    @staticmethod
    async def tree_on_error(
        interaction: discord.Interaction, error: discord.app_commands.AppCommandError
    ) -> None:
        """
        The code in this event is executed every time a normal valid command catches an
        error.
        """
        if isinstance(error, discord.app_commands.errors.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            embed = discord.Embed(
                description=f"**Please slow down** - You can use this command again in "
                f"{f'{round(hours)} hours' if round(hours) > 0 else ''}"
                f"{f'{round(minutes)} minutes' if round(minutes) > 0 else ''}"
                f"{f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
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

    def format(self, record) -> str:
        log_colour = self.COLOURS[record.levelno]
        format = (
            "(black){asctime}(reset) (levelcolour){levelname:<8}(reset) "
            "(green){name}(reset) {message}"
        )
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolour)", log_colour)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)
