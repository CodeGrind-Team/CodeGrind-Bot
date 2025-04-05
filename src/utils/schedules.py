from datetime import time
from functools import wraps
from typing import TYPE_CHECKING, Callable

from discord.ext import tasks

from src.utils.dev import prune_members_and_guilds
from src.utils.notifications import process_daily_question_and_stats_update

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot


def task_exception_handler(func: Callable) -> Callable:
    """
    Decorator to gracefully catch exceptions in a discord.ext.tasks.loop function and
    allow it to continue running.

    This allows the task to continue running on it's next scheduled iteration.
    """

    @wraps(func)
    async def wrapper(bot: "DiscordBot", *args, **kwargs):
        try:
            await func(bot, *args, **kwargs)
        except Exception as e:
            bot.logger.critical(f"Task '{func.__name__}' encountered an error: {e}")

    return wrapper


@tasks.loop(
    time=[time(hour=hour, minute=minute) for hour in range(24) for minute in [0, 30]],
    reconnect=False,
)
@task_exception_handler
async def schedule_question_and_stats_update(bot: "DiscordBot") -> None:
    """
    Schedule to send the daily question and update the stats.
    """
    await process_daily_question_and_stats_update(bot)


@tasks.loop(hours=168, reconnect=False)
@task_exception_handler
async def schedule_prune_members_and_guilds(bot: "DiscordBot") -> None:
    """
    Prune servers that don't have the bot in them, profiles of users that are not in
    the corresponding guild anymore, and users that don't have any profiles.

    168 hours == 1 week
    """

    # Skip the first loop as it is called immediately after starting the bot
    if schedule_prune_members_and_guilds.current_loop == 0:
        return

    await prune_members_and_guilds(bot)


@tasks.loop(hours=168)
@task_exception_handler
async def schedule_update_zerotrac_ratings(bot: "DiscordBot") -> None:
    """
    Update zerotrac ratings weekly.

    168 hours == 1 week.
    """
    await bot.ratings.update_ratings()


@tasks.loop(hours=24)
@task_exception_handler
async def schedule_update_neetcode_solutions(bot: "DiscordBot") -> None:
    """
    Update NeetCode solutions data daily.
    """
    await bot.neetcode.update_solutions()
