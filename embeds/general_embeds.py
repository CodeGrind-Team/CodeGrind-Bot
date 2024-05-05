import discord


def help_embed(description: str) -> discord.Embed:
    embed = discord.Embed(
        title="CodeGrind Bot Info & Commands",
        url="https://github.com/CodeGrind-Team/CodeGrind-Bot/wiki/Commands",
        colour=discord.Colour.blurple(),
    )

    embed.description = description

    return embed


def not_admin_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Only admins can use this command", colour=discord.Colour.red()
    )

    return embed


def not_creator_embed() -> discord.Embed:
    embed = discord.Embed(title="Action denied", colour=discord.Colour.red())

    embed.description = (
        "Only the person who used the command can use the buttons on this leaderboard"
    )

    return embed
