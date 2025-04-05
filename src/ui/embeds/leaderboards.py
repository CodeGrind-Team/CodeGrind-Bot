import discord
import pytz

from src.constants import DifficultyScore
from src.database.models import Server
from src.ui.embeds.common import failure_embed


def empty_leaderboard_embed() -> discord.Embed:
    return failure_embed(
        title="Leaderboard is empty",
        description="Nobody has connected their account to this server's leaderboards "
        "yet",
    )


def leaderboard_embed(
    server: Server,
    page_i: int,
    page_count: int,
    title: str,
    leaderboard: str,
    include_page_count: bool = True,
) -> discord.Embed:
    embed = discord.Embed(
        title=title, description=leaderboard, colour=discord.Colour.yellow()
    )
    # Converting the unaware datetime to a timezone-aware one is required
    # to display the correct timestamp to the user.

    # Short Date/Time relative timestamp format: <t:{timestamp}:f>,
    last_updated_start = (
        f"<t:{int(pytz.utc.localize(server.last_update_start).timestamp())}:f>"
    )
    # Short Time relative timestamp format: <t:{timestamp}:t>,
    last_updated_end = (
        f"<t:{int(pytz.utc.localize(server.last_update_end).timestamp())}:t>"
    )
    page_count_text = (
        f"\n-# Page {page_i + 1}/{page_count}" if include_page_count else ""
    )

    # '-#' displays as subtext (smaller font and less visible colour) whilst
    # still allowing the use of other markdown formatting and relative timestamps
    # unlike the embed's footer.
    embed.description += (
        f"\n\n-# Easy: {DifficultyScore.EASY.value} pt | Medium: "
        f"{DifficultyScore.MEDIUM.value} pts | Hard: {DifficultyScore.HARD.value} "
        f"pts"
        f"\n-# Updated on {last_updated_start} - {last_updated_end}"
        f"{page_count_text}"
    )

    return embed
