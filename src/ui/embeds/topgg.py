import discord

from ui.embeds.common import failure_embed


def topgg_not_voted_embed() -> discord.Embed:
    url = "https://top.gg/bot/1059122559066570885/vote"

    embed = failure_embed(
        title="You must vote on top.gg before using this feature!",
        description=f"You can vote [here]({url})",
    )

    embed.set_footer(
        text="Note: you will have access to these features for 30 days since voting, "
        "unless you vote again."
    )

    return embed
