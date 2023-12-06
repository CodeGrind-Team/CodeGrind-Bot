import asyncio
import functools
from typing import Callable


# https://stackoverflow.com/questions/65881761/discord-gateway-warning-shard-id-none-heartbeat-blocked-for-more-than-10-second
def to_thread(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


def calculate_scores(easy: int = 0, medium: int = 0, hard: int = 0) -> int:
    return easy * DIFFICULTY_SCORE['easy'] + medium * DIFFICULTY_SCORE['medium'] + hard * DIFFICULTY_SCORE['hard']
