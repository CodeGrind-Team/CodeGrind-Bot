from datetime import UTC, datetime
from functools import wraps
from typing import Callable

import discord

from database.models import User
from embeds.topgg_embeds import topgg_not_voted


def topgg_vote_required(func: Callable) -> Callable:
    """
    Decorator to require a user to have voted on Top.gg within the last 30 days before
    executing a function.

    This decorator checks if the Discord user has voted on Top.gg recently. If not, it
    sends a message indicating that voting is required and prevents the wrapped
    function from executing. If the user has voted, the wrapped function is executed.

    :param func: The function to be wrapped.
    :return: A decorator that checks if the user has voted on Top.gg recently.
    """

    @wraps(func)
    async def wrapper(
        self, interaction: discord.Interaction, *args, **kwargs
    ) -> Callable | None:
        user = await User.find_one(User.id == interaction.user.id)

        if not user.votes.last_voted or (
            user.votes.last_voted
            and (datetime.now(UTC) - user.votes.last_voted).days > 30
        ):
            await interaction.followup.send(embed=topgg_not_voted())
            return

        return await func(self, interaction, *args, **kwargs)

    return wrapper
