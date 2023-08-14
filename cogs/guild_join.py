import discord
from discord.ext import commands

from bot_globals import logger
from embeds.stats_embeds import stats_embed, account_hidden_embed
from embeds.users_embeds import account_not_found_embed
from models.user_model import User
from utils.middleware import track_analytics

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

        return None

    # When the bot joins the server, create a verified role to be used for connected users.
async def generate_connected_users_role(self, guild: discord.Guild) -> discord.Role:
    role_name = "CodeGrind Verified"
    role = discord.utils.get(guild.roles, name=role_name)

    if role is None:
        role = await guild.create_role(name=role_name, color=discord.Color.gray(), hoist=True, mentionable=False)

    return role

async def generate_milestone_users_role(self, guild: discord.Guild) -> None:
    milestone_roles = {
        1: ("Initiate (1 Problem)", discord.Color.blue()),          # 1 Problem
        10: ("Problem Solver (10 Problems)", discord.Color.green()),  # 10 Problems
        25: ("Algorithm Apprentice (25 Problems)", discord.Color.gold()),  # 25 Problems
        50: ("Logic Guru (50 Problems)", discord.Color.purple()),     # 50 Problems
        75: ("Code Crusader (75 Problems)", discord.Color.orange()),  # 75 Problems
        100: ("LeetCode Legend (100 Problems)", discord.Color.red()),  # 100 Problems
        150: ("Problem Connoisseur (150 Problems)", discord.Color.teal()),  # 150 Problems
        200: ("Mastermind (200 Problems)", discord.Color.dark_blue())  # 200 Problems
    }

    created_roles = []

    for role in milestone_roles:
        role_name, role_color = milestone_roles.get(role)
        if discord.utils.get(guild.roles, name=role_name) is None:
            created_roles.append(await guild.create_role(name=role_name, color=role_color, hoist=True, mentionable=False))

    return created_roles

async def generate_streaks_users_role(self, guild: discord.Guild) -> discord.Role:
    streak_roles = {
        3: ("Streak Starter (3 Days)", discord.Color.blue()),          # 3 Days
        7: ("Streak Challenger (7 Days)", discord.Color.green()),  # 7 Days
        14: ("Streak Conqueror (14 Days)", discord.Color.gold()),  # 14 Days
        30: ("Streak Legend (30 Days)", discord.Color.purple()),     # 30 Days
    }

    created_roles = []

    for role in streak_roles:
        role_name, role_color = streak_roles.get(role)
        if discord.utils.get(guild.roles, name=role_name) is None:
            created_roles.append(await guild.create_role(name=role_name, color=role_color, hoist=True, mentionable=False))

    return created_roles


async def setup(client: commands.Bot):
    await client.add_cog(GuildJoin(client))