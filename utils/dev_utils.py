import asyncio
import discord
from datetime import datetime, UTC
from random import random


class ChannelLogger:
    def __init__(self, client: discord.Bot, channel_id: int) -> None:
        self.client = client
        self.rate_limits = 0
        self.forbidden_count = 0
        self.channel_id = channel_id

    def rate_limited(self) -> None:
        self.rate_limits += 1

    def forbidden(self) -> None:
        self.forbidden_count += 1

    async def info(self, message: str, include_error_counts: bool = False) -> None:
        if include_error_counts:
            message += f". Rate limited {self.rate_limits} times"
            self.rate_limits = 0

        await self.log(message, discord.Color.blue())

        if include_error_counts:
            await self.WARNING(f"Forbidden {self.forbidden_count} times.")
            self.forbidden_count = 0

    async def warning(self, message: str) -> None:
        await self.log(message, discord.Color.orange())

    async def error(
        self,
        message: str,
    ) -> None:
        await self.log(message, discord.Color.red(), True)

    async def exception(self, message: str) -> None:
        await self.log(message, discord.Color.red(), True)

    async def log(self, message: str, color: discord.Color, silent: bool) -> None:
        embed = discord.Embed(color=color, description=message)
        embed.set_footer(text=datetime.now(UTC).strftime("%H:%M:%S.%f"))

        try:
            channel = client.get_channel(self.channel_id)
            if not channel or not isinstance(channel, discord.TextChannel):
                return

            await asyncio.sleep(random())
            await channel.send(embed=embed, silent=silent)

        except discord.errors.Forbidden as e:
            client.logger.exception(
                "file: utils/dev_utils.py ~ ChannelLogger.log ~ \
                    missing permissions on logging channel. Error: %s",
                e,
            )
        except Exception as e:
            client.logger.exception(
                "file: utils/dev_utils.py ~ ChannelLogger.log ~ Error: %s", e
            )
