import discord
import pytz

from constants import DifficultyScore
from database.models import Server
from utils.common import strftime_with_suffix


def empty_leaderboard_embed() -> discord.Embed:
    return discord.Embed(
        title="Leaderboard is empty",
        description="No one has added their LeetCode username yet",
        colour=discord.Colour.red(),
    )


def leaderboard_embed(
    server: Server, page_i: int, page_count: int, title: str, leaderboard: str
) -> discord.Embed:
    embed = discord.Embed(
        title=title, description="\n".join(leaderboard), colour=discord.Colour.yellow()
    )

    last_updated_start = strftime_with_suffix(
        "{S} %b %Y at %H:%M %Z",
        pytz.timezone("UTC")
        .localize(server.last_update_start)
        .astimezone(pytz.timezone(server.timezone)),
    )

    last_updated_end = strftime_with_suffix(
        "{S} %b %Y at %H:%M %Z",
        pytz.timezone("UTC")
        .localize(server.last_update_end)
        .astimezone(pytz.timezone(server.timezone)),
    )

    embed.set_footer(
        text=f"""Easy: {DifficultyScore.EASY.value} point, Medium:
          {DifficultyScore.MEDIUM.value} points, Hard: {DifficultyScore.HARD.value}
            points\nUpdated between {last_updated_start} - {last_updated_end}
            \nPage {page_i + 1}/{page_count}"""
    )

    return embed
