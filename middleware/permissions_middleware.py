from functools import wraps
from typing import Callable

import discord

from embeds.general_embeds import not_admin_embed


def admins_only(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs) -> Callable | None:
        if not interaction.user.guild_permissions.administrator:
            embed = not_admin_embed()
            await interaction.followup.send(embed=embed)
            return

        return await func(self, interaction, *args, **kwargs)

    return wrapper
