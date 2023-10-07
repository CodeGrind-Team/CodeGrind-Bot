import discord
from discord.ext import commands

from bot_globals import logger
from embeds.roles_embeds import (missing_manage_roles_permission_embed,
                                 roles_created_embed, roles_removed_embed)
from models.server_model import Server
from utils.middleware import (admins_only, defer_interaction,
                              ensure_server_document, track_analytics)
from utils.roles import create_roles, remove_roles, update_roles


class Roles(commands.GroupCog, name="roles"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="enable", description="Admins only: create and give CodeGrind roles to users")
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @admins_only
    @track_analytics
    async def enable(self, interaction: discord.Interaction):
        logger.info("file: cogs/roles.py ~ roles enable ~ run")

        if not interaction.guild.me.guild_permissions.manage_roles:
            embed = missing_manage_roles_permission_embed()
            await interaction.followup.send(embed=embed)
            return

        # Create the new roles
        await create_roles(interaction.guild)

        server = await Server.find_one(Server.id == interaction.guild.id, fetch_links=True)
        await update_roles(server)

        embed = roles_created_embed()
        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="disable", description="Admins only: remove CodeGrind roles from users")
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @admins_only
    @track_analytics
    async def disable(self, interaction: discord.Interaction):
        logger.info("file: cogs/roles.py ~ roles disable ~ run")

        if not interaction.guild.me.guild_permissions.manage_roles:
            embed = missing_manage_roles_permission_embed()
            await interaction.followup.send(embed=embed)
            return

        # Delete the roles
        await remove_roles(interaction.guild)

        embed = roles_removed_embed()
        await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Roles(client))
