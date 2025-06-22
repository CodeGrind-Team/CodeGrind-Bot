import asyncio
import functools
from typing import Awaitable, Callable, Protocol

import discord

from src.constants import DifficultyScore


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
        easy * DifficultyScore.EASY.value
        + medium * DifficultyScore.MEDIUM.value
        + hard * DifficultyScore.HARD.value
    )


class GuildInteraction(Protocol):
    guild: discord.Guild
    guild_id: int
    user: discord.Member
    followup: discord.Webhook
    edit_original_response: Callable[..., Awaitable[discord.InteractionMessage]]
    response: discord.InteractionResponse

    async def original_response(self) -> discord.InteractionMessage: ...  # noqa: E704
