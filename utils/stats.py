import asyncio
import io
import os
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import discord
import requests
from beanie.odm.operators.update.general import Inc
from beanie.operators import In
from PIL import Image, UnidentifiedImageError

from constants import Period, StatsCardExtensions
from database.models import (
    LanguageProblemCount,
    Profile,
    Record,
    Server,
    SkillProblemCount,
    SkillsProblemCount,
    Submissions,
    User,
)
from utils.common import to_thread
from utils.leaderboards import all_users_and_scores
from utils.problems import fetch_problems_solved_and_rank

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


async def update_stats(
    bot: "DiscordBot",
    user: User,
    reset_day: bool = False,
) -> None:
    """
    Update a user's problem-solving statistics and optionally store them as a record.

    This function fetches updated statistics for a user, assigns the new values to the
    user's submission statistics, and optionally creates a record with the updated
    stats.

    :param user: The user whose stats are being updated.
    :param reset_day: If `True`, a new record is created and stored with the updated
    stats.
    """

    stats = await fetch_problems_solved_and_rank(bot, user.leetcode_id)
    if not stats:
        return

    user = await User.find_one(User.id == user.id)
    if not user:
        return

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

    if reset_day:
        languages_problem_count = list(
            map(
                lambda x: LanguageProblemCount(
                    language=x.language, count=x.problem_count
                ),
                stats.languages_problem_count,
            )
        )

        skills_problem_count = SkillsProblemCount(
            fundamental=list(
                map(
                    lambda x: SkillProblemCount(skill=x.skill, count=x.problem_count),
                    stats.skills_problem_count.fundamental,
                )
            ),
            intermediate=list(
                map(
                    lambda x: SkillProblemCount(skill=x.skill, count=x.problem_count),
                    stats.skills_problem_count.intermediate,
                )
            ),
            advanced=list(
                map(
                    lambda x: SkillProblemCount(skill=x.skill, count=x.problem_count),
                    stats.skills_problem_count.advanced,
                )
            ),
        )

        record = Record(
            timestamp=datetime.now(UTC).replace(
                hour=0, minute=0, second=0, microsecond=0
            ),
            user_id=user.id,
            submissions=Submissions(
                easy=stats.submissions.easy,
                medium=stats.submissions.medium,
                hard=stats.submissions.hard,
                score=stats.submissions.score,
            ),
            languages_problem_count=languages_problem_count,
            skills_problem_count=skills_problem_count,
        )

        await record.create()

    user.last_updated = datetime.now(UTC)
    await user.save()


async def update_wins() -> None:
    """
    Update the win counts for all users in all servers.
    """
    all_users = await User.all().to_list()

    # Collect scores for all users in each period.
    user_to_score: dict[Period, dict[int, int]] = {}
    for period in {Period.DAY, Period.WEEK, Period.MONTH}:
        users_and_scores = await all_users_and_scores(all_users, period, previous=False)
        user_to_score[period] = {user.id: score for user, score in users_and_scores}

    async for server in Server.all():
        profiles = await Profile.find_many(Profile.server_id == server.id).to_list()
        users: list[int] = [profile.user_id for profile in profiles]

        # Update win counts for the profiles.
        for period, increment_field in (
            (Period.DAY, Profile.win_count.days),
            (Period.WEEK, Profile.win_count.weeks),
            (Period.MONTH, Profile.win_count.months),
        ):
            max_score = max(user_to_score[period][user] for user in users)
            winners = {
                user_id
                for user_id, score in user_to_score[period].items()
                if score == max_score
            }
            await Profile.find_many(
                Profile.server_id == server.id, In(User.id, winners)
            ).update(Inc({increment_field: 1}))


async def update_all_user_stats(bot: "DiscordBot", reset_day: bool = False) -> None:
    """
    Update stats for all users.

    :param reset_day: Whether the day needs resetting.
    """
    await update_wins()

    counter = 0
    tasks = []
    async for user in User.all():
        task = asyncio.create_task(update_stats(bot, user, reset_day))
        tasks.append(task)

    total_users = len(tasks)
    for completed_task in asyncio.as_completed(tasks):
        await completed_task
        counter += 1
        if counter % 200 == 0 or counter == total_users:
            bot.logger.info(f"{counter} / {total_users} users stats updated")

    bot.logger.info("All users stats updated")


@to_thread
def stats_card(
    bot: "DiscordBot",
    leetcode_id: str,
    filename: str,
    extension: StatsCardExtensions,
    display_url: bool,
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

    if not display_url:
        anonymise_stats_card(bot, paths[0])

    with open(paths[0], "rb") as f:
        # read the file contents
        data = f.read()
        # create a BytesIO object from the data
        image_binary = io.BytesIO(data)
        # move the cursor to the beginning
        image_binary.seek(0)

        file = discord.File(fp=image_binary, filename=f"{filename}.png")

    os.remove(paths[0])

    return file


def anonymise_stats_card(bot: "DiscordBot", path: str) -> None:
    """
    Anonymise the stats card at the given path using Pillow (PIL).

    This function modifies any given stats card to remove the user's
    LeetCode ID from the image if they want to be anonymous.

    :param path: The path to the stats card image.
    """
    try:
        stats_card = Image.open(path)
        hidden_banner = Image.open("ui/assets/stats_card_hidden_banner.png")
        region = hidden_banner.crop((0, 0, 435, 30))
        stats_card.paste(region, (60, 20, 495, 50))
        stats_card.save(path)

    except UnidentifiedImageError as e:
        bot.logger.exception(
            f"An error occurred while opening or identifying the stats card image: {e}"
        )
