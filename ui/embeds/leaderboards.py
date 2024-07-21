import discord

from constants import DifficultyScore
from database.models import Server
from ui.embeds.common import failure_embed


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

    # Short Date/Time relative timestamp format: <t:{timestamp}:f>,
    last_updated_start = f"<t:{int(server.last_update_start.timestamp())}:f>"
    # Short Time relative timestamp format: <t:{timestamp}:t>,
    last_updated_end = f"<t:{int(server.last_update_end.timestamp())}:t>"
    page_count_text = (
        f"\n-# Page {page_i + 1}/{page_count}" if include_page_count else ""
    )

    # '-#' displays as subtext (smaller font and less visible colour) whilst
    # still allowing the use of other markdown formatting and relative timestamps
    # unlike the embed's footer.
    embed.description += (
        f"\n\n-# Easy: {DifficultyScore.EASY.value} point, Medium: "
        f"{DifficultyScore.MEDIUM.value} points, Hard: {DifficultyScore.HARD.value} "
        f"points"
        f"\n-# Updated on {last_updated_start} - {last_updated_end}"
        f"{page_count_text}"
    )

    return embed
