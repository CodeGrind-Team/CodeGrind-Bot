import asyncio
import math
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import discord
from beanie.operators import In

from constants import GLOBAL_LEADERBOARD_ID, Period, LeaderboardSortBy, RankEmoji
from database.models import Profile, Record, Server, User
from ui.embeds.leaderboards import empty_leaderboard_embed, leaderboard_embed
from ui.views.leaderboards import LeaderboardPagination

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


async def user_score(user: User, period: Period, previous: bool) -> int:
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


async def user_win_count(user: User, period: Period, server_id: int) -> int:
    """
    Returns the win count for a given period for a user.

    :param user: The user to retrieve the win count for.
    :param period: The period for which to retrieve the win count.
    :param server_id: The server to retrieve the win count for.

    :return: The win count for the specified period.
    """
    profile = await Profile.find_one(Profile.user_id == user.id, Profile.server_id == server_id)

    if not profile or not profile.win_count:
        return 0

    match period:
        case Period.DAY:
            return profile.win_count.days
        case Period.WEEK:
            return profile.win_count.weeks
        case Period.MONTH:
            return profile.win_count.months
        case _:
            return 0


async def user_score_and_wins(
    user: User, period: Period, previous: bool, server_id: int
) -> tuple[User, int, int]:
    """
    Get the score and wins for a given period for a user.

    :param period: The period for which to retrieve the score.
    :param user_id: The ID of the user to retrieve the score for.
    :param previous: Whether to display the leaderboard of one period before.
    :param server_id: The ID of the server to retrieve the score for.

    :return: A tuple of the user, their score and wins.
    """
    score = await user_score(user, period, previous)
    win_count = await user_win_count(user, period, server_id)

    return user, score, win_count


async def all_users_scores_and_wins(
    users: list[User], period: Period, previous: bool, server_id: int
) -> list[tuple[User, int, int]]:
    """
    Fetch and calculate the scores and wins for all users, for the selected time period.

    :param users: The users in the server.
    :param period: The period for which to retrieve and sort the scores.
    :param previous: Whether to display the leaderboard of one period before.
    :param server_id: The ID of the server to retrieve the score for.

    :return: A list of users with their scores and wins.
    """
    coroutines = [user_score_and_wins(user, period, previous, server_id) for user in users]
    users_with_scores_and_wins = await asyncio.gather(*coroutines)
    return users_with_scores_and_wins


async def users_from_profiles(
    server_id: int,
) -> tuple[dict[int, Profile], list[User]]:
    """
    Retrieves the users that are part of a server, and their respective profiles.

    :param server_id: the server to retrieve the users that are in it.
    """
    profiles = await Profile.find_many(Profile.server_id == server_id).to_list()

    user_id_to_profile = {profile.user_id: profile for profile in profiles}

    users = await User.find_many(In(User.id, set(user_id_to_profile.keys()))).to_list()

    return user_id_to_profile, users


async def generate_leaderboard_embed(
    period: Period,
    sort_by: LeaderboardSortBy,
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
    :param sort_by: Sorting method
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
    user_id_to_profile, users = await users_from_profiles(server_id)
    users_with_scores_and_wins = await all_users_scores_and_wins(users, period, previous, server_id)

    match sort_by:
        case LeaderboardSortBy.WIN_COUNT:
            sorted_users_with_metrics = sorted(
                users_with_scores_and_wins, key=lambda pair: pair[2], reverse=True
            )
        case _:
            sorted_users_with_metrics = sorted(
                users_with_scores_and_wins, key=lambda pair: pair[1], reverse=True
            )

    pages: list[discord.Embed] = []
    num_pages = math.ceil(len(users) / users_per_page)

    place = 0
    prev_metric_value = float("-inf")
    for page_index in range(num_pages):
        page_embed, place, prev_score = await build_leaderboard_page(
            period,
            sort_by,
            server,
            user_id_to_profile,
            sorted_users_with_metrics,
            winners_only,
            global_leaderboard,
            page_index,
            users_per_page,
            num_pages,
            place,
            prev_metric_value,
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
    sort_by: LeaderboardSortBy,
    server: Server,
    user_id_to_profile: list[dict[int, Profile]],
    sorted_users: list[tuple[User, int, int]],
    winners_only: bool,
    global_leaderboard: bool,
    page_index: int,
    users_per_page: int,
    num_pages: int,
    place: int,
    prev_metric_value: float,
) -> tuple[discord.Embed, int, float]:
    """
    Build a leaderboard page.

    :param period: The period.
    :param sort_by: Sorting method
    :param server: The server.
    :param user_id_to_profile: Mapping from user ids to their profile.
    :param sorted_users: The list of users sorted by selected metric (score or win count) in the respective period.
    :param winners_only: Whether to display only the winners.
    :param global_leaderboard: Whether to display the global leaderboard.
    :param page_index: The page index.
    :param users_per_page: The number of users per page.
    :param num_pages: The number of pages.
    :param place: The place.
    :param prev_metric_value: The previous metric value.

    :return: The leaderboard page, place, and previous metric value.
    """

    leaderboard = []

    for user, score, win_count in sorted_users[
        page_index * users_per_page : page_index * users_per_page + users_per_page
    ]:

        profile_link = f"https://leetcode.com/{user.leetcode_id}"

        profile = user_id_to_profile[user.id]

        if not profile:
            # ! would actually lead to error. Assert
            continue

        name = profile.preference.name
        url = profile.preference.url
        anonymous = profile.preference.anonymous

        match sort_by:
            case LeaderboardSortBy.WIN_COUNT:
                display_metric = win_count
                metric_label = "wins"
            case _:
                display_metric = score
                metric_label = "pts"

        if display_metric != prev_metric_value:
            place += 1

        if winners_only and (display_metric == 0 or place == 4):
            break

        prev_metric_value = display_metric

        display_name = (
            "Anonymous User"
            if anonymous and global_leaderboard
            else (f"[{name}]({profile_link})" if url else name)
        )

        rank = get_rank_emoji(place, display_metric)
        leaderboard.append(f"**{rank} {display_name}** - **{display_metric}** {metric_label}")

    title = get_title(period, winners_only, global_leaderboard, sort_by)

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
        prev_metric_value,
    )


def get_title(period: Period, winners_only: bool, global_leaderboard: bool, sort_by: LeaderboardSortBy) -> str:
    """
    Get the title of the leaderboard.

    :param period: The leaderboard's period.
    :param sort_by: Sorting method.
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

    metric_label = "Win Count" if sort_by == LeaderboardSortBy.WIN_COUNT else "Score"

    title = (
        f"{'Global ' if global_leaderboard else ''}"
        + f"{period_to_text[period].capitalize()} Leaderboard"
        + f" ({metric_label})"
    )

    if winners_only:
        title = get_winners_title(period)

    return title


def get_winners_title(period: Period) -> str:
    """
    Get the title of the winners leaderboard.
    The titles use the relative timestamp in the Long Date format: <t:{timestamp}:D>,
    except the month title which displays just the month and year.

    :param period: The period.

    :return: The title of the winners leaderboard.
    """
    title = ""
    time_now = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

    match period:
        case Period.DAY:
            time_interval_text = (
                f"<t:{int((time_now - timedelta(days=1)).timestamp())}:D>"
            )
            title = f"Today's Winners ({time_interval_text})"

        case Period.WEEK:
            start_timestamp = (
                f"<t:{int((time_now - timedelta(weeks=1)).timestamp())}:D>"
            )
            end_timestamp = f"<t:{int((time_now - timedelta(days=1)).timestamp())}:D>"
            title = f"This Week's Winners ({start_timestamp} - {end_timestamp})"

        case Period.MONTH:
            month_and_year = (
                (time_now - timedelta(days=1)).replace(day=1).strftime("%b %Y")
            )

            title = f"This Month's Winners ({month_and_year})"

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
