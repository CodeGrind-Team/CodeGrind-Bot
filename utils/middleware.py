from functools import wraps
from typing import Callable

import discord

from embeds.general_embeds import not_admin_embed
from embeds.misc_embeds import error_embed
from models.server_model import Server
from models.analytics_model import Analytics


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


def track_analytics(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel) or not isinstance(interaction.user, discord.Member):
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        analytics = await Analytics.find_all().to_list()

        if not analytics:
            analytics = Analytics()
            await analytics.create()
        else:
            analytics = analytics[0]

        if interaction.user.id not in analytics.distinct_users_total:
            analytics.distinct_users_total.append(interaction.user.id)

        if interaction.user.id not in analytics.distinct_users_today:
            analytics.distinct_users_today.append(interaction.user.id)

        analytics.command_count_today += 1
        await analytics.save()

        return await func(self, interaction, *args, **kwargs)

    return wrapper
