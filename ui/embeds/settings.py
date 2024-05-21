import discord


def timezone_invalid_embed() -> discord.Embed:
    url = "https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568"

    return discord.Embed(
        title="Invalid timezone",
        description=f"Please provide a timezone (case sensitive) from {url}",
        colour=discord.Colour.red(),
    )


def timezone_updated_embed() -> discord.Embed:
    return discord.Embed(
        title="Timezone changed successfully",
        description="""Leaderboards will now display the last updated time in the
          selected timezone""",
        colour=discord.Colour.green(),
    )
