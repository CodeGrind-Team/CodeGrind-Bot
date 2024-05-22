from typing import TYPE_CHECKING

import discord

from constants import StatsCardExtensions
from ui.embeds.common import error_embed
from utils.stats import stats_card

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


async def stats_embed(
    bot: "DiscordBot",
    leetcode_id: str,
    display_name: str,
    extension: StatsCardExtensions,
) -> tuple[discord.Embed, discord.File | None]:
    file = await stats_card(bot, leetcode_id, display_name, extension)

    if not file:
        return error_embed(), None

    embed = discord.Embed(
        title=display_name,
        url=f"https://leetcode.com/{leetcode_id}",
        colour=discord.Colour.orange(),
    )
    embed.set_image(url=f"attachment://{leetcode_id}.png")

    return embed, file


def invalid_username_embed() -> discord.Embed:
    return discord.Embed(
        title="Error",
        description="The username you entered is invalid",
        colour=discord.Colour.red(),
    )


def account_hidden_embed() -> discord.Embed:
    return discord.Embed(
        title="Cannot access data",
        description="The chosen user has their LeetCode details hidden as their "
        "`include_url` setting is set to OFF",
        colour=discord.Colour.red(),
    )
