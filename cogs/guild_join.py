import discord
from discord.ext import commands

from bot_globals import logger, STREAK_ROLES, MILESTONE_ROLES, VERIFIED_ROLE
from embeds.misc_embeds import error_embed
from embeds.stats_embeds import stats_embed, account_hidden_embed
from embeds.users_embeds import account_not_found_embed
from models.user_model import User
from utils.middleware import admins_only, ensure_server_document, track_analytics

class GuildJoin(commands.Cog):
    def __init__(self, client):
        self.client = client

    # When the bot joins a server, create a new display information for each user in the server.
    @commands.Cog.listener()
    async def on_guild_join(self, guild) -> None:
        print(f'Joined {guild.name} with {guild.member_count} members!')

        # Create a new role
        await generate_connected_users_role(self, guild)
        await generate_milestone_users_role(self, guild)
        await generate_streaks_users_role(self, guild)

        return None
    
    @discord.app_commands.command(name="create-roles", description="Admins only: Creates roles on the server")
    @ensure_server_document
    @admins_only
    @track_analytics
    async def create_roles(self, interaction: discord.Interaction) -> None:
        logger.info("file: cogs/guild_join.py ~ createRoles ~ run")

        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel) or not isinstance(interaction.user, discord.Member):
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Create a new role
        await generate_connected_users_role(self, interaction.guild)
        await generate_milestone_users_role(self, interaction.guild)
        await generate_streaks_users_role(self, interaction.guild)

        await interaction.followup.send("Roles created successfully!", ephemeral=True)

    # When the bot joins the server, create a verified role to be used for connected users.
async def generate_connected_users_role(self, guild: discord.Guild) -> discord.Role:
    role_name = VERIFIED_ROLE
    role = discord.utils.get(guild.roles, name=role_name)

    if role is None:
        role = await guild.create_role(name=role_name, color=discord.Color.gray(), hoist=False, mentionable=False)

    return role

async def generate_milestone_users_role(self, guild: discord.Guild) -> None:
    created_roles = []

    for role in MILESTONE_ROLES:
        role_name, role_color = MILESTONE_ROLES.get(role)
        if discord.utils.get(guild.roles, name=role_name) is None:
            created_roles.append(await guild.create_role(name=role_name, color=role_color, hoist=False, mentionable=False))

    return created_roles

async def generate_streaks_users_role(self, guild: discord.Guild) -> discord.Role:
    created_roles = []

    for role in STREAK_ROLES:
        role_name, role_color = STREAK_ROLES.get(role)
        if discord.utils.get(guild.roles, name=role_name) is None:
            created_roles.append(await guild.create_role(name=role_name, color=role_color, hoist=False, mentionable=False))

    return created_roles


async def setup(client: commands.Bot):
    await client.add_cog(GuildJoin(client))