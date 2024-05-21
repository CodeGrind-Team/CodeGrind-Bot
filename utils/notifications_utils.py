import asyncio
from datetime import UTC, datetime, time

import aiohttp
import discord
from beanie.odm.operators.update.general import Set
from discord.ext import commands, tasks

from constants import Period
from database.models import Server, User
from embeds.questions_embeds import daily_question_embed
from utils.leaderboards_utils import send_leaderboard_winners
from utils.roles_utils import update_roles
from utils.stats_utils import update_stats


async def send_daily_question(
    bot: commands.Bot, server: Server, embed: discord.Embed
) -> None:
    """
    Send the daily question to the server's daily question channels.

    :param server: The server to send the daily question to (with links fetched).
    :param embed: The embed containing the daily question.
    """
    bot.logger.info("file: utils/notifications_utils.py ~ send_daily ~ run")

    for channel_id in server.channels.daily_question:
        channel = bot.get_channel(channel_id)

        if not channel or not isinstance(channel, discord.TextChannel):
            continue

        await channel.send(embed=embed)


@tasks.loop(
    time=[time(hour=hour, minute=minute) for hour in range(24) for minute in [0, 30]]
)
async def send_daily_question_and_update_stats_schedule(bot: commands.Bot) -> None:
    """
    Schedule to send the daily question and update the stats.
    """
    await send_daily_question_and_update_stats(bot)


async def send_daily_question_and_update_stats(
    bot: commands.Bot,
    force_update_stats: bool = True,
    force_daily_reset: bool = False,
    force_weekly_reset: bool = False,
    force_monthly_reset: bool = False,
) -> None:
    """
    Send the daily question and update the stats.

    :param force_update_stats: Whether to force update the stats.
    :param force_daily_reset: Whether to force the daily reset.
    :param force_weekly_reset: Whether to force the weekly reset.
    :param force_monthly_reset: Whether to force the monthly reset.
    """
    bot.logger.info(
        "file: utils/notifications_utils.py ~ send_daily_question_and_update_stats ~ \
            started"
    )

    start = datetime.now(UTC)

    daily_reset = (start.hour == 0 and start.minute == 0) or force_daily_reset
    weekly_reset = (
        start.weekday() == 0 and start.hour == 0 and start.minute == 0
    ) or force_weekly_reset
    monthly_reset = (
        start.day == 1 and start.hour == 0 and start.minute == 0
    ) or force_monthly_reset

    midday = start.hour == 12 and start.minute == 0

    if daily_reset:
        # Send problem of the day.
        embed = await daily_question_embed()
        async for server in Server.all(fetch_links=True):
            await send_daily_question(server, embed)

    if force_update_stats:
        await bot.channel_logger.INFO("Started updating users stats")

        # Update users' stats.
        async with aiohttp.ClientSession() as client_session:
            tasks = []
            async for user in User.all():
                task = asyncio.create_task(coro=update_stats(client_session, user))

                tasks.append(task)

            await asyncio.gather(*tasks)

        await bot.channel_logger.INFO(
            "Completed updating users stats", include_error_counts=True
        )

    await bot.channel_logger.INFO("Started updating server rankings")

    async for server in Server.all(fetch_links=True):
        await Server.find_one(Server.id == server.id).update(
            Set(
                {
                    Server.last_update_start: start,
                    Server.last_update_end: datetime.now(UTC),
                }
            )
        )

        if daily_reset:
            await send_leaderboard_winners(server, Period.DAY)

        if weekly_reset:
            await send_leaderboard_winners(server, Period.WEEK)

        if monthly_reset:
            await send_leaderboard_winners(server, Period.MONTH)

        if midday:
            await update_roles(bot, server)

    await bot.channel_logger.INFO("Completed updating server rankings")

    bot.logger.info(
        "file: utils/notifications_utils.py ~ send_daily_question_and_update_stats ~ \
            ended"
    )
