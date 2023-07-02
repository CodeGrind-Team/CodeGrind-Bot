import asyncio
import os
from datetime import datetime, timedelta

import discord

from bot_globals import client, logger
from embeds.questions_embeds import daily_question_embed
from models.server_model import Server
from utils.io_handling import read_file
from utils.leaderboards import send_leaderboard_winners
from utils.stats import update_stats_and_rankings


async def wait_until_next_half_hour() -> None:
    now_utc = datetime.utcnow()

    if now_utc.minute < 30:
        next_half_hour = now_utc.replace(minute=30, second=0, microsecond=0)
    else:
        next_half_hour = (now_utc + timedelta(hours=1)).replace(minute=0,
                                                                second=0, microsecond=0)

    logger.info(
        "file: utils/message_scheduler.py ~ wait_until_next_half_hour ~ next_half_hour: %s", next_half_hour)

    seconds_to_wait = (next_half_hour - now_utc).total_seconds()
    await asyncio.sleep(seconds_to_wait)


async def send_daily_question(server: Server) -> None:
    logger.info("file: utils/message_scheduler.py ~ send_daily ~ run")
    embed = daily_question_embed()

    for channel in server.channels:
        channel = client.get_channel(channel.id)

        if not isinstance(channel, discord.TextChannel):
            continue

        await channel.send(embed=embed)

        # async for message in channel.history(limit=1):
        #     try:
        #         await message.pin()
        #     except discord.errors.Forbidden:
        #         logger.exception(
        #             "file: utils/message_scheduler.py ~ send_daily ~ message not pinned due to missing permissions in channel %s", channel_id)

        logger.info(
            "file: utils/message_scheduler.py ~ send_daily ~ daily question sent to channel %s", channel.id)

    logger.info(
        "file: utils/message_scheduler.py ~ send_daily ~ all daily questions sent to server ID: %s", server.id)


async def send_daily_question_and_update_stats() -> None:
    logger.info(
        "file: utils/message_scheduler.py ~ send_daily_question_and_update_stats ~ run")

    while not client.is_closed():
        await wait_until_next_half_hour()

        now_utc = datetime.utcnow()
        daily_question_reset = now_utc.hour == 0 and now_utc.minute == 0

        async for server in Server.all():
            # daily changes at midnight UTC
            now_timezone = datetime.now(server.timezone)
            daily_reset = now_timezone.hour == 0 and now_timezone.minute == 0
            weekly_reset = now_timezone.weekday(
            ) == 0 and now_timezone.hour == 0 and now_timezone.minute == 0

            await update_stats_and_rankings(server, now_utc, daily_reset, weekly_reset)

            if daily_reset:
                await send_leaderboard_winners(server, "yesterday")

            if weekly_reset:
                await send_leaderboard_winners(server, "last_week")

            if daily_question_reset:
                await send_daily_question(server)
