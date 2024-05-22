import discord
import pytz

from constants import DifficultyScore
from database.models import Server
from ui.embeds.common import failure_embed
from utils.common import strftime_with_suffix


def empty_leaderboard_embed() -> discord.Embed:
    return failure_embed(
        title="Leaderboard is empty",
        description="Nobody has connected their account to this server's leaderboards "
        "yet",
    )


def leaderboard_embed(
    server: Server, page_i: int, page_count: int, title: str, leaderboard: str
) -> discord.Embed:
    embed = discord.Embed(
        title=title, description=leaderboard, colour=discord.Colour.yellow()
    )

    last_updated_start = strftime_with_suffix(
        "{S} %b %Y between %H:%M",
        pytz.timezone("UTC")
        .localize(server.last_update_start)
        .astimezone(pytz.timezone(server.timezone)),
    )

    last_updated_end = strftime_with_suffix(
        "%H:%M %Z",
        pytz.timezone("UTC")
        .localize(server.last_update_end)
        .astimezone(pytz.timezone(server.timezone)),
    )

    embed.set_footer(
        text=f"Easy: {DifficultyScore.EASY.value} point, Medium: "
        f"{DifficultyScore.MEDIUM.value} points, Hard: {DifficultyScore.HARD.value} "
        f"points\nUpdated on {last_updated_start} - {last_updated_end}\nPage "
        f"{page_i + 1}/{page_count}"
    )

    return embed
