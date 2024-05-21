import discord


def topgg_not_voted() -> discord.Embed:
    embed = discord.Embed(
        title="You must vote on top.gg before using this feature!",
        colour=discord.Colour.red(),
    )

    url = "https://top.gg/bot/1059122559066570885/vote"

    embed.description = f"You can vote [here]({url})"

    embed.set_footer(
        text="Note: you will have access to these features for 30 days since voting, unless you vote again."
    )

    return embed
