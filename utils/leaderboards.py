import os
from datetime import datetime, timedelta

import discord
import pytz

from bot_globals import RANK_EMOJI, TIMEFRAME_TITLE, TIMEZONE, client, logger
from embeds.leaderboards_embeds import (empty_leaderboard_embed,
                                        leaderboard_embed)
from models.server_model import Server
from models.user_model import User
from utils.views import Pagination


def get_score(server: Server, user: User, timeframe: str) -> int:
    if timeframe == "alltime":
        return user.submissions.total_score

    else:
        score = next(
            (score for score in user.scores if score.timezone == server.timezone), None)

        if not score:
            return 0

        if timeframe == "daily":
            return score.today_score

        elif timeframe == "weekly":
            return score.week_score


async def display_leaderboard(send_message, server_id, user_id=None, timeframe: str = "alltime", page: int = 1, winners_only: bool = False, users_per_page: int = 10) -> None:
    logger.info(
        "file: cogs/leaderboards.py ~ display_leaderboard ~ run ~ guild id: %s", server_id)

    # TODO: Project
    server = await Server.find_one(Server.id == server_id, fetch_links=True)

    if not server:
        embed = empty_leaderboard_embed()
        await send_message(embed=embed)
        return

    users = sorted(server.users,
                   key=lambda user: get_score(server, user, timeframe), reverse=True)

    if winners_only:
        users = users[:3]

    pages = []
    page_count = -(-len(users)//users_per_page)

    for page_i in range(page_count):
        leaderboard = []

        for lb_rank, user in enumerate(users[page_i * users_per_page: page_i * users_per_page + users_per_page], start=page_i * users_per_page + 1):
            profile_link = f"https://leetcode.com/{user.leetcode_username}"

            display_information = next(
                (di for di in user.display_information if di.server_id == server_id), None)

            if not display_information:
                continue

            name = display_information.name
            hyperlink = display_information.hyperlink
            total_score = get_score(server, user, timeframe)

            number_rank = f"{lb_rank}\."
            name_with_link = f"[{name}]({profile_link})"

            wins = 0

            # if timeframe == "daily":
            #     wins = sum(
            #         rank == 1 for rank in stats['daily_rankings'].values())

            # elif timeframe == "weekly":
            #     wins = sum(
            #         rank == 1 for rank in stats['weekly_rankings'].values())

            wins_text = f"({str(wins)} wins) "
            # wins won't be displayed for alltime timeframe as wins !> 0
            leaderboard.append(
                f"**{RANK_EMOJI[lb_rank] if lb_rank in RANK_EMOJI else number_rank} {name_with_link if hyperlink else name}** {wins_text if  wins > 0 else ''}- **{total_score}** pts"
            )

        title = f"{TIMEFRAME_TITLE[timeframe]['title']} Leaderboard"
        if winners_only:
            if timeframe == "yesterday":
                title = f"{TIMEFRAME_TITLE[timeframe]['title']} Winners ({(datetime.now(TIMEZONE) - timedelta(days=1)).strftime('%d/%m/%Y')})"

            elif timeframe == "last_week":
                title = f"{TIMEFRAME_TITLE[timeframe]['title']} Winners ({(datetime.now(TIMEZONE) - timedelta(days=7)).strftime('%d/%m/%Y')} - {(datetime.now(TIMEZONE) - timedelta(days=1)).strftime('%d/%m/%Y')})"

        embed = leaderboard_embed(
            server, page_i, page_count, title, leaderboard)
        pages.append(embed)

    if len(pages) == 0:
        embed = empty_leaderboard_embed()
        pages.append(embed)

    page = page - 1 if page > 0 else 0
    view = None if winners_only else Pagination(user_id, pages, page)
    await send_message(embed=pages[page], view=view)


async def send_leaderboard_winners(timeframe: str) -> None:
    for filename in os.listdir("./data"):
        if filename.endswith(".json"):
            server_id = int(filename.split("_")[0])

            data = await read_file(f"data/{server_id}_leetcode_stats.json")

            if "channels" in data:
                for channel_id in data["channels"]:
                    channel = client.get_channel(channel_id)

                    if not isinstance(channel, discord.TextChannel):
                        continue

                    await display_leaderboard(channel.send, server_id, timeframe=timeframe, winners_only=True, users_per_page=3)

    logger.info(
        "file: utils/leaderboards.py ~ send_leaderboard_winners ~ %s winners leaderboard sent to channels", timeframe)
