import discord


def invalid_timezone_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Invalid timezone",
        color=discord.Color.red())

    url = "https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568"

    embed.description = f"Please provide a timezone (case sensitive) from {url}"

    return embed


def timezone_updated_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Timezone changed successfully",
        color=discord.Color.green())

    embed.description = f"Leaderboards will now display the last updated time in the selected timezone"

    return embed
