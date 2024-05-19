import asyncio
from datetime import UTC, datetime, time

import aiohttp
import discord
from discord.ext import commands, tasks

from database.models.server_model import Server
from database.models.user_model import User
from embeds.questions_embeds import daily_question_embed
from utils.leaderboards_utils import send_leaderboard_winners, update_global_leaderboard
from utils.roles_utils import update_roles
from utils.stats_utils import update_stats


async def send_daily_question(
    bot: commands.Bot, server: Server, embed: discord.Embed
) -> None:
    """
    Send the daily question to the server's daily question channels.

    :param bot: The Discord bot.
    :param server: The server to send the daily question to.
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

    :param bot: The Discord bot.
    :param force_update_stats: Whether to force update the stats.
    :param force_daily_reset: Whether to force the daily reset.
    :param force_weekly_reset: Whether to force the weekly reset.
    """
    bot.logger.info(
        "file: utils/notifications_utils.py ~ send_daily_question_and_update_stats ~ \
            started"
    )

    now = datetime.now(UTC)

    daily_reset = (now.hour == 0 and now.minute == 0) or force_daily_reset
    weekly_reset = (
        now.weekday() == 0 and now.hour == 0 and now.minute == 0
    ) or force_weekly_reset
    monthly = (
        now.day == 1 and now.hour == 0 and now.minute == 0
    ) or force_monthly_reset

    midday = now.hour == 12 and now.minute == 0

    if daily_reset:
        embed = await daily_question_embed()

        async for server in Server.all(fetch_links=True):
            await send_daily_question(server, embed)

    if force_update_stats:
        await bot.channel_logger.INFO("Started updating users stats")
        async with aiohttp.ClientSession() as client_session:
            tasks = []
            async for user in User.all():
                task = asyncio.create_task(
                    coro=update_stats(
                        client_session, user, now, daily_reset, weekly_reset
                    )
                )

                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=False)

        await update_global_leaderboard()

        await bot.channel_logger.INFO(
            "Completed updating users stats", include_error_counts=True
        )

    await bot.channel_logger.INFO("Started updating server rankings")
    async for server in Server.all(fetch_links=True):
        server.last_updated = now
        await server.save()

        if daily_reset:
            await send_leaderboard_winners(server, "yesterday")

        if weekly_reset:
            await send_leaderboard_winners(server, "last_week")

        if midday:
            await update_roles(bot, server)

    await bot.channel_logger.INFO("Completed updating server rankings")

    if monthly:
        await bot.channel_logger.INFO("Started pruning")
        await remove_inactive_users()
        await bot.channel_logger.INFO("Completed pruning")

    bot.logger.info(
        "file: utils/notifications_utils.py ~ send_daily_question_and_update_stats ~ \
            ended"
    )
