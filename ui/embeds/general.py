import discord


def help_embed(description: str) -> discord.Embed:
    return discord.Embed(
        title="CodeGrind Bot Info & Commands",
        description=description,
        colour=discord.Colour.blurple(),
    )


def not_creator_embed() -> discord.Embed:
    return discord.Embed(
        title="Action denied",
        description="Only the person who used the command can use the buttons on this "
        "leaderboard",
        colour=discord.Colour.red(),
    )
