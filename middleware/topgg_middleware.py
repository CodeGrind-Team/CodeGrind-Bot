from functools import wraps
from typing import Callable

import discord

from bot_globals import client
from embeds.topgg_embeds import topgg_not_voted


def topgg_vote_required(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs) -> Callable | None:
        voted = await client.topggpy.get_user_vote(interaction.user.id)

        if not voted:
            embed = topgg_not_voted()
            await interaction.followup.send(embed=embed)
            return

        return await func(self, interaction, *args, **kwargs)

    return wrapper
