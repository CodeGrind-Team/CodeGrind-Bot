import discord
from discord.ext import commands

from bot_globals import MILESTONE_ROLES, STREAK_ROLES, VERIFIED_ROLE, logger
from embeds.misc_embeds import error_embed
from embeds.roles_embeds import roles_created_embed, roles_removed_embed
from utils.middleware import (admins_only, ensure_server_document,
                              track_analytics)
from utils.roles import (create_roles_from_dict, create_roles_from_string,
                         remove_roles_from_dict, remove_roles_from_string)


class Roles(commands.GroupCog, name="roles"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="enable", description="Admins only: create and give CodeGrind roles to users")
    @ensure_server_document
    @admins_only
    @track_analytics
    async def enable(self, interaction: discord.Interaction):
        logger.info("file: cogs/roles.py ~ roles enable ~ run")

        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel) or not isinstance(interaction.user, discord.Member):
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        # Create the new roles
        await create_roles_from_string(interaction.guild, VERIFIED_ROLE)
        await create_roles_from_dict(interaction.guild, MILESTONE_ROLES)
        await create_roles_from_dict(interaction.guild, STREAK_ROLES)

        embed = roles_created_embed()
        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="disable", description="Admins only: remove CodeGrind roles from users")
    @ensure_server_document
    @admins_only
    @track_analytics
    async def disable(self, interaction: discord.Interaction):
        logger.info("file: cogs/roles.py ~ roles disable ~ run")

        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel) or not isinstance(interaction.user, discord.Member):
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        # Delete the roles
        await remove_roles_from_string(interaction.guild, VERIFIED_ROLE)
        await remove_roles_from_dict(interaction.guild, MILESTONE_ROLES)
        await remove_roles_from_dict(interaction.guild, STREAK_ROLES)

        embed = roles_removed_embed()
        await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Roles(client))
