import asyncio
import functools
from typing import Callable

from bot_globals import file_lock


# https://stackoverflow.com/questions/65881761/discord-gateway-warning-shard-id-none-heartbeat-blocked-for-more-than-10-second
def to_thread(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with file_lock:
            return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper
