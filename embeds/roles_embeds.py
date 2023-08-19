import discord


def roles_created_embed() -> discord.Embed:
    embed = discord.Embed(title="Success", color=discord.Color.green())
    embed.description = "The roles have been created"
    return embed


def roles_removed_embed() -> discord.Embed:
    embed = discord.Embed(title="Success", color=discord.Color.green())
    embed.description = "The roles have been removed"
    return embed


def missing_manage_roles_permission_embed() -> discord.Embed:
    embed = discord.Embed(title="Error", color=discord.Color.red())
    embed.description = "CodeGrind Bot does not have `manage roles` permission.\nPlease enable this permission in the bot's role."
    return embed
