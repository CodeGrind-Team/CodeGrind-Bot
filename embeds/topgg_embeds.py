import discord


def topgg_not_voted() -> discord.Embed:
    embed = discord.Embed(
        title="You must vote on top.gg before using this feature!",
        color=discord.Color.red())

    url = "https://top.gg/bot/1059122559066570885/vote"

    embed.description = f"You can vote [here]({url})"

    embed.set_footer(
        text="Note: votes are reset on the first day of each month")

    return embed
