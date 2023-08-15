import discord
from discord.ext import commands

from bot_globals import logger
from embeds.stats_embeds import stats_embed, account_hidden_embed
from embeds.users_embeds import account_not_found_embed
from models.user_model import User
from utils.middleware import track_analytics

from bot_globals import STREAK_ROLES, MILESTONE_ROLES, VERIFIED_ROLE

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

    # When the bot joins the server, create a verified role to be used for connected users.
async def generate_connected_users_role(self, guild: discord.Guild) -> discord.Role:
    role_name = VERIFIED_ROLE
    role = discord.utils.get(guild.roles, name=role_name)

    if role is None:
        role = await guild.create_role(name=role_name, color=discord.Color.gray(), hoist=True, mentionable=False)

    return role

async def generate_milestone_users_role(self, guild: discord.Guild) -> None:
    created_roles = []

    for role in MILESTONE_ROLES:
        role_name, role_color = MILESTONE_ROLES.get(role)
        if discord.utils.get(guild.roles, name=role_name) is None:
            created_roles.append(await guild.create_role(name=role_name, color=role_color, hoist=True, mentionable=False))

    return created_roles

async def generate_streaks_users_role(self, guild: discord.Guild) -> discord.Role:
    created_roles = []

    for role in STREAK_ROLES:
        role_name, role_color = STREAK_ROLES.get(role)
        if discord.utils.get(guild.roles, name=role_name) is None:
            created_roles.append(await guild.create_role(name=role_name, color=role_color, hoist=True, mentionable=False))

    return created_roles


async def setup(client: commands.Bot):
    await client.add_cog(GuildJoin(client))