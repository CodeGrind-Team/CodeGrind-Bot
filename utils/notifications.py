import asyncio
from datetime import UTC, datetime, time
from typing import TYPE_CHECKING

import aiohttp
import discord
from beanie.odm.operators.update.general import Set
from discord.ext import tasks

from constants import Period
from database.models import Server, User
from ui.embeds.problems import daily_question_embed
from utils.leaderboards import send_leaderboard_winners
from utils.roles import update_roles
from utils.stats import update_stats

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


@tasks.loop(
    time=[time(hour=hour, minute=minute) for hour in range(24) for minute in [0, 30]]
)
async def schedule_question_and_stats_update(bot: "DiscordBot") -> None:
    """
    Schedule to send the daily question and update the stats.
    """
    await process_daily_question_and_stats_update(bot)


async def process_daily_question_and_stats_update(
    bot: "DiscordBot",
    update_stats: bool = True,
    force_reset_day: bool = False,
    force_reset_week: bool = False,
    force_reset_month: bool = False,
) -> None:
    """
    Send the daily question and update the stats.

    :param update_stats: Whether to update the users stats.
    :param force_reset_day: Whether to force the daily reset.
    :param force_reset_week: Whether to force the weekly reset.
    :param force_reset_month: Whether to force the monthly reset.
    """
    bot.logger.info(
        "file: utils/notifications.py ~ send_daily_question_and_update_stats ~ \
            started"
    )
    await bot.channel_logger.info("Started updating")

    start = datetime.now(UTC)

    reset_day = (start.hour == 0 and start.minute == 0) or force_reset_day
    reset_week = (
        start.weekday() == 0 and start.hour == 0 and start.minute == 0
    ) or force_reset_week
    reset_month = (
        start.day == 1 and start.hour == 0 and start.minute == 0
    ) or force_reset_month

    midday = start.hour == 12 and start.minute == 0

    if reset_day:
        # Send problem of the day.
        async with aiohttp.ClientSession() as client_session:
            embed = await daily_question_embed(bot, client_session)

        async for server in Server.all(fetch_links=True):
            await send_daily_question(bot, server, embed)

    if update_stats:
        await update_all_user_stats(bot, reset_day)

    async for server in Server.all(fetch_links=True):
        await Server.find_one(Server.id == server.id).update(
            Set(
                {
                    Server.last_update_start: start,
                    Server.last_update_end: datetime.now(UTC),
                }
            )
        )

        if reset_day:
            await send_leaderboard_winners(bot, server, Period.DAY)

        if reset_week:
            await send_leaderboard_winners(bot, server, Period.WEEK)

        if reset_month:
            await send_leaderboard_winners(bot, server, Period.MONTH)

        if midday:
            guild = bot.get_guild(server.id)
            await update_roles(guild, server.id)

    bot.logger.info(
        "file: utils/notifications.py ~ send_daily_question_and_update_stats ~ \
            ended"
    )
    await bot.channel_logger.info("Completed updating")


async def send_daily_question(
    bot: "DiscordBot", server: Server, embed: discord.Embed
) -> None:
    """
    Send the daily question to the server's daily question channels.

    :param server: The server to send the daily question to (with links fetched).
    :param embed: The embed containing the daily question.
    """
    bot.logger.info("file: utils/notifications.py ~ send_daily ~ run")

    for channel_id in server.channels.daily_question:
        channel = bot.get_channel(channel_id)

        if not channel or not isinstance(channel, discord.TextChannel):
            continue

        await channel.send(embed=embed, silent=True)


async def update_all_user_stats(bot: "DiscordBot", reset_day: int = False) -> None:
    """
    Update stats for all users.
    """
    async with aiohttp.ClientSession() as client_session:
        tasks = []
        async for user in User.all():
            task = asyncio.create_task(
                update_stats(bot, client_session, user, reset_day)
            )
            tasks.append(task)
        await asyncio.gather(*tasks)
