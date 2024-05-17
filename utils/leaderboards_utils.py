from datetime import UTC, datetime, timedelta

import discord
from beanie.odm.operators.update.array import AddToSet
from discord.ext import commands

from constants import GLOBAL_LEADERBOARD_ID, Period, RankEmoji
from database.models.preference_model import Preference
from database.models.record_model import Record
from database.models.server_model import Server
from database.models.user_model import User
from embeds.leaderboards_embeds import empty_leaderboard_embed, leaderboard_embed
from utils.common_utils import strftime_with_suffix
from views.leaderboard_view import LeaderboardPagination


async def get_score(period: Period, user: User) -> int:
    """
    Get the score for a given period for a user.

    :param period: The period for which to retrieve the score.
    :param user_id: The ID of the user to retrieve the score for.

    :return: The calculated score for the specified period.
    """

    current_score = user.stats.submissions.score
    record_timestamp: datetime | None = None

    match period:
        case Period.DAY:
            # Midnight today
            record_timestamp = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        case Period.WEEK:
            # Midnight of the current week's start (Monday)
            current_day = datetime.now().weekday()
            record_timestamp = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=current_day)

        case Period.MONTH:
            # Midnight of the first day of the current month
            record_timestamp = datetime.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

        case Period.ALLTIME:
            return current_score

    # If a timestamp is defined, find the record starting from that time
    if record_timestamp:
        record = await Record.find_one(
            Record.user_id == user.id,
            Record.timestamp >= record_timestamp,
            sort=Record.timestamp,
        )

        if not record:
            return 0

        previous_score = record.submissions.score
        return current_score - previous_score

    return 0


async def generate_leaderboard_embed(
    period: Period,
    server_id: int,
    author_user_id: int | None = None,
    winners_only: bool = False,
    global_leaderboard: bool = False,
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
    :param page: The page number.
    :param users_per_page: The number of users per page.

    :return: The leaderboard embed and view.
    """
    server = await Server.find_one(Server.id == server_id, fetch_links=True)

    if not server:
        return empty_leaderboard_embed(), None

    sorted_users: list[User] = sorted(
        server.users, key=lambda user: get_score(period, user), reverse=True
    )

    pages: list[discord.Embed] = []
    num_pages = -(-len(server.users) // users_per_page)

    place = 0
    prev_score = float("-inf")

    for page_index in range(num_pages):
        page, place, prev_score = await build_leaderboard_page(
            period,
            server,
            sorted_users,
            winners_only,
            global_leaderboard,
            page_index,
            users_per_page,
            num_pages,
            place,
            prev_score,
        )
        pages.append(page)

    if len(pages) == 0:
        embed = empty_leaderboard_embed()
        pages.append(embed)

    page = page - 1 if page > 0 else 0
    view = None if winners_only else LeaderboardPagination(author_user_id, pages, page)

    return pages[page], view


async def build_leaderboard_page(
    period: Period,
    server: Server,
    sorted_users: list[User],
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

    for user in sorted_users[
        page_index * users_per_page : page_index * users_per_page + users_per_page
    ]:

        profile_link = f"https://leetcode.com/{user.leetcode_username}"

        # ? Check if this is possible or if dbref needs to be
        # ? specified on the id
        preference = await Preference.find_one(
            Preference.user_id == user.id, Preference.server_id == server.id
        )

        if not preference:
            continue

        name = preference.name
        url = preference.url
        visible = preference.visible
        score = await get_score(period, user.id)

        if score != prev_score:
            place += 1

        if winners_only and (score == 0 or place == 4):
            break

        prev_score = score

        display_name = (
            "Anonymous User"
            if not visible and global_leaderboard
            else (f"[{name}]({profile_link})" if url else name)
        )

        rank = get_rank_emoji(place, score)
        leaderboard.append(f"**{rank} {display_name}** - **{score}** pts")

    title = get_title(period, winners_only, global_leaderboard)

    return (
        leaderboard_embed(server, page_index, num_pages, title, leaderboard),
        place,
        prev_score,
    )


def get_title(period: Period, winners_only: bool, global_leaderboard: bool) -> str:
    """
    Get the title of the leaderboard.

    :param period: The period.
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
    time_interval_text = ""

    if period == Period.DAY:
        time_interval_text = strftime_with_suffix(
            "{S} %b %Y", datetime.now() - timedelta(days=1)
        )
        return f"Today's Winners ({time_interval_text})"

    elif period == Period.WEEK:
        start_timestamp = strftime_with_suffix(
            "{S} %b %Y", datetime.now(UTC) - timedelta(weeks=1)
        )
        end_timestamp = strftime_with_suffix(
            "{S} %b %Y", datetime.now(UTC) - timedelta(days=1)
        )
        return f"Last Week's Winners ({start_timestamp} - {end_timestamp})"

    elif period == Period.MONTH:
        start_timestamp = strftime_with_suffix(
            "{S} %b %Y", (datetime.now(UTC) - timedelta(days=1)).replace(day=1)
        )
        end_timestamp = strftime_with_suffix(
            "{S} %b %Y", datetime.now(UTC) - timedelta(days=1)
        )
        return f"Last Month's Winners ({start_timestamp} - {end_timestamp})"


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
                return RankEmoji.FIRST
            case 2:
                return RankEmoji.SECOND
            case 3:
                return RankEmoji.THIRD

    return f"{place}\."  # noqa: W605


async def send_leaderboard_winners(
    bot: commands.Bot, server: Server, period: Period
) -> None:
    """
    Send the leaderboard winners to the specified channels on a Discord server.

    This function sends the leaderboard winners' embed to a list of specified channels
    within a given Discord server. It checks each channel to ensure it's valid and a
    text channel, and handles forbidden (permission-related) errors when attempting to
    send the embed.

    :param bot: The Discord bot instance used to get the channels and send messages.
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
                period, server.id, winners_only=True
            )

            await channel.send(embed=embed, view=view)

        except discord.errors.Forbidden as e:
            bot.logger.exception(
                "file: utils/leaderboards_utils.py ~ send_leaderboard_winners ~ \
                    missing permissions on channel id %s. Error: %s",
                channel.id,
                e,
            )

    bot.logger.info(
        "file: utils/leaderboards_utils.py ~ send_leaderboard_winners ~ %s winners \
            leaderboard sent to channels",
        period,
    )


async def update_global_leaderboard() -> None:
    """
    Add all users to the global server in case anyone is missing.
    """
    async for user in User.all():
        await Server.find_one(Server.id == GLOBAL_LEADERBOARD_ID).update(
            AddToSet({Server.users: user})
        )
