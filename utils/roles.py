import discord

from bot_globals import (MILESTONE_ROLES, STREAK_ROLES, VERIFIED_ROLE, client,
                         logger)
from models.user_model import User
from models.server_model import Server


async def create_roles_from_string(guild: discord.Guild, role: str):
    role_found = discord.utils.get(guild.roles, name=role)

    if not role_found:
        try:
            await guild.create_role(name=role, color=discord.Color.light_gray(),
                                    hoist=False, mentionable=False)
        except discord.errors.Forbidden:
            logger.exception(
                "file: cogs/roles.py ~ create_roles_from_string ~ 403 Forbidden error")


async def create_roles_from_dict(guild: discord.Guild, roles: dict):
    for role in roles:
        role_name, role_color = roles[role]

        if discord.utils.get(guild.roles, name=role_name) is None:
            try:
                await guild.create_role(name=role_name, color=role_color,
                                        hoist=False, mentionable=False)
            except discord.errors.Forbidden:
                logger.exception(
                    "file: cogs/roles.py ~ create_roles_from_dict ~ 403 Forbidden error")


async def remove_roles_from_string(guild: discord.Guild, role: str):
    role_found = discord.utils.get(guild.roles, name=role)

    if role_found:
        try:
            await role_found.delete()
        except discord.errors.Forbidden:
            logger.exception(
                "file: cogs/roles.py ~ remove_roles_from_string ~ 403 Forbidden error")


async def remove_roles_from_dict(guild: discord.Guild, roles: dict):
    for role in roles:
        role_name, _ = roles[role]

        role_found = discord.utils.get(guild.roles, name=role_name)

        if role_found:
            try:
                await role_found.delete()
            except discord.errors.Forbidden:
                logger.exception(
                    "file: cogs/roles.py ~ remove_roles_from_dict ~ 403 Forbidden error")

                
async def update_roles(server: Server):
    for user in server.users:
        await give_verified_role(user, server.id)
        await give_streak_role(user, server.id, user.scores.streak)
        await give_milestone_role(user, server.id, user.submissions.total_score)


async def give_verified_role(user: discord.User, guild_id: int) -> None:
    guild = client.get_guild(guild_id)

    if not guild:
        return

    discord_user = guild.get_member(user.id)

    if not discord_user:
        return

    role_to_assign = discord.utils.get(guild.roles, name=VERIFIED_ROLE)

    # Check if the role exists
    if role_to_assign is None:
        return

    try:
        # Attempt to assign the role to the user
        await discord_user.add_roles(role_to_assign)
    except discord.errors.Forbidden:
        logger.exception(
            "file: cogs/roles.py ~ give_verified_role ~ run ~ 403 Forbidden error")
    except Exception as e:
        # Handle other exceptions
        logger.exception(
            "file: cogs/roles.py ~ give_verified_role ~ run ~ error: %s", e)


async def give_streak_role(user: discord.User, guild_id: int, streak: int) -> None:
    logger.info(
        "file: utils/roles.py ~ give_streak_role ~ run ~ user_id: %s ~ streak: %s", user.id, streak)
    guild = client.get_guild(guild_id)

    if not guild:
        return

    discord_user = guild.get_member(user.id)

    if not discord_user:
        return

    role_to_assign = None

    for role_streak, (role_name, _) in STREAK_ROLES.items():
        if streak >= role_streak:
            role_to_assign = discord.utils.get(guild.roles, name=role_name)

    # Remove all other roles
    for role_streak, _ in STREAK_ROLES.items():
        role_name, _ = STREAK_ROLES[role_streak]
        role = discord.utils.get(guild.roles, name=role_name)
        if role is not None:
            await discord_user.remove_roles(role)

    if role_to_assign:
        # Give the user the appropriate role
        await discord_user.add_roles(role_to_assign)
        logger.info(
            "file: utils/roles.py ~ give_streak_role ~ assigned %s role to %s", role_to_assign.name, discord_user.display_name)
    else:
        logger.warning(
            "file: utils/roles.py ~ give_streak_role ~ no suitable streak role found.")


async def give_milestone_role(user: discord.User, guild_id: int, total_solved: int) -> None:
    logger.info(
        "file: utils/roles.py ~ give_milestone_role ~ run ~ user_id: %s, total_solved: %s, guild_id: %s", user.id, total_solved, guild_id)

    guild = client.get_guild(guild_id)

    if not guild:
        return

    discord_user = guild.get_member(user.id)

    if not discord_user:
        return

    role_to_assign = None

    for role_milestone, (role_name, _) in MILESTONE_ROLES.items():
        if total_solved >= role_milestone:
            role_to_assign = discord.utils.get(guild.roles, name=role_name)

    # Remove all other roles
    for role_milestone, _ in MILESTONE_ROLES.items():
        role_name, _ = MILESTONE_ROLES[role_milestone]
        role = discord.utils.get(guild.roles, name=role_name)
        if role is not None:
            await discord_user.remove_roles(role)

    if role_to_assign:
        # Give the user the appropriate role
        await discord_user.add_roles(role_to_assign)
        logger.info("file: utils/roles.py ~ give_milestone_role ~ assigned %s role to %s", role_to_assign.name,
                    discord_user.display_name)
    else:
        logger.warning(
            "file: utils/roles.py ~ give_milestone_role ~ no suitable milestone role found.")
