import asyncio
from datetime import datetime, timedelta

import discord

from bot_globals import client, logger
from embeds.questions_embeds import daily_question_embed
from models.server_model import Server, User
from utils.leaderboards import send_leaderboard_winners
from utils.stats import update_rankings, update_stats


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


async def send_daily_question(server: Server, embed: discord.Embed) -> None:
    logger.info("file: utils/message_scheduler.py ~ send_daily ~ run")

    for channel_id in server.channels.daily_question:
        channel = client.get_channel(channel_id)

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


async def send_daily_question_and_update_stats(force_update: bool = False, force_daily_reset: bool = False, force_weekly_reset: bool = False) -> None:
    logger.info(
        "file: utils/message_scheduler.py ~ send_daily_question_and_update_stats ~ run")

    while not client.is_closed():
        if not force_update:
            await wait_until_next_half_hour()
        else:
            force_update = False

        now = datetime.utcnow()
        # for debugging purposes
        daily_reset = (now.hour == 0 and now.minute == 0) or force_daily_reset
        weekly_reset = (now.weekday() == 0 and now.hour ==
                        0 and now.minute == 0) or force_weekly_reset
        force_update = False

        async for user in User.all():
            await update_stats(user, now, daily_reset, weekly_reset)

        async for server in Server.all(fetch_links=True):
            server.last_updated = now
            await server.save_changes()

            if daily_reset:
                await update_rankings(server, now, "daily")
                await send_leaderboard_winners(server, "yesterday")

            if weekly_reset:
                await update_rankings(server, now, "weekly")
                await send_leaderboard_winners(server, "last_week")

        if daily_reset:
            embed = daily_question_embed()

            async for server in Server.all(fetch_links=True):
                await send_daily_question(server, embed)
