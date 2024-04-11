import asyncio
import functools
from datetime import datetime
from typing import Callable

from bot_globals import DIFFICULTY_SCORE


# https://stackoverflow.com/questions/65881761/discord-gateway-warning-shard-id-none-heartbeat-blocked-for-more-than-10-second
def to_thread(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


def convert_to_score(easy: int = 0, medium: int = 0, hard: int = 0) -> int:
    return easy * DIFFICULTY_SCORE['easy'] + medium * DIFFICULTY_SCORE['medium'] + hard * DIFFICULTY_SCORE['hard']


def strftime_with_suffix(format: str, t: datetime) -> str:
    def suffix(d):
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 20, 'th')
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))
