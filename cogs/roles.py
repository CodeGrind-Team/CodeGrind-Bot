import discord
from discord.ext import commands

from bot_globals import MILESTONE_ROLES, STREAK_ROLES, VERIFIED_ROLE, logger
from embeds.misc_embeds import error_embed
from embeds.roles_embeds import roles_created_embed
from utils.middleware import (admins_only, ensure_server_document,
                              track_analytics)
from utils.roles import generate_roles_from_dict, generate_roles_from_string


class Roles(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # When the bot joins a server, create a new display information for each user in the server.
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        logger.info('file: cogs/roles.py ~ on_guild_join ~ run')

        # Create a new role
        await generate_roles_from_string(guild, VERIFIED_ROLE)
        await generate_roles_from_dict(guild, MILESTONE_ROLES)
        await generate_roles_from_dict(guild, STREAK_ROLES)

    @discord.app_commands.command(name="create-roles", description="Admins only: Creates roles on the server")
    @ensure_server_document
    @admins_only
    @track_analytics
    async def create_roles(self, interaction: discord.Interaction):
        logger.info("file: cogs/guild_join.py ~ create_roles ~ run")

        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel) or not isinstance(interaction.user, discord.Member):
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        # Create the new roles
        await generate_roles_from_string(interaction.guild, VERIFIED_ROLE)
        await generate_roles_from_dict(interaction.guild, MILESTONE_ROLES)
        await generate_roles_from_dict(interaction.guild, STREAK_ROLES)

        embed = roles_created_embed()
        await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Roles(client))
