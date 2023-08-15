import discord
from bot_globals import MILESTONE_ROLES, STREAK_ROLES, logger, client

async def give_user_streak_role(user: discord.User, guild_id: int, streak: int) -> None:
    logger.info(f"file: utils/stats.py ~ give_user_streak_role ~ run - {user.id} - {streak}")
    guild = client.get_guild(guild_id)

    if not guild:
        return
    
    discord_user = guild.get_member(user.id)

    if not discord_user:
        return
    
    role_to_assign = None
    
    for role_streak, (role_name, role_color) in STREAK_ROLES.items():
        if streak >= role_streak:
            role_to_assign = discord.utils.get(guild.roles, name=role_name)
    
    # Remove all other streak roles
    for role_streak, _ in STREAK_ROLES.items():
        role_name, _ = STREAK_ROLES.get(role_streak)
        role = discord.utils.get(guild.roles, name=role_name)
        if (role and role in discord_user.roles and role != role_to_assign) or role_to_assign is None:
            await discord_user.remove_roles(role)
            
    if role_to_assign:
        # Give the user the appropriate streak role
        await discord_user.add_roles(role_to_assign)
        logger.info(f"Assigned {role_to_assign.name} role to {discord_user.display_name}")
    else:
        logger.warning("No suitable streak role found.")

    return None

async def give_user_milestone_role(user: discord.User, guild_id: int, totalSolved: int) -> None:
    logger.info(f"file: utils/stats.py ~ give_user_milestone_role ~ run - {user.id} - {totalSolved} - {guild_id}")

    guild = client.get_guild(guild_id)

    if not guild:
        return
    
    discord_user = guild.get_member(user.id)

    if not discord_user:
        return
    
    role_to_assign = None
    
    for role_milestone, (role_name, role_color) in MILESTONE_ROLES.items():
        if totalSolved >= role_milestone:
            role_to_assign = discord.utils.get(guild.roles, name=role_name)
    
    # Remove all other streak roles
    for role_milestone, _ in MILESTONE_ROLES.items():
        role_name, _ = MILESTONE_ROLES.get(role_milestone)
        role = discord.utils.get(guild.roles, name=role_name)
        if (role and role in discord_user.roles and role != role_to_assign) or role_to_assign is None:
            await discord_user.remove_roles(role)
    
    if role_to_assign:
        # Give the user the appropriate streak role
        await discord_user.add_roles(role_to_assign)
        logger.info(f"Assigned {role_to_assign.name} role to {discord_user.display_name}")
    else:
        logger.warning("No suitable milestone role found.")

    return None