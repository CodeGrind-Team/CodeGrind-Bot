from functools import wraps
from typing import Callable

import discord

from embeds.misc_embeds import error_embed

from .database_middleware import update_user_preferences_prompt


def defer_interaction(*, ephemeral_default: bool = False, user_preferences_prompt: bool = False) -> Callable:
    def ephemeral_response(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs) -> Callable | None:
            display_publicly: bool | None = kwargs.get(
                'display_publicly', None)

            ephemeral = not display_publicly if display_publicly is not None else ephemeral_default

            await interaction.response.defer(ephemeral=ephemeral)

            if not interaction.guild or not isinstance(interaction.channel, (discord.TextChannel, discord.Thread)) or not isinstance(interaction.user, discord.Member):
                embed = error_embed()
                await interaction.followup.send(embed=embed)
                return

            ret = await func(self, interaction, *args, **kwargs)

            if user_preferences_prompt:
                await update_user_preferences_prompt(interaction, reminder=True)

            return ret

        return wrapper
    return ephemeral_response
