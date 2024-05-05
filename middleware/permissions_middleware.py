from functools import wraps
from typing import Callable

import discord

from embeds.general_embeds import not_admin_embed


def admins_only(func: Callable) -> Callable:
    """
    Decorator to restrict access to Discord commands to administrators only.

    This decorator ensures that the interaction user has administrator permissions in
    the Discord server before executing the wrapped function. If the user does not
    have administrator permissions, an appropriate error message is sent, and the
    original function is not executed.

    :param func: The function to be wrapped.

    :return: A decorator that restricts function execution to Discord administrators.
    """

    @wraps(func)
    async def wrapper(
        self, interaction: discord.Interaction, *args, **kwargs
    ) -> Callable | None:
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send(embed=not_admin_embed())
            return

        return await func(self, interaction, *args, **kwargs)

    return wrapper
