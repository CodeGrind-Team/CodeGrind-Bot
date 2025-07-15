import asyncio
import io
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import discord
from beanie.odm.operators.update.general import Inc, Set
from beanie.operators import In
from PIL import Image, UnidentifiedImageError
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import FloatRect

from src.constants import Period, StatsCardExtensions
from src.database.models import (
    LanguageProblemCount,
    Profile,
    Record,
    Server,
    SkillProblemCount,
    SkillsProblemCount,
    Submissions,
    User,
)
from src.utils.leaderboards import all_users_scores_and_wins
from src.utils.problems import fetch_problems_solved_and_rank

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot

stats_update_semaphore = asyncio.Semaphore(4)


async def update_stats(
    bot: "DiscordBot",
    db_user: User,
    reset_day: bool = False,
) -> None:
    """
    Update a user's problem-solving statistics and optionally store them as a record.

    This function fetches updated statistics for a user, assigns the new values to the
    user's submission statistics, and optionally creates a record with the updated
    stats.

    :param db_user: The user whose stats are being updated.
    :param reset_day: If `True`, a new record is created and stored with the updated
    stats.
    """

    async with stats_update_semaphore:
        stats = await fetch_problems_solved_and_rank(bot, db_user.leetcode_id)
        if not stats:
            return

        (
            db_user.stats.submissions.easy,
            db_user.stats.submissions.medium,
            db_user.stats.submissions.hard,
            db_user.stats.submissions.score,
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
                        lambda x: SkillProblemCount(
                            skill=x.skill, count=x.problem_count
                        ),
                        stats.skills_problem_count.fundamental,
                    )
                ),
                intermediate=list(
                    map(
                        lambda x: SkillProblemCount(
                            skill=x.skill, count=x.problem_count
                        ),
                        stats.skills_problem_count.intermediate,
                    )
                ),
                advanced=list(
                    map(
                        lambda x: SkillProblemCount(
                            skill=x.skill, count=x.problem_count
                        ),
                        stats.skills_problem_count.advanced,
                    )
                ),
            )

            record = Record(
                timestamp=datetime.now(UTC).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
                user_id=db_user.id,
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

        db_user.last_updated = datetime.now(UTC)
        await db_user.save()


async def update_wins(
    reset_day: bool = False,
    reset_week: bool = False,
    reset_month: bool = False,
) -> None:
    """
    Update the win counts for all users in all servers.
    """
    all_users = await User.all().to_list()

    # Map periods to their respective reset flags and increment fields.
    periods_and_resets = (
        (Period.DAY, reset_day, Profile.win_count.days),
        (Period.WEEK, reset_week, Profile.win_count.weeks),
        (Period.MONTH, reset_month, Profile.win_count.months),
    )

    # Collect scores of all users for each period.
    user_to_score: dict[Period, dict[int, int]] = {}
    for period, reset, _ in periods_and_resets:
        if not reset:
            continue

        users_and_scores = await all_users_scores_and_wins(
            all_users, period, previous=True
        )
        user_to_score[period] = {user.id: score for user, score, _ in users_and_scores}

    async for db_server in Server.all():
        db_profiles = await Profile.find_many(
            Profile.server_id == db_server.id
        ).to_list()
        user_ids: list[int] = [profile.user_id for profile in db_profiles]

        # Could occur for global server with ID 0. Prevents error from occurring when
        # max is used.
        if not user_ids:
            continue

        # Update win counts for the profiles.
        for period, reset, increment_field in periods_and_resets:
            if not reset:
                continue

            max_score = max(
                [
                    user_to_score[period][user]
                    for user in user_ids
                    if user in user_to_score[period]
                ]
            )
            # Scores of 0 don't count as a win.
            if max_score <= 0:
                continue

            winners = {
                user_id
                for user_id, score in user_to_score[period].items()
                if score == max_score
            }

            await Profile.find_many(
                Profile.server_id == db_server.id, In(Profile.user_id, winners)
            ).update(
                Inc({increment_field: 1}),
                Set({Profile.win_count.last_updated: datetime.now(UTC)}),
            )  # type: ignore


async def update_all_user_stats(
    bot: "DiscordBot",
    reset_day: bool = False,
    reset_week: bool = False,
    reset_month: bool = False,
) -> None:
    """
    Update stats for all users.

    :param reset_day: Whether the day needs resetting.
    """

    counter = 0
    tasks = []
    async for db_user in User.all():
        task = asyncio.create_task(update_stats(bot, db_user, reset_day))
        tasks.append(task)

    total_users = len(tasks)
    for completed_task in asyncio.as_completed(tasks):
        await completed_task
        counter += 1
        if counter % 200 == 0 or counter == total_users:
            bot.logger.info(f"{counter} / {total_users} users stats updated")

    bot.logger.info("All users stats updated")

    if reset_day or reset_week or reset_month:
        await update_wins(reset_day, reset_week, reset_month)
        bot.logger.info("All users wins updated")


async def stats_card(
    bot: "DiscordBot",
    leetcode_id: str,
    extension: StatsCardExtensions,
    display_url: bool,
) -> tuple[str, discord.File] | None:
    width = 500
    height = 200
    if extension in (StatsCardExtensions.ACTIVITY, StatsCardExtensions.CONTEST):
        height = 400
    elif extension == StatsCardExtensions.HEATMAP:
        height = 350

    url = f"""https://leetcard.jacoblin.cool/{leetcode_id}?theme=dark&animation=false&
    width={width}&height={height}&ext={extension.value}"""

    return await capture_stats_card(bot, display_url, url, width, height)


async def capture_stats_card(
    bot: "DiscordBot",
    display_url: bool,
    url: str,
    width: int,
    height: int,
) -> tuple[str, discord.File] | None:
    context = await bot.browser.new_context()
    try:
        page = await context.new_page()
        await page.goto(url)

        image_bytes = await page.screenshot(
            clip=FloatRect(x=0, y=0, width=width, height=height)
        )

    except PlaywrightError as e:
        bot.logger.exception(f"An error occurred while capturing the stats card: {e}")
        return

    finally:
        await context.close()

    screenshot_buffer = io.BytesIO(image_bytes)

    if not display_url:
        if not (
            anonymised_screenshot_buffer := anonymise_stats_card(bot, screenshot_buffer)
        ):
            return

        screenshot_buffer = anonymised_screenshot_buffer

    screenshot_buffer.seek(0)

    filename = str(uuid.uuid4())
    return filename, discord.File(fp=screenshot_buffer, filename=f"{filename}.png")


def anonymise_stats_card(
    bot: "DiscordBot", image_bytes: io.BytesIO
) -> io.BytesIO | None:
    """
    Anonymise the stats card at the given path using Pillow (PIL).

    This function modifies any given stats card to remove the user's
    LeetCode ID from the image if they want to be anonymous.

    :param image_bytes: The stats card image as a byte stream.
    """
    try:
        stats_card = Image.open(image_bytes)
        hidden_banner = Image.open("src/ui/assets/stats_card_hidden_banner.png")
        region = hidden_banner.crop((0, 0, 435, 30))
        stats_card.paste(region, (60, 20, 495, 50))

        output_buffer = io.BytesIO()
        stats_card.save(output_buffer, format="PNG")
        return output_buffer

    except UnidentifiedImageError as e:
        bot.logger.exception(
            f"An error occurred while opening or identifying the stats card image: {e}"
        )
