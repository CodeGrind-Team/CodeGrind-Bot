import discord


def roles_created_embed() -> discord.Embed:
    embed = discord.Embed(title="Success", color=discord.Color.green())
    embed.description = "The roles have been created"
    return embed
