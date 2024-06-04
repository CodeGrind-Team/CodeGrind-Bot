import asyncio
import math
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import discord
from beanie.operators import In

from constants import GLOBAL_LEADERBOARD_ID, Period, RankEmoji
from database.models import Preference, Record, Server, User
from ui.embeds.leaderboards import empty_leaderboard_embed, leaderboard_embed
from ui.views.leaderboards import LeaderboardPagination
from utils.common import strftime_with_suffix

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


async def get_score(user: User, period: Period, previous: bool) -> int:
    """
    Get the score for a given period for a user.

    :param user: The user to retrieve the score for.
    :param period: The period for which to retrieve the score.
    :param previous: Whether to get the score for the previous period.

    :return: The calculated score for the specified period.
    """

    if period == Period.ALLTIME:
        return user.stats.submissions.score

    record_timestamp_end: datetime | None = None
    record_timestamp_start: datetime | None = None

    # Determine the start and end timestamps based on the specified period
    match period:
        case Period.DAY:
            # Midnight today
            record_timestamp_end = datetime.now(UTC).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            record_timestamp_start = record_timestamp_end - timedelta(days=1)

        case Period.WEEK:
            # Midnight of the current week's start (Monday)
            record_timestamp_end = datetime.now(UTC).replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=datetime.now(UTC).weekday())
            record_timestamp_start = record_timestamp_end - timedelta(weeks=1)

        case Period.MONTH:
            # Midnight of the first day of the current month
            record_timestamp_end = datetime.now(UTC).replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            record_timestamp_start = (record_timestamp_end - timedelta(days=1)).replace(
                day=1
            )

    if previous:
        record_end = await Record.find_one(
            Record.user_id == user.id,
            Record.timestamp == record_timestamp_end,
        )
        if not record_end:
            return 0

        record_start = await Record.find_one(
            Record.user_id == user.id,
            Record.timestamp >= record_timestamp_start,
            Record.timestamp < record_timestamp_end,
        )
        if not record_start:
            return 0

        score_end = record_end.submissions.score
        score_start = record_start.submissions.score
        return score_end - score_start

    else:
        current_score = user.stats.submissions.score
        record = await Record.find_one(
            Record.user_id == user.id,
            Record.timestamp >= record_timestamp_end,
        )
        if not record:
            return 0

        previous_score = record.submissions.score
        return current_score - previous_score


async def get_user_and_score(
    user: User, period: Period, previous: bool
) -> tuple[User, int]:
    """
    Get the score for a given period for a user.

    :param period: The period for which to retrieve the score.
    :param user_id: The ID of the user to retrieve the score for.
    :param previous: Whether to display the leaderboard of one period before.

    :return: A tuple of the user and their score.
    """
    score = await get_score(user, period, previous)
    return user, score


async def sort_users_by_score(
    users: list[User], period: Period, previous: bool
) -> list[User]:
    """
    Sort the users on a server by their score for a given period.

    :param users: The users in the server.
    :param period: The period for which to retrieve and sort the scores.
    :param previous: Whether to display the leaderboard of one period before.

    :return: A list of users sorted by their score in descending order.
    """
    coroutines = [get_user_and_score(user, period, previous) for user in users]
    users_with_scores = await asyncio.gather(*coroutines)
    sorted_users_with_score = sorted(
        users_with_scores, key=lambda pair: pair[1], reverse=True
    )

    return sorted_users_with_score


async def get_users_from_preferences(
    server_id: int,
) -> tuple[dict[int, Preference], list[User]]:
    """
    Retrieves the users that are part of a server, and their respective preferences.

    :param server_id: the server to retrieve the users that are in it.
    """
    preferences = await Preference.find_many(
        Preference.server_id == server_id
    ).to_list()

    user_id_to_preference = {
        preference.user_id: preference for preference in preferences
    }

    users = await User.find_many(
        In(User.id, set(user_id_to_preference.keys()))
    ).to_list()

    return user_id_to_preference, users


async def generate_leaderboard_embed(
    period: Period,
    server_id: int,
    author_user_id: int | None = None,
    winners_only: bool = False,
    global_leaderboard: bool = False,
    previous: bool = False,
    page: int = 1,
    users_per_page: int = 10,
) -> tuple[discord.Embed, discord.ui.View]:
    """
    Generate a leaderboard embed.

    :param period: The period.
    :param server_id: The server's id.
    :param author_user_id: The author's user ID.
    :param winners_only: Whether to display only the winners.
    :param global_leaderboard: Whether to display the global leaderboard.
    :param previous: Whether to display the leaderboard of one period before.
    :param page: The page number.
    :param users_per_page: The number of users per page.

    :return: The leaderboard embed and view.
    """
    server_id = server_id if not global_leaderboard else GLOBAL_LEADERBOARD_ID
    server = await Server.find_one(Server.id == server_id, fetch_links=True)

    if not server:
        return empty_leaderboard_embed(), None

    user_id_to_preference, users = await get_users_from_preferences(server_id)
    sorted_users_with_score = await sort_users_by_score(users, period, previous)

    pages: list[discord.Embed] = []
    num_pages = math.ceil(len(users) / users_per_page)

    place = 0
    prev_score = float("-inf")

    for page_index in range(num_pages):
        page_embed, place, prev_score = await build_leaderboard_page(
            period,
            server,
            user_id_to_preference,
            sorted_users_with_score,
            winners_only,
            global_leaderboard,
            page_index,
            users_per_page,
            num_pages,
            place,
            prev_score,
        )
        pages.append(page_embed)

    if len(pages) == 0:
        embed = empty_leaderboard_embed()
        pages.append(embed)

    page = max(page - 1, 0)
    view = None if winners_only else LeaderboardPagination(author_user_id, pages, page)

    return pages[page], view


async def build_leaderboard_page(
    period: Period,
    server: Server,
    user_id_to_preference: list[dict[int, Preference]],
    sorted_users: list[tuple[User, int]],
    winners_only: bool,
    global_leaderboard: bool,
    page_index: int,
    users_per_page: int,
    num_pages: int,
    place: int,
    prev_score: float,
) -> tuple[discord.Embed, int, float]:
    """
    Build a leaderboard page.

    :param period: The period.
    :param server: The server.
    :param sorted_users: The list of users sorted by score in the respective period.
    :param winners_only: Whether to display only the winners.
    :param global_leaderboard: Whether to display the global leaderboard.
    :param page_index: The page index.
    :param users_per_page: The number of users per page.
    :param num_pages: The number of pages.
    :param place: The place.
    :param prev_score: The previous score.

    :return: The leaderboard page, place, and previous score.
    """

    leaderboard = []

    for user, score in sorted_users[
        page_index * users_per_page : page_index * users_per_page + users_per_page
    ]:

        profile_link = f"https://leetcode.com/{user.leetcode_id}"

        preference = user_id_to_preference[user.id]

        if not preference:
            # ! would actually lead to error. Assert
            continue

        name = preference.name
        url = preference.url
        anonymous = preference.anonymous

        if score != prev_score:
            place += 1

        if winners_only and (score == 0 or place == 4):
            break

        prev_score = score

        display_name = (
            "Anonymous User"
            if anonymous and global_leaderboard
            else (f"[{name}]({profile_link})" if url else name)
        )

        rank = get_rank_emoji(place, score)
        leaderboard.append(f"**{rank} {display_name}** - **{score}** pts")

    title = get_title(period, winners_only, global_leaderboard)

    return (
        leaderboard_embed(
            server,
            page_index,
            num_pages,
            title,
            "\n".join(leaderboard),
            include_page_count=not winners_only,
        ),
        place,
        prev_score,
    )


def get_title(period: Period, winners_only: bool, global_leaderboard: bool) -> str:
    """
    Get the title of the leaderboard.

    :param period: The leaderboard's period.
    :param winners_only: Whether to display only the winners.
    :param global_leaderboard: Whether to display the global leaderboard.

    :return: The title of the leaderboard.
    """
    period_to_text = {
        Period.DAY: "daily",
        Period.WEEK: "weekly",
        Period.MONTH: "monthly",
        Period.ALLTIME: "allTime",
    }

    title = (
        f"{'Global ' if global_leaderboard else ''}"
        + f"{period_to_text[period].capitalize()} Leaderboard"
    )

    if winners_only:
        title = get_winners_title(period)

    return title


def get_winners_title(period: Period) -> str:
    """
    Get the title of the winners leaderboard.

    :param period: The period.

    :return: The title of the winners leaderboard.
    """
    title = ""

    match period:
        case Period.DAY:
            time_interval_text = strftime_with_suffix(
                "{S} %b %Y", datetime.now(UTC) - timedelta(days=1)
            )
            title = f"Today's Winners ({time_interval_text})"

        case Period.WEEK:
            start_timestamp = strftime_with_suffix(
                "{S} %b %Y", datetime.now(UTC) - timedelta(weeks=1)
            )
            end_timestamp = strftime_with_suffix(
                "{S} %b %Y", datetime.now(UTC) - timedelta(days=1)
            )
            title = f"This Week's Winners ({start_timestamp} - {end_timestamp})"

        case Period.MONTH:
            timestamp = strftime_with_suffix(
                "%b", (datetime.now(UTC) - timedelta(days=1)).replace(day=1)
            )

            title = f"This Month's Winners ({timestamp})"

    return title


def get_rank_emoji(place: int, score: int) -> str:
    """
    Get the rank emoji for a user.

    :param place: The user's place.
    :param score: The user's score.

    :return: The rank emoji.
    """
    if score != 0:
        match place:
            case 1:
                return RankEmoji.FIRST.value
            case 2:
                return RankEmoji.SECOND.value
            case 3:
                return RankEmoji.THIRD.value

    return f"{place}\."  # noqa: W605


async def send_leaderboard_winners(
    bot: "DiscordBot", server: Server, period: Period
) -> None:
    """
    Send the leaderboard winners to the specified channels on a Discord server.

    Sends the leaderboard winners' embed to a list of specified channels
    within a given Discord server. It checks each channel to ensure it's valid and a
    text channel, and handles forbidden (permission-related) errors when attempting to
    send the embed.

    :param server: The server instance containing the list of channel IDs where the
    leaderboard winners will be announced.
    :param period: The period for which the leaderboard is being sent (e.g., weekly,
    monthly).
    """

    for channel_id in server.channels.winners:
        channel = bot.get_channel(channel_id)

        if not channel or not isinstance(channel, discord.TextChannel):
            continue

        try:
            embed, view = await generate_leaderboard_embed(
                period, server.id, winners_only=True, previous=True
            )

            await channel.send(embed=embed, view=view, silent=True)

        except discord.errors.Forbidden:
            bot.logger.exception(
                f"Missing permissions on channel ({channel_id}) to send leaderboard "
                "winners."
            )
