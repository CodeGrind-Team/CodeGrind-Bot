import io
import os
from datetime import datetime
from typing import TYPE_CHECKING

import aiohttp
import discord
import requests

from constants import StatsCardExtensions
from database.models import Record, Submissions, User
from utils.common import to_thread
from utils.problems import UserStats, fetch_problems_solved_and_rank

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


async def update_stats(
    bot: "DiscordBot",
    client_session: aiohttp.ClientSession,
    user: User,
    daily_reset: bool = False,
) -> None:
    """
    Update a user's problem-solving statistics and optionally store them as a record.

    This function fetches updated statistics for a user, assigns the new values to the
    user's submission statistics, and optionally creates a record with the updated
    stats.

    :param user: The user whose stats are being updated.
    :param daily_reset: If `True`, a new record is created and stored with the updated
    stats.
    """

    stats: UserStats = await fetch_problems_solved_and_rank(
        bot, client_session, user.leetcode_id
    )

    if not stats:
        return

    user = await User.find_one(User.id == user.id)

    (
        user.stats.submissions.easy,
        user.stats.submissions.medium,
        user.stats.submissions.hard,
        user.stats.submissions.score,
    ) = (
        stats.submissions.easy,
        stats.submissions.medium,
        stats.submissions.hard,
        stats.submissions.score,
    )

    if daily_reset:
        record = Record(
            timestamp=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            user_id=user.id,
            submissions=Submissions(
                easy=stats.submissions.easy,
                medium=stats.submissions.medium,
                hard=stats.submissions.hard,
                score=stats.submissions.score,
            ),
        )

        await record.create()

    await user.save_changes()


@to_thread
def stats_card(
    bot: "DiscordBot",
    leetcode_id: str,
    display_name: str,
    extension: StatsCardExtensions,
) -> tuple[discord.File | None]:
    width = 500
    height = 200
    if extension in (StatsCardExtensions.ACTIVITY, StatsCardExtensions.CONTEST):
        height = 400
    elif extension == StatsCardExtensions.HEATMAP:
        height = 350

    url = f"""https://leetcard.jacoblin.cool/{leetcode_id}?theme=dark&animation=false&
    width={width}&height={height}&ext={extension.value}"""

    # Making sure the website is reachable before running hti.screenshot()
    # as the method will stall if url isn't reachable.
    try:
        response = requests.get(url)
        response.raise_for_status()

    except requests.exceptions.RequestException:
        return

    paths = bot.html2image.screenshot(url=url, size=(width, height))

    with open(paths[0], "rb") as f:
        # read the file contents
        data = f.read()
        # create a BytesIO object from the data
        image_binary = io.BytesIO(data)
        # move the cursor to the beginning
        image_binary.seek(0)

        file = discord.File(fp=image_binary, filename=f"{leetcode_id}.png")

    os.remove(paths[0])

    return file
