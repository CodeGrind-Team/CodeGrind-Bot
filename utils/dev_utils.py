
import asyncio
import os
from enum import Enum
import discord
from dotenv import load_dotenv
from bot_globals import client, logger
from datetime import datetime
from random import random

load_dotenv()

LOGGING_CHANNEL_ID = int(os.environ['LOGGING_CHANNEL_ID'])


class LogType(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3


async def log_to_channel(log_type: LogType, message: str):
    color = None

    match log_type:
        case LogType.INFO:
            color = discord.Color.blue()
        case LogType.WARNING:
            color = discord.Color.orange()
        case LogType.ERROR:
            color = discord.Color.red()
        case _:
            return

    embed = discord.Embed(color=color, description=message)
    embed.set_footer(text=datetime.utcnow().strftime("%H:%M:%S.%f"))

    try:
        channel = client.get_channel(LOGGING_CHANNEL_ID)
        if not channel or not isinstance(channel, discord.TextChannel):
            return

        await asyncio.sleep(random())
        await channel.send(embed=embed)
    except discord.errors.Forbidden as e:
        logger.exception(
            "file: utils/dev_utils.py ~ log_to_channel ~ missing permissions on channel id %s. Error: %s", LOGGING_CHANNEL_ID, e)
