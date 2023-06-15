import os

from bot_globals import client, logger
from cogs.leaderboards import display_leaderboard
from utils.io_handling import read_file


async def send_leaderboard_winners(timeframe: str):
    for filename in os.listdir("./data"):
        if filename.endswith(".json"):
            server_id = int(filename.split("_")[0])

            data = await read_file(f"data/{server_id}_leetcode_stats.json")

            if "channels" in data:
                for channel_id in data["channels"]:
                    channel = client.get_channel(channel_id)
                    await display_leaderboard(channel.send, server_id, timeframe=timeframe, winners_only=True, users_per_page=3)

    logger.info(
        "file: utils/leaderboards.py ~ send_leaderboard_winners ~ %s winners leaderboard sent to channels", timeframe)
