from typing import Any

import discord
from discord import Role

from constants import MILESTONE_ROLES, STREAK_ROLES, VERIFIED_ROLE, CodeGrindTierInfo
from database.models import Profile, User


def get_highest_tier_info(
    tier_group: dict[Any, CodeGrindTierInfo], val: int
) -> CodeGrindTierInfo:
    """
    Get the highest tier info based on a value.

    :param val: The value to check against.
    :return: The highest tier info.
    """
    highest_tier_info = None

    for tier_info in tier_group.values():
        if val < tier_info.threshold:
            break

        highest_tier_info = tier_info

    return highest_tier_info


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


async def create_roles_from_dict(
    guild: discord.Guild, roles: dict[Any, CodeGrindTierInfo]
) -> None:
    """
    Create roles in the guild based on a dictionary of roles and their colours.

    :param guild: The guild in which to create the roles.
    :param roles: A dictionary where keys are role names and values are role colours.
    """
    for codegrind_tier in roles.values():
        role_found = discord.utils.get(guild.roles, name=codegrind_tier.role_name)
        if not role_found:
            await guild.create_role(
                name=codegrind_tier.role_name,
                colour=codegrind_tier.role_colour,
                hoist=False,
                mentionable=False,
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


async def remove_roles_from_dict(
    guild: discord.Guild, roles: dict[Any, CodeGrindTierInfo]
) -> None:
    """
    Remove roles from the guild based on a dictionary of roles.

    :param guild: The guild from which to remove the roles.
    :param roles: A dictionary where keys are role names to be removed.
    """
    for codegrind_tier in roles.values():
        role_found = discord.utils.get(guild.roles, name=codegrind_tier.role_name)

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

    async for profile in Profile.find_many(Profile.server_id == server_id):
        user = await User.find_one(User.id == profile.user_id)

        if not user:
            # This shouldn't happen
            continue

        member = guild.get_member(user.id)

        if not member:
            continue

        await give_verified_role(guild, member)
        await give_tier_group_role(guild, member, STREAK_ROLES, user.stats.streak)
        await give_tier_group_role(
            guild, member, MILESTONE_ROLES, user.stats.submissions.score
        )


async def give_verified_role(guild: discord.Guild, member: discord.Member) -> None:
    """
    Give the verified role to a member.

    :param guild: The guild in which to give the role.
    :param member: The member to whom to give the role.
    """
    role = discord.utils.get(guild.roles, name=VERIFIED_ROLE)

    # Check if the role exists
    if not role or role in member.roles:
        return

    await member.add_roles(role)


async def give_tier_group_role(
    guild: discord.Guild,
    member: discord.Member,
    tier_group: dict[Any, CodeGrindTierInfo],
    user_value: int,
) -> None:
    """
    Give a tier group role to a user based on their value (e.g. points or streak).

    :param guild: The guild in which to give the role.
    :param member: The member to whom to give the role.
    :param tier_group: The tier group to assign roles from.
    :param user_value: The user's value.
    """
    role_to_assign: Role | None = None
    if highest_tier_info := get_highest_tier_info(MILESTONE_ROLES, user_value):
        role_to_assign = discord.utils.get(
            guild.roles, name=highest_tier_info.role_name
        )

    # Remove all other roles.
    for codegrind_tier in tier_group.values():
        role = discord.utils.get(guild.roles, name=codegrind_tier.role_name)
        if role and role in member.roles and role != role_to_assign:
            await member.remove_roles(role)

    if role_to_assign:
        # Give the member the appropriate role.
        await member.add_roles(role_to_assign)
