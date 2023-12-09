from collections import Counter
from datetime import datetime, timedelta

import discord
from beanie.odm.operators.update.array import AddToSet
from bson import DBRef

from bot_globals import RANK_EMOJI, TIMEFRAME_TITLE, client, logger
from database.models.server_model import Server
from database.models.user_model import User
from embeds.leaderboards_embeds import (empty_leaderboard_embed,
                                        leaderboard_embed)
from utils.common_utils import strftime_with_suffix
from views.leaderboard_view import LeaderboardPagination


def get_score(user: User, timeframe: str | None = None) -> int:
    if timeframe == "alltime":
        return user.submissions.total_score

    else:
        if timeframe == "daily":
            return user.scores.day_score

        elif timeframe == "weekly":
            return user.scores.week_score

        elif timeframe == "yesterday":
            return user.scores.yesterday_score

        elif timeframe == "last_week":
            return user.scores.last_week_score

        elif timeframe == "start_of_week_total":
            start_of_week_total_score = user.scores.start_of_week_total_score
            return start_of_week_total_score if start_of_week_total_score is not None else user.submissions.total_score

        elif timeframe == "start_of_day_total":
            start_of_day_total_score = user.scores.start_of_day_total_score
            return start_of_day_total_score if start_of_day_total_score is not None else user.submissions.total_score


async def display_leaderboard(send_message, server_id: int = 0, user_id: int | None = None, timeframe: str = "alltime", page: int = 1, winners_only: bool = False, users_per_page: int = 10, global_leaderboard: bool = False) -> None:
    logger.info(
        "file: cogs/leaderboards.py ~ display_leaderboard ~ run ~ guild id: %s", server_id)

    # TODO: Project
    # Server ID of 0 is the global leaderboard
    server = await Server.find_one(Server.id == server_id, fetch_links=True)

    if not server:
        embed = empty_leaderboard_embed()
        await send_message(embed=embed)
        return

    users = sorted(server.users,
                   key=lambda user: get_score(user, timeframe), reverse=True)

    user_to_wins = Counter(
        rankings.winner for rankings in server.rankings if rankings.timeframe == timeframe)

    pages = []
    page_count = -(-len(users)//users_per_page)

    place = 0
    prev_score = float("-inf")
    reached_end_of_winners = False

    for page_i in range(page_count):
        leaderboard = []

        for user in users[page_i * users_per_page: page_i * users_per_page + users_per_page]:
            profile_link = f"https://leetcode.com/{user.leetcode_username}"

            display_information = next(
                (di for di in user.display_information if di.server_id == server_id), None)

            if not display_information:
                continue

            name = display_information.name
            url = display_information.url
            private = display_information.private
            total_score = get_score(user, timeframe)

            if winners_only and (total_score == 0 or place == 3):
                reached_end_of_winners = True
                break

            if total_score != prev_score:
                place += 1

            prev_score = total_score

            number_rank = f"{place}\."

            display_name = "Private User" if private and global_leaderboard else (
                f"[{name}]({profile_link})"if url else name)

            wins = user_to_wins[user.id]

            wins_text = f"({str(wins)} wins) "
            # wins won't be displayed for alltime timeframe as wins !> 0
            leaderboard.append(
                f"**{RANK_EMOJI[place] if place in RANK_EMOJI and total_score != 0 else number_rank} {display_name}** {wins_text if  wins > 0 else ''}- **{total_score}** pts"
            )

        title = f"{'Global ' if global_leaderboard else ''}{TIMEFRAME_TITLE[timeframe]['title']} Leaderboard"
        if winners_only:
            if timeframe == "yesterday":
                title = f"{TIMEFRAME_TITLE[timeframe]['title']} Winners ({strftime_with_suffix('{S} %b %Y', datetime.utcnow() - timedelta(days=1))})"

            elif timeframe == "last_week":
                title = f"{TIMEFRAME_TITLE[timeframe]['title']} Winners ({strftime_with_suffix('{S} %b %Y', datetime.utcnow() - timedelta(days=7))} - {strftime_with_suffix('{S} %b %Y', datetime.utcnow() - timedelta(days=1))})"

        embed = leaderboard_embed(
            server, page_i, page_count, title, leaderboard)
        pages.append(embed)

        if reached_end_of_winners:
            break

    if len(pages) == 0:
        embed = empty_leaderboard_embed()
        pages.append(embed)

    page = page - 1 if page > 0 else 0
    view = None if winners_only else LeaderboardPagination(
        user_id, pages, page)

    try:
        await send_message(embed=pages[page], view=view)
    except discord.errors.Forbidden as e:
        logger.exception(
            "file: utils/leaderboards_utils.py ~ display_leaderboard ~ missing permissions on server id %s. Error: %s", server_id, e)


async def send_leaderboard_winners(server: Server, timeframe: str) -> None:
    for channel_id in server.channels.winners:
        channel = client.get_channel(channel_id)

        if not channel or not isinstance(channel, discord.TextChannel):
            continue

        try:
            await display_leaderboard(channel.send, server.id, timeframe=timeframe, winners_only=True)
        except discord.errors.Forbidden as e:
            logger.exception(
                "file: utils/leaderboards_utils.py ~ send_leaderboard_winners ~ missing permissions on channel id %s. Error: %s", channel.id, e)

    logger.info(
        "file: utils/leaderboards_utils.py ~ send_leaderboard_winners ~ %s winners leaderboard sent to channels", timeframe)


async def update_global_leaderboard() -> None:
    """Add all users to the global server in case anyone is missing.
    """
    async for user in User.all():
        await Server.find_one(Server.id == 0).update(AddToSet({Server.users: DBRef("users",  user.id)}))
