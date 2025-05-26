import asyncio
from datetime import UTC, datetime
from random import random
from typing import TYPE_CHECKING

import discord

from src.constants import GLOBAL_LEADERBOARD_ID
from src.database.models import Profile, Server, User
from src.utils.notifications import process_daily_question_and_stats_update
from src.utils.users import delete_user

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot


class ChannelLogger:
    """
    A logging utility class for sending messages to a specific Discord channel.

    This class is designed to log informational, warning, error, and exception messages
    to a specified Discord channel, with functionality to track rate limits and
    forbidden (permission-related) issues.

    :param bot: The Discord bot instance.
    :param channel_id: The ID of the Discord channel to log messages to.
    """

    def __init__(self, bot: "DiscordBot", channel_id: int) -> None:
        self.bot = bot
        self.rate_limits = 0
        self.forbidden_count = 0
        self.channel_id = channel_id

    def rate_limited(self) -> None:
        """
        Increment the rate limit counter.
        """
        self.rate_limits += 1
        if self.rate_limits % 100 == 0:
            self.bot.logger.info(f"{self.rate_limits} rate limited requests")

    def forbidden(self) -> None:
        """
        Increment the forbidden counter.
        """
        self.forbidden_count += 1

    async def info(self, message: str, include_error_counts: bool = False) -> None:
        """
        Log an informational message to the designated Discord channel.

        This method sends an informational message to the logging channel. If
        `include_error_counts` is `True`, it appends the rate limit count and
        sends a warning message with the forbidden count.

        :param message: The informational message to log.
        :param include_error_counts: If `True`, includes rate limit and forbidden
        counts in the log.
        """
        if include_error_counts and self.rate_limits > 0:
            message += f"\nRate limited **{self.rate_limits}** times"
            self.rate_limits = 0

        await self.log(message, discord.Colour.blue())

        if include_error_counts and self.forbidden_count > 0:
            await self.warning(f"Forbidden **{self.forbidden_count}** times")
            self.forbidden_count = 0

    async def warning(self, message: str) -> None:
        """
        Log a warning message to the designated Discord channel.
        This method sends a warning message with an orange color to indicate potential
        issues.

        :param message: The warning message to log.
        """
        await self.log(message, discord.Colour.orange(), silent=False)

    async def error(
        self,
        message: str,
    ) -> None:
        """
        Log an error message to the designated Discord channel.
        This method sends an error message with a red color to indicate a critical
        issue.

        :param message: The error message to log.
        """
        await self.log(message, discord.Colour.red(), silent=False)

    async def exception(self, message: str) -> None:
        """
        Log an exception message to the designated Discord channel.
        This method sends an exception message with a red color, similar to
        `error`, indicating a significant error.

        :param message: The exception message to log.
        """
        await self.log(message, discord.Colour.red())

    async def log(
        self, message: str, colour: discord.Colour, silent: bool = True
    ) -> None:
        """
        Log a message to the designated Discord channel with a specified color.

        This is a helper method used by other methods to send an embed message to the
        logging channel. It handles the creation and sending of the embed, with error
        handling for forbidden access and other exceptions.

        :param message: The message to log.
        :param colour: The color of the embed (e.g., blue for info, orange for warning).
        :param silent: If `True`, the embed is sent silently (without user
        notifications).
        """
        embed = discord.Embed(colour=colour)
        embed.description = message + f"\n<t:{int(datetime.now(UTC).timestamp())}:T>"

        try:
            # Get the designated logging channel
            channel = self.bot.get_channel(self.channel_id)
            if not channel or not isinstance(channel, discord.TextChannel):
                return

            # Add a small delay to avoid rate limits, using random to avoid patterns
            await asyncio.sleep(random())
            await channel.send(embed=embed, silent=silent)

        except discord.errors.Forbidden:
            self.bot.logger.exception(
                "ChannelLogger.log: missing permissions on logging channel.",
            )
        except Exception as e:
            self.bot.logger.exception(f"ChannelLogger.log : Error: {e}")


async def share_announcement(bot: "DiscordBot", message: discord.Message) -> None:
    message_content = message.content.lower()

    announcement = message.content[
        message_content.find("share announcement\n") + len("share announcement\n") :
    ]
    bot.logger.info(f"on_message: share announcement: {announcement}")

    image_url: str | None = None
    if len(message.attachments) == 1:
        image_url = message.attachments[0].url

    async for server in Server.all():
        for channel_id in server.channels.maintenance:
            channel = bot.get_channel(channel_id)
            if channel and isinstance(channel, discord.TextChannel):
                try:
                    if image_url:
                        await channel.send(
                            content=announcement + f"\n{image_url}",
                        )
                    else:
                        await channel.send(content=announcement)

                except discord.errors.Forbidden:
                    bot.logger.info(
                        f"Forbidden to share announcement to channel with ID: "
                        f"{channel_id}"
                    )


async def prune_members_and_guilds(bot: "DiscordBot") -> None:
    """
    Refresh members in the database by deleting profiles, users, and servers that no
    longer exist.
    """
    server_index = 0
    async for server in Server.all():
        server_index += 1
        if server_index % 100 == 0:
            bot.logger.info(f"Refreshing members: {server_index} servers checked")

        if server.id == 0:
            continue

        # Delete servers that no longer have the bot in them.
        try:
            guild = await bot.fetch_guild(server.id)
        except discord.errors.NotFound:
            await server.delete()
            bot.logger.info(f"Deleted server with ID: {server.id}")
            continue

        # Delete profiles that no longer have the corresponding member in the server.
        async for profile in Profile.find_many(Profile.server_id == server.id):
            try:
                await guild.fetch_member(profile.user_id)
            except discord.errors.NotFound:
                await profile.delete()
                bot.logger.info(
                    f"Deleted profile with user ID: {profile.user_id} and "
                    f"server ID: {server.id}"
                )

    # Delete users that no longer have any profiles.
    async for user in User.all():
        profiles = await Profile.find_many(
            Profile.user_id == user.id,
            Profile.server_id != GLOBAL_LEADERBOARD_ID,
        ).to_list()

        if len(profiles) == 0:
            await delete_user(user.id)
            bot.logger.info(f"Deleted user with user ID: {user.id}")


async def dev_commands(bot: "DiscordBot", message: discord.Message) -> None:
    """
    Handle developer commands sent by a developer.

    :param message: The message sent by the user.
    """
    message_content = message.content.lower()

    if "share announcement\n" in message_content:
        await share_announcement(bot, message)

    elif "restart" in message_content:
        bot.logger.info("on_message: restart")
        await bot.close()

    elif "maintenance" in message_content:
        if "on" in message_content:
            bot.logger.info("on_message: maintenance on")
            await bot.change_presence(
                status=discord.Status.do_not_disturb,
                activity=discord.Game(name="Under Maintenance"),
            )

        elif "off" in message_content:
            bot.logger.info("on_message: maintenance off")
            await bot.change_presence(
                status=discord.Status.online,
                activity=None,
            )

    elif "sync" in message_content:
        bot.logger.info("on_message: sync")
        await bot.tree.sync()

    elif "update stats" in message_content:
        bot.logger.info("on_message: update stats")
        await process_daily_question_and_stats_update(bot)

    elif "reset stats" in message_content:
        bot.logger.info("on_message: reset stats")
        await process_daily_question_and_stats_update(
            bot,
            not ("no-update" in message_content),
            "day" in message_content,
            "week" in message_content,
            "month" in message_content,
        )

    elif "prune members" in message_content:
        bot.logger.info("on_message: prune members")
        await prune_members_and_guilds(bot)

    bot.logger.info("on_message completed")
