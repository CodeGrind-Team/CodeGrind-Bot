import asyncio
import functools
from datetime import datetime
from typing import Callable

from constants import DifficultyScore


# https://stackoverflow.com/questions/65881761/discord-gateway-warning-shard-id-none-heartbeat-blocked-for-more-than-10-second
def to_thread(func: Callable) -> Callable:
    """
    Decorator to run a function in a separate thread.

    :param func: The function to run in a separate thread.

    :return: The wrapper function.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


def convert_to_score(easy: int = 0, medium: int = 0, hard: int = 0) -> int:
    """
    Convert the number of easy, medium, and hard questions into a score.

    :param easy: The number of easy questions.
    :param medium: The number of medium questions.
    :param hard: The number of hard questions.

    :return: The score.
    """
    return (
        easy * DifficultyScore.EASY
        + medium * DifficultyScore.MEDIUM
        + hard * DifficultyScore.HARD
    )


def strftime_with_suffix(format: str, t: datetime) -> str:
    """
    Format the datetime object with the day as a suffix.

    :param format: The format string.
    :param t: The datetime object.

    :return: The formatted string.
    """

    def suffix(d: int) -> str:
        """
        Get the suffix for the day.

        :param d: The day.
        """
        return {1: "st", 2: "nd", 3: "rd"}.get(d % 20, "th")

    return t.strftime(format).replace("{S}", str(t.day) + suffix(t.day))
