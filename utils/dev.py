import asyncio
from datetime import UTC, datetime
from random import random
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


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
        if include_error_counts:
            message += f". Rate limited {self.rate_limits} times"
            self.rate_limits = 0

        await self.log(message, discord.Colour.blue())

        if include_error_counts and self.forbidden_count > 0:
            await self.warning(f"Forbidden {self.forbidden_count} times.")
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
        embed = discord.Embed(colour=colour, description=message)
        embed.set_footer(text=datetime.now(UTC).strftime("%H:%M:%S.%f"))

        try:
            # Get the designated logging channel
            channel = self.bot.get_channel(self.channel_id)
            if not channel or not isinstance(channel, discord.TextChannel):
                return

            # Add a small delay to avoid rate limits, using random to avoid patterns
            await asyncio.sleep(random())
            await channel.send(embed=embed, silent=silent)

        except discord.errors.Forbidden as e:
            self.bot.logger.exception(
                "file: utils/dev.py ~ ChannelLogger.log ~ \
                    missing permissions on logging channel. Error: %s",
                e,
            )
        except Exception as e:
            self.bot.logger.exception(
                "file: utils/dev.py ~ ChannelLogger.log ~ Error: %s", e
            )
