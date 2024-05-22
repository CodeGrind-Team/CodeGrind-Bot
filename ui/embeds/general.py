import discord

from ui.embeds.common import failure_embed
from ui.constants import CATEGORY_DESCRIPTIONS, CommandCategory


def help_embed(category: CommandCategory = CommandCategory.HOME) -> discord.Embed:
    return discord.Embed(
        title="CodeGrind Bot Info & Commands",
        description=CATEGORY_DESCRIPTIONS[category],
        colour=discord.Colour.blurple(),
    )


def not_creator_embed() -> discord.Embed:
    return failure_embed(
        title="Action denied",
        description="Only the user who ran the command can navigate and delete this "
        "leaderboard",
    )
