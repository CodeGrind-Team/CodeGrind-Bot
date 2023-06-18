import asyncio
import os
from datetime import datetime, timedelta

import discord

from bot_globals import TIMEZONE, client, logger
from utils.io_handling import read_file
from utils.leaderboards import send_leaderboard_winners
from utils.questions import daily_question_embed
from utils.stats import update_stats_and_rankings


async def wait_until_next_half_hour() -> None:
    now = datetime.now(TIMEZONE)

    if now.minute < 30:
        next_half_hour = now.replace(minute=30, second=0, microsecond=30)
    else:
        next_half_hour = (now + timedelta(hours=1)).replace(minute=0,
                                                            second=0, microsecond=30)

    logger.info(
        "file: utils/message_scheduler.py ~ wait_until_next_half_hour ~ next_half_hour: %s", next_half_hour)

    seconds_to_wait = (next_half_hour - now).total_seconds()
    await asyncio.sleep(seconds_to_wait)


async def send_daily_question() -> None:
    logger.info("file: utils/message_scheduler.py ~ send_daily ~ run")
    embed = daily_question_embed()

    for filename in os.listdir("./data"):
        if filename.endswith(".json"):
            server_id = int(filename.split("_")[0])

            data = await read_file(f"data/{server_id}_leetcode_stats.json")

            if "channels" in data:
                for channel_id in data["channels"]:
                    channel = client.get_channel(channel_id)

                    if not isinstance(channel, discord.TextChannel):
                        continue

                    await channel.send(embed=embed)

                    async for message in channel.history(limit=1):
                        try:
                            await message.pin()
                        except discord.errors.Forbidden:
                            logger.exception(
                                "file: utils/message_scheduler.py ~ send_daily ~ message not pinned due to missing permissions in channel %s", channel_id)

                    logger.info(
                        "file: utils/message_scheduler.py ~ send_daily ~ daily question retrieved and pinned in channel %s", channel_id)

    logger.info(
        "file: utils/message_scheduler.py ~ send_daily ~ all daily questions sent and pinned")


async def send_daily_question_and_update_stats() -> None:
    logger.info(
        "file: utils/message_scheduler.py ~ send_daily_question_and_update_stats ~ run")

    lock = asyncio.Lock()

    while not client.is_closed():
        await wait_until_next_half_hour()

        now = datetime.now(TIMEZONE)
        # daily changes at midnight UTC rather than BST
        daily_question_reset = datetime.utcnow().hour == 0 and datetime.utcnow().minute == 0
        daily_reset = now.hour == 0 and now.minute == 0
        weekly_reset = now.weekday() == 0 and now.hour == 0 and now.minute == 0

        async with lock:
            await update_stats_and_rankings(client, now, daily_reset, weekly_reset)

        async with lock:
            if daily_question_reset:
                await send_daily_question()

            if daily_reset:
                await send_leaderboard_winners("yesterday")

            if weekly_reset:
                await send_leaderboard_winners("last_week")
