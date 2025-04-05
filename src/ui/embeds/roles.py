import discord

from src.ui.embeds.common import success_embed


def roles_menu_embed() -> discord.Embed:
    return discord.Embed(
        title="CodeGrind Roles",
        description="The following roles will be given to users if this feature is "
        "enabled:\n"
        "- `CodeGrind verified`: Given to user's that have connected their LeetCode "
        "account to the bot in this server.\n"
        "- `Point milestones`: Given to user's depending on their total CodeGrind "
        "score.\n"
        "- `Streak`: Given to user's depending on their streak. Their streak is "
        "incremented each day if the user has completed a new LeetCode question (not "
        "necessarily the LeetCode daily question).",
    )


def roles_created_embed() -> discord.Embed:
    return success_embed(description="The roles have been created")


def roles_removed_embed() -> discord.Embed:
    return success_embed(description="The roles have been removed")
