import discord


def success_embed(
    title: str = "Success", description: str | None = None
) -> discord.Embed:
    return discord.Embed(
        title=title, description=description, colour=discord.Colour.green()
    )


def failure_embed(title: str, description: str | None = None) -> discord.Embed:
    return discord.Embed(
        title=title, description=description, colour=discord.Colour.red()
    )


def error_embed(
    title: str = "Error", description: str = "An error occured! Please try again."
) -> discord.Embed:
    return discord.Embed(
        title=title, description=description, colour=discord.Colour.red()
    )
