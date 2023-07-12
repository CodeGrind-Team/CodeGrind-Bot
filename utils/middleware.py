from functools import wraps
from typing import Callable

import discord

from embeds.general_embeds import not_admin_embed
from embeds.misc_embeds import error_embed
from models.server_model import Server


def ensure_server_document(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
        if not interaction.guild:
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        server_id = interaction.guild.id
        server = await Server.get(server_id)

        if not server:
            server = Server(id=server_id)
            await server.create()

        return await func(self, interaction, *args, **kwargs)

    return wrapper


def admins_only(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel) or not isinstance(interaction.user, discord.Member):
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not interaction.user.guild_permissions.administrator:
            embed = not_admin_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        return await func(self, interaction, *args, **kwargs)

    return wrapper
