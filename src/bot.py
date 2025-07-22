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
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, DefaultDict

import aiohttp
import discord
import topgg
from beanie.odm.operators.update.general import Set
from datadog.dogstatsd.base import DogStatsd, statsd
from discord.ext import commands
from playwright.async_api import Browser, Playwright, async_playwright

from src.constants import GLOBAL_LEADERBOARD_ID, ProblemList
from src.database.models import Profile, Server
from src.database.setup import initialise_mongodb_connection
from src.utils.channel_logging import DiscordChannelLogger
from src.utils.dev import dev_commands
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
    LOGGING_CHANNEL_ID: int
    DEVELOPER_DISCORD_ID: int
    PRODUCTION: bool
    TOPGG_TOKEN: str | None
    GOOGLE_APPLICATION_CREDENTIALS: str | None
    DD_API_KEY: str | None
    DD_APP_KEY: str | None


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
        self.channel_logger = DiscordChannelLogger(self, self.config.LOGGING_CHANNEL_ID)
        self.ratings = Ratings(self)
        self.neetcode = NeetcodeSolutions(self)
        # {problem_list: {problem_id,}}
        self.problem_lists: DefaultDict[ProblemList, set[str]] = defaultdict(set)

        self._http_client: HttpClient | None = None
        self._topggpy: topgg.client.DBLClient | None = None
        self._browser: Browser | None = None
        self._playwright: Playwright | None = None

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

    @property
    def playwright(self) -> Playwright:
        if self._playwright is None:
            raise RuntimeError("setup_hook() must be called first")
        return self._playwright

    @property
    def browser(self) -> Browser:
        if self._browser is None:
            raise RuntimeError("setup_hook() must be called first")
        return self._browser

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

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True, chromium_sandbox=False
        )

        await self.load_cogs()
        await self.init_topgg()

        schedule_update_zerotrac_ratings.start(self)
        schedule_update_neetcode_solutions.start(self)
        schedule_question_and_stats_update.start(self)
        schedule_prune_members_and_guilds.start(self)

    async def on_ready(self) -> None:
        """
        Called when the client is done preparing the data received from Discord.
        """
        self.logger.info("Bot is ready.")
        statsd.service_check(
            "discord.bot.status",
            DogStatsd.OK,
            tags=["bot:" + self.user.name if self.user else "Unknown"],
        )

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

        statsd.increment(
            "discord.commands.count",
            tags=["command:" + executed_command],
        )
        statsd.timing(
            "discord.commands.duration",
            (datetime.now(UTC) - interaction.created_at).total_seconds(),
            tags=["command:" + executed_command],
        )

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """
        Called when a guild gets deleted.
        Delete the server and all it's profiles.
        """
        await Profile.find_many(Profile.server_id == guild.id).delete()
        await Server.find_one(Server.id == guild.id).delete()

        self.logger.info(
            f"Guild {guild.name} (ID: {guild.id}) discord account removed",
        )
        statsd.increment("discord.guilds.removed")

    async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent) -> None:
        """
        Called when a member leaves a guild.
        Delete the profile of the user.
        """
        await unlink_user_from_server(payload.guild_id, payload.user.id)

        db_profiles = await Profile.find_many(
            Profile.user_id == payload.user.id,
            Profile.server_id != GLOBAL_LEADERBOARD_ID,
        ).to_list()

        if len(db_profiles) == 0:
            await delete_user(payload.user.id)

        self.logger.info(
            f"Member {payload.user.name} (ID: {payload.user.id}) in Guild "
            f"(ID: {payload.guild_id}) discord account removed",
        )
        statsd.increment("discord.guilds.members.removed")

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

        statsd.increment("discord.guilds.members.updated")

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

        statsd.increment("discord.users.updated")

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

    async def on_disconnect(self) -> None:
        """
        Called when the client has disconnected from Discord, or a connection attempt
        to Discord has failed. This could happen either through the internet being
        disconnected, explicit calls to close, or Discord terminating the connection
        one way or the other.
        """
        statsd.service_check(
            "discord.bot.status",
            DogStatsd.WARNING,
            tags=["bot:" + self.user.name if self.user else "Unknown"],
        )

    async def close(self) -> None:
        """
        Closes the connection to Discord, gracefully closes the session, and reboots
        the device.
        """
        self.logger.fatal(
            "Closing bot." "\nTriggering container restart."
            if self.config.PRODUCTION
            else ""
        )
        statsd.service_check(
            "discord.bot.status",
            DogStatsd.CRITICAL,
            tags=["bot:" + self.user.name if self.user else "Unknown"],
        )

        try:
            await self.http_client.session.close()
            await self.browser.close()
            await self.playwright.stop()
            await super().close()
        finally:
            if self.config.PRODUCTION:
                sys.exit(1)

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        """
        Event raised errors.

        Currently this causes an outage, and therefore will log the error and restart
        the bot.
        """
        self.logger.critical("Critical error in %s.", event_method)
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
            statsd.increment("discord.commands.error", tags=["error:cooldown"])

        elif isinstance(error, discord.app_commands.errors.MissingPermissions):
            embed = discord.Embed(
                description="You are missing the permission(s) `"
                + ", ".join(error.missing_permissions)
                + "` to execute this command!",
                colour=0xE02B2B,
            )
            await interaction.response.send_message(embed=embed)
            statsd.increment(
                "discord.commands.error", tags=["error:member_permissions"]
            )

        elif isinstance(error, discord.app_commands.errors.BotMissingPermissions):
            embed = discord.Embed(
                description="I am missing the permission(s) `"
                + ", ".join(error.missing_permissions)
                + "` to fully perform this command!",
                colour=0xE02B2B,
            )
            await interaction.response.send_message(embed=embed)
            statsd.increment("discord.commands.error", tags=["error:bot_permissions"])

        else:
            raise error
