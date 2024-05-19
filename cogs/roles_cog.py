import discord
from discord.ext import commands

from database.models.server_model import Server
from embeds.roles_embeds import roles_created_embed, roles_removed_embed
from middleware import (
    admins_only,
    defer_interaction,
    ensure_server_document,
)
from utils.roles_utils import create_roles, remove_roles, update_roles


class RolesGroupCog(commands.GroupCog, name="roles"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command(
        name="enable",
        description="Admins only: create and assign CodeGrind roles to users",
    )
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @admins_only
    async def enable(self, interaction: discord.Interaction):
        """
        Command to enable CodeGrind roles assignment.

        :param interaction: The Discord interaction.
        """

        await create_roles(interaction.guild)

        server = await Server.find_one(
            Server.id == interaction.guild.id, fetch_links=True
        )
        await update_roles(interaction.guild, server)

        await interaction.followup.send(embed=roles_created_embed())

    @discord.app_commands.command(
        name="disable", description="Admins only: remove CodeGrind roles from users"
    )
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @admins_only
    async def disable(self, interaction: discord.Interaction):
        """
        Command to disable CodeGrind roles assignment.

        :param interaction: The Discord interaction.
        """
        await remove_roles(interaction.guild)

        await interaction.followup.send(embed=roles_removed_embed())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RolesGroupCog(bot))
