import discord


def topgg_not_voted() -> discord.Embed:
    url = "https://top.gg/bot/1059122559066570885/vote"

    embed = discord.Embed(
        title="You must vote on top.gg before using this feature!",
        description=f"You can vote [here]({url})",
        colour=discord.Colour.red(),
    )

    embed.set_footer(
        text="""Note: you will have access to these features for 30 days since voting,
          unless you vote again."""
    )

    return embed
