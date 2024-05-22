import discord
from ui.embeds.common import success_embed


def roles_menu_embed() -> discord.Embed:
    return discord.Embed(
        title="Roles Menu",
        description="CodeGrind roles " "Enable or disable",
    )


def roles_created_embed() -> discord.Embed:
    return success_embed(description="The roles have been created")


def roles_removed_embed() -> discord.Embed:
    return success_embed(description="The roles have been removed")
