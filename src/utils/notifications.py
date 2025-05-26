from datetime import UTC, datetime
from typing import TYPE_CHECKING

import discord
from beanie.odm.operators.update.general import Set

from src.constants import GLOBAL_LEADERBOARD_ID, Period
from src.database.models import Server
from src.ui.embeds.problems import daily_question_embed
from src.utils.leaderboards import send_leaderboard_winners
from src.utils.roles import update_roles
from src.utils.stats import update_all_user_stats

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot


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
    bot.logger.info("Sending daily notifications and updating stats started")
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
        embed = await daily_question_embed(bot)

        try:
            async for server in Server.all(fetch_links=True):
                await send_daily_question(bot, server, embed)
        except discord.errors.HTTPException:
            bot.logger.exception(
                "HTTPException raised when trying to share daily questions to channels:"
                " embed length over limit."
            )

        bot.logger.info("Daily question sent to all servers")

    if update_stats:
        await update_all_user_stats(bot, reset_day, reset_week, reset_month)

    async for server in Server.all():
        await Server.find_one(Server.id == server.id).update(
            Set(
                {
                    Server.last_update_start: start,
                    Server.last_update_end: datetime.now(UTC),
                }
            )
        )  # type: ignore

        if server.id == GLOBAL_LEADERBOARD_ID:
            continue

        if reset_day:
            await send_leaderboard_winners(bot, server, Period.DAY)

        if reset_week:
            await send_leaderboard_winners(bot, server, Period.WEEK)

        if reset_month:
            await send_leaderboard_winners(bot, server, Period.MONTH)

        if midday:
            if guild := bot.get_guild(server.id):
                try:
                    await update_roles(guild, server.id)
                except discord.errors.Forbidden:
                    # Missing permissions are handled inside update_roles, so it
                    # shouldn't raise an error.
                    bot.logger.info(
                        f"Forbidden to add roles to members of server with ID: "
                        f"{server.id}"
                    )

    bot.logger.info("Sending daily notifications and updating stats completed")
    await bot.channel_logger.info("Completed updating", include_error_counts=True)


async def send_daily_question(
    bot: "DiscordBot", server: Server, embed: discord.Embed
) -> None:
    """
    Send the daily question to the server's daily question channels.

    :param server: The server to send the daily question to (with links fetched).
    :param embed: The embed containing the daily question.
    """
    for channel_id in server.channels.daily_question:
        channel = bot.get_channel(channel_id)

        if not channel or not isinstance(channel, discord.TextChannel):
            continue

        try:
            message = await channel.send(embed=embed, silent=True)

            await channel.create_thread(
                name=embed.title if embed.title else "Daily Question",
                message=message,
                auto_archive_duration=1440,  # in minutes (1 day).
            )

        except discord.errors.Forbidden:
            bot.logger.info(
                f"Forbidden to share daily question to channel with ID: {channel_id}"
            )
