import discord
import pytz

from constants import DifficultyScore
from database.models.server_model import Server
from utils.common_utils import strftime_with_suffix


def empty_leaderboard_embed() -> discord.Embed:
    embed = discord.Embed(
        title=f"Leaderboard is empty",
        description="No one has added their LeetCode username yet",
        colour=discord.Colour.red(),
    )

    return embed


def leaderboard_embed(
    server: Server, page_i: int, page_count: int, title: str, leaderboard: str
) -> discord.Embed:
    embed = discord.Embed(title=title, colour=discord.Colour.yellow())

    embed.description = "\n".join(leaderboard)

    last_updated = strftime_with_suffix(
        "{S} %b %Y at %H:%M %Z",
        pytz.timezone("UTC")
        .localize(server.last_updated)
        .astimezone(pytz.timezone(server.timezone)),
    )

    # ! add start and end update to footer

    embed.set_footer(
        text=f"Easy: {DifficultyScore.EASY.value} point, Medium: {DifficultyScore.MEDIUM.value} points, Hard: {DifficultyScore.HARD.value} points\nUpdated on {last_updated}\nPage {page_i + 1}/{page_count}"
    )

    return embed
