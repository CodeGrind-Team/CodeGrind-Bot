import aiohttp
import asyncio
from datetime import datetime, time

import discord
from discord.ext import tasks

from bot_globals import client, logger
from database.models.server_model import Server
from database.models.user_model import User
from embeds.questions_embeds import daily_question_embed
from utils.analytics_utils import save_analytics
from utils.leaderboards_utils import (send_leaderboard_winners,
                                      update_global_leaderboard)
from utils.roles_utils import update_roles
from utils.stats_utils import update_rankings, update_stats
from utils.users_utils import remove_inactive_users


async def send_daily_question(server: Server, embed: discord.Embed) -> None:
    logger.info("file: utils/notifications_utils.py ~ send_daily ~ run")

    for channel_id in server.channels.daily_question:
        channel = client.get_channel(channel_id)

        if not channel or not isinstance(channel, discord.TextChannel):
            continue

        try:
            await channel.send(embed=embed)
        except discord.errors.Forbidden as e:
            logger.exception(
                "file: utils/notifications_utils.py ~ send_daily ~ missing permissions on channel id %s. Error: %s", channel.id, e)

        # async for message in channel.history(limit=1):
        #     try:
        #         await message.pin()
        #     except discord.errors.Forbidden as e:
        #         logger.exception(
        #             "file: utils/notifications_utils.py ~ send_daily ~ message not pinned due to missing permissions in channel %s", channel_id)

        logger.info(
            "file: utils/notifications_utils.py ~ send_daily ~ daily question sent to channel %s", channel.id)

    logger.info(
        "file: utils/notifications_utils.py ~ send_daily ~ all daily questions sent to server ID: %s", server.id)


@tasks.loop(time=[time(hour=hour, minute=minute) for hour in range(24) for minute in [0, 30]])
async def send_daily_question_and_update_stats_schedule() -> None:
    await send_daily_question_and_update_stats()


async def send_daily_question_and_update_stats(force_update_stats: bool = True, force_daily_reset: bool = False, force_weekly_reset: bool = False) -> None:
    logger.info(
        "file: utils/notifications_utils.py ~ send_daily_question_and_update_stats ~ started")

    now = datetime.utcnow()

    daily_reset = (now.hour == 0 and now.minute == 0) or force_daily_reset
    weekly_reset = (now.weekday() == 0 and now.hour ==
                    0 and now.minute == 0) or force_weekly_reset
    midday = (now.hour == 12 and now.minute == 0)
    monthly = (now.day == 1 and now.hour ==
               12 and now.minute == 0)

    if force_update_stats:
        await client.channel_logger.INFO("Started updating users stats")
        async with aiohttp.ClientSession() as client_session:
            tasks = []
            async for user in User.all():
                task = asyncio.create_task(coro=update_stats(client_session, user,
                                                             now, daily_reset, weekly_reset))

                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=False)

        await update_global_leaderboard()

        await client.channel_logger.INFO("Completed updating users stats", include_error_counts=True)

    await client.channel_logger.INFO("Started updating server rankings")
    async for server in Server.all(fetch_links=True):
        server.last_updated = now
        await server.save()

        if daily_reset:
            await update_rankings(server, now, "daily")
            await send_leaderboard_winners(server, "yesterday")

        if weekly_reset:
            await update_rankings(server, now, "weekly")
            await send_leaderboard_winners(server, "last_week")

        if midday:
            await update_roles(server)

    await client.channel_logger.INFO("Completed updating server rankings")

    if daily_reset:
        embed = await daily_question_embed()

        async for server in Server.all(fetch_links=True):
            await send_daily_question(server, embed)

        await save_analytics()

    if monthly:
        await client.channel_logger.INFO("Started pruning")
        await remove_inactive_users()
        await client.channel_logger.INFO("Completed pruning")

    logger.info(
        "file: utils/notifications_utils.py ~ send_daily_question_and_update_stats ~ ended")
