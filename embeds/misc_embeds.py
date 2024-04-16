import discord


def error_embed(title: str = "Error", description: str = "An error occured! Please try again.") -> discord.Embed:
    return discord.Embed(title=title, description=description,
                         colour=discord.Colour.red())
