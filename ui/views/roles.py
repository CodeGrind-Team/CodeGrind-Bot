import discord

from database.models import Server
from ui.embeds.roles import roles_created_embed, roles_removed_embed
from utils.roles import create_roles, remove_roles, update_roles


class RolesView(discord.ui.View):
    @discord.ui.button(label="Enable", style=discord.ButtonStyle.blurple)
    async def enable(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        await interaction.response.defer()

        await create_roles(interaction.guild)

        server = await Server.find_one(
            Server.id == interaction.guild.id, fetch_links=True
        )
        await update_roles(interaction.guild, server)

        await interaction.followup.send(embed=roles_created_embed())

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        await interaction.response.defer()

        await remove_roles(interaction.guild)

        await interaction.followup.send(embed=roles_removed_embed())
