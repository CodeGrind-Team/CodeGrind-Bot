from typing import cast

import discord

from src.ui.embeds.roles import roles_created_embed, roles_removed_embed
from src.utils.common import GuildInteraction
from src.utils.roles import create_roles, remove_roles, update_roles


class RolesView(discord.ui.View):
    @discord.ui.button(label="Enable", style=discord.ButtonStyle.blurple)
    async def enable(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        guild_interaction = cast(GuildInteraction, interaction)

        await guild_interaction.response.defer()

        await create_roles(guild_interaction.guild)
        await update_roles(guild_interaction.guild, guild_interaction.guild_id)

        await guild_interaction.followup.send(embed=roles_created_embed())

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        guild_interaction = cast(GuildInteraction, interaction)

        await guild_interaction.response.defer()

        await remove_roles(guild_interaction.guild)

        await guild_interaction.followup.send(embed=roles_removed_embed())
