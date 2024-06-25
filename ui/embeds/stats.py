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
    display_url: bool,
    extension: StatsCardExtensions,
) -> tuple[discord.Embed, discord.File | None]:
    file = await stats_card(bot, leetcode_id, extension)

    if not file:
        return error_embed(), None

    if display_url:
        embed = discord.Embed(
            title=display_name,
            url=f"https://leetcode.com/{leetcode_id}",
            colour=discord.Colour.orange(),
        )
    else:
        embed = discord.Embed(
            title=display_name,
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
        description="The user has chosen not to make their LeetCode account public",
        colour=discord.Colour.red(),
    )
