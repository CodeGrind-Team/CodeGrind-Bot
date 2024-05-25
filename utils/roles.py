import discord

from constants import MILESTONE_ROLES, STREAK_ROLES, VERIFIED_ROLE
from database.models import Preference, User


async def create_roles_from_string(guild: discord.Guild, role: str) -> None:
    """
    Create a role in the guild if it doesn't already exist.

    :param guild: The guild in which to create the role.
    :param role: The name of the role to create.
    """
    role_found = discord.utils.get(guild.roles, name=role)
    if not role_found:
        guild.me.guild_permissions.manage_roles
        await guild.create_role(
            name=role,
            colour=discord.Colour.light_gray(),
            hoist=False,
            mentionable=False,
        )


async def create_roles_from_dict(guild: discord.Guild, roles: dict) -> None:
    """
    Create roles in the guild based on a dictionary of roles and their colours.

    :param guild: The guild in which to create the roles.
    :param roles: A dictionary where keys are role names and values are role colours.
    """
    for role in roles:
        role_name, role_colour = roles[role]
        role_found = discord.utils.get(guild.roles, name=role_name)
        if not role_found:
            await guild.create_role(
                name=role_name, colour=role_colour, hoist=False, mentionable=False
            )


async def remove_roles_from_string(guild: discord.Guild, role: str) -> None:
    """
    Remove a role from the guild.

    :param guild: The guild from which to remove the role.
    :param role: The name of the role to remove.
    """
    role_found = discord.utils.get(guild.roles, name=role)

    if role_found:
        await role_found.delete()


async def remove_roles_from_dict(guild: discord.Guild, roles: dict) -> None:
    """
    Remove roles from the guild based on a dictionary of roles.

    :param guild: The guild from which to remove the roles.
    :param roles: A dictionary where keys are role names to be removed.
    """
    for role in roles:
        role_name, _ = roles[role]

        role_found = discord.utils.get(guild.roles, name=role_name)

        if role_found:
            await role_found.delete()


async def create_roles(guild: discord.Guild) -> None:
    """
    Create default roles in the guild.

    :param guild: The guild in which to create the roles.
    """
    if not guild.me.guild_permissions.manage_roles:
        return

    await create_roles_from_string(guild, VERIFIED_ROLE)
    await create_roles_from_dict(guild, MILESTONE_ROLES)
    await create_roles_from_dict(guild, STREAK_ROLES)


async def remove_roles(guild: discord.Guild) -> None:
    """
    Remove default roles from the guild.

    :param guild: The guild from which to remove the roles.
    """
    if not guild.me.guild_permissions.manage_roles:
        return

    await remove_roles_from_string(guild, VERIFIED_ROLE)
    await remove_roles_from_dict(guild, MILESTONE_ROLES)
    await remove_roles_from_dict(guild, STREAK_ROLES)


async def update_roles(guild: discord.Guild, server_id: int) -> None:
    """
    Update roles for users in the server based on their stats.

    :param guild: The guild in which to update the roles.
    :param server_id: The id of the server to update its roles.
    """
    if not guild.me.guild_permissions.manage_roles:
        return

    async for preference in Preference.find_many(Preference.server_id == server_id):
        user = await User.find_one(User.id == preference.user_id)

        if not user:
            # This shouldn't happen
            continue

        member = guild.get_member(user.id)

        if not member:
            continue

        await give_verified_role(guild, member)
        await give_streak_role(guild, member, user.stats.streak)
        await give_milestone_role(guild, member, user.stats.submissions.score)


async def give_verified_role(guild: discord.Guild, member: discord.Member) -> None:
    """
    Give the verified role to a member.

    :param guild: The guild in which to give the role.
    :param member: The member to whom to give the role.
    """
    role = discord.utils.get(guild.roles, name=VERIFIED_ROLE)

    # Check if the role exists
    if not role:
        return

    await member.add_roles(role)


async def give_streak_role(
    guild: discord.Guild, member: discord.Member, streak: int
) -> None:
    """
    Give a streak role to a user based on their streak.

    :param guild: The guild in which to give the role.
    :param member: The member to whom to give the role.
    :param streak: The streak of the user.
    """
    role_to_assign = None

    for role_streak, (role_name, _) in STREAK_ROLES.items():
        if streak >= role_streak:
            role_to_assign = discord.utils.get(guild.roles, name=role_name)
        else:
            break

    # Remove all other roles.
    for role_milestone, _ in STREAK_ROLES.items():
        role_name, _ = STREAK_ROLES[role_milestone]
        role = discord.utils.get(guild.roles, name=role_name)
        if role and role in member.roles:
            await member.remove_roles(role)

    if role_to_assign:
        # Give the member the appropriate role.
        await member.add_roles(role_to_assign)


async def give_milestone_role(
    guild: discord.Guild, member: discord.Member, total_solved: int
) -> None:
    """
    Give a milestone role to a user based on their total solved milestones.

    :param guild: The guild in which to give the role.
    :param member: The member to whom to give the role.
    :param total_solved: The total solved milestones of the user.
    """
    role_to_assign = None

    for role_milestone, (role_name, _) in MILESTONE_ROLES.items():
        if total_solved >= role_milestone:
            role_to_assign = discord.utils.get(guild.roles, name=role_name)

    # Remove all other roles
    for role_milestone, _ in MILESTONE_ROLES.items():
        role_name, _ = MILESTONE_ROLES[role_milestone]
        role = discord.utils.get(guild.roles, name=role_name)
        if role and role in member.roles:
            await member.remove_roles(role)

    if role_to_assign:
        # Give the member the appropriate role
        await member.add_roles(role_to_assign)
