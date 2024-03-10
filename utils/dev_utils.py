
import asyncio
import discord
from bot_globals import client, logger
from datetime import datetime
from random import random


class ChannelLogger:
    def __init__(self, channel_id: int) -> None:
        self.rate_limits = 0
        self.forbidden_count = 0
        self.channel_id = channel_id

    def rate_limited(self) -> None:
        self.rate_limits += 1

    def forbidden(self) -> None:
        self.forbidden_count += 1

    async def INFO(self, message: str, include_error_counts: bool = False) -> None:
        if include_error_counts:
            message += f". Rate limited {self.rate_limits} times"
            self.rate_limits = 0

        await self.log(message, discord.Color.blue())

        if include_error_counts:
            await self.WARNING(f"Forbidden {self.forbidden_count} times.")
            self.forbidden_count = 0

    async def WARNING(self, message: str) -> None:
        await self.log(message, discord.Color.orange())

    async def ERROR(self, message: str) -> None:
        await self.log(message, discord.Color.red())

    async def log(self, message: str, color: discord.Color) -> None:
        embed = discord.Embed(color=color, description=message)
        embed.set_footer(text=datetime.utcnow().strftime("%H:%M:%S.%f"))

        try:
            channel = client.get_channel(self.channel_id)
            if not channel or not isinstance(channel, discord.TextChannel):
                return

            await asyncio.sleep(random())
            await channel.send(embed=embed)
        except discord.errors.Forbidden as e:
            logger.exception(
                "file: utils/dev_utils.py ~ ChannelLogger.log ~ missing permissions on logging channel. Error: %s", e)
        except Exception as e:
            logger.exception(
                "file: utils/dev_utils.py ~ ChannelLogger.log ~ Error: %s", e)
