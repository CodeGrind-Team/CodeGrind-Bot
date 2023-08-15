import discord
from discord.ext import commands

from bot_globals import logger, STREAK_ROLES, MILESTONE_ROLES, VERIFIED_ROLE
from embeds.misc_embeds import error_embed
from embeds.stats_embeds import stats_embed, account_hidden_embed
from embeds.users_embeds import account_not_found_embed
from models.user_model import User
from utils.middleware import admins_only, ensure_server_document, track_analytics

class GuildJoin(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # When the bot joins a server, create a new display information for each user in the server.
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
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

        await interaction.followup.send("Roles created successfully!")

    # When the bot joins the server, create a verified role to be used for connected users.
async def generate_connected_users_role(self, guild: discord.Guild) -> None:
    generate_roles_from_string(self, guild, VERIFIED_ROLE)


async def generate_milestone_users_role(self, guild: discord.Guild) -> None:
    generate_roles_from_dict(self, guild, MILESTONE_ROLES)


async def generate_streaks_users_role(self, guild: discord.Guild) -> None:
    generate_roles_from_dict(self, guild, STREAK_ROLES)


async def generate_roles_from_dict(self, guild: discord.Guild, roles: dict) -> None:
    for role in roles:
        role_name, role_color = roles[role]

        if discord.utils.get(guild.roles, name=role_name) is None:
            await guild.create_role(name=role_name, color=role_color,
                                    hoist=False, mentionable=False)


async def generate_roles_from_string(self, guild: discord.Guild, role: str) -> None:
    role = discord.utils.get(guild.roles, name=role)

    if role is None:
        role = await guild.create_role(name=role, color=discord.Color.gray(),
                                        hoist=False, mentionable=False)


async def setup(client: commands.Bot):
    await client.add_cog(GuildJoin(client))