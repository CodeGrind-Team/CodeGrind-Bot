
from typing import List

from bot_globals import client, logger
from cogs.leaderboards import create_leaderboard


async def send_leaderboard_winners(timeframe: str, guild_id: int, specific_channels: List[int] = None):
    channels = []
    if specific_channels is not None:
        channels = specific_channels
    else:
        with open('dailychannels.txt', 'r', encoding="UTF-8") as f:
            channels = [channel.strip() for channel in f.readlines()]

    for channel_id in channels:
        channel = client.get_channel(int(channel_id))
        await create_leaderboard(channel.send, guild_id, timeframe=timeframe, winners_only=True, users_per_page=3)

    logger.info(
        "file: utils/leaderboards.py ~ send_leaderboard_winners ~ %s winners leaderboard sent to channels", timeframe)
