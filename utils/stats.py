import asyncio
from datetime import datetime, timedelta

from discord.ext import commands

from bot_globals import DIFFICULTY_SCORE, logger
from utils.io_handling import read_file, write_file
from utils.questions import get_problems_solved_and_rank


async def update_rankings(client: commands.Bot, now: datetime, daily_reset: bool = False, weekly_reset: bool = False) -> None:
    logger.info("file: cogs/stats.py ~ update_rankings ~ run ~ now: %s | daily reset: %s | weekly reset: %s",
                now.strftime("%d/%m/%Y, %H:%M:%S"), daily_reset, weekly_reset)

    if not daily_reset and not weekly_reset:
        logger.info(
            'file: cogs/stats.py ~ update_rankings ~ No rank updating required')
        return

    # retrieve every server the bot is in
    server_ids = [guild.id for guild in client.guilds]
    logger.info(
        'file: cogs/stats.py ~ update_rankings ~ server IDs: %s', server_ids)

    # for each server, retrieve the leaderboard
    for server_id in server_ids:
        logger.info(
            'file: cogs/stats.py ~ update_rankings ~ current server ID: %s', server_ids)
        # retrieve the keys from the json file
        data = await read_file(f"data/{server_id}_leetcode_stats.json")

        if data is not None:
            places = {}

            if daily_reset:
                today_score_sorted = sorted(data["users"].items(),
                                            key=lambda x: x[1]["yesterday_score"],
                                            reverse=True)

                for place, (discord_id, stats) in enumerate(today_score_sorted):
                    if discord_id not in places:
                        places[discord_id] = {}

                    places[discord_id]["daily_ranking"] = place + 1

            if weekly_reset:
                week_score_sorted = sorted(data["users"].items(),
                                           key=lambda x: x[1]["last_week_score"],
                                           reverse=True)

                for place, (discord_id, stats) in enumerate(week_score_sorted):
                    if discord_id not in places:
                        places[discord_id] = {}

                    places[discord_id]["weekly_ranking"] = place + 1

            for (discord_id, stats) in data["users"].items():
                if "daily_rankings" not in stats:
                    data["users"][discord_id]["daily_rankings"] = {}

                if "weekly_rankings" not in stats:
                    data["users"][discord_id]["weekly_rankings"] = {}

                if daily_reset:
                    data["users"][discord_id]["daily_rankings"][str(now.strftime(
                        "%d/%m/%Y"))] = places[discord_id]["daily_ranking"]

                if weekly_reset:
                    data["users"][discord_id]["weekly_rankings"][str(now.strftime(
                        "%d/%m/%Y"))] = places[discord_id]["weekly_ranking"]

                await write_file(f"data/{server_id}_leetcode_stats.json", data)

    logger.info(
        'file: cogs/stats.py ~ update_rankings ~ rankings updated successfully')


async def update_stats(client: commands.Bot, now: datetime, daily_reset: bool = False, weekly_reset: bool = False) -> None:
    logger.info("file: cogs/stats.py ~ update_stats ~ run ~ now: %s | daily_reset: %s | weekly_reset %s",
                now.strftime("%d/%m/%Y, %H:%M:%S"), daily_reset, weekly_reset)

    # retrieve every server the bot is in
    server_ids = [guild.id for guild in client.guilds]
    logger.info(
        'file: cogs/stats.py ~ update_stats ~ server IDs: %s', server_ids)

    # for each server, retrieve the leaderboard
    for server_id in server_ids:
        logger.info(
            'file: cogs/stats.py ~ update_stats ~ current server ID: %s', server_ids)

        data = await read_file(f"data/{server_id}_leetcode_stats.json")

        if data is not None:
            for (discord_id, stats) in data["users"].items():
                leetcode_username = stats["leetcode_username"]

                submissions_and_rank = get_problems_solved_and_rank(
                    leetcode_username)

                if submissions_and_rank is None:
                    continue

                rank = submissions_and_rank["profile"]["ranking"]

                easy_completed = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Easy"]
                medium_completed = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Medium"]
                hard_completed = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Hard"]
                total_questions_done = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["All"]

                total_score = easy_completed * \
                    DIFFICULTY_SCORE["easy"] + medium_completed * \
                    DIFFICULTY_SCORE["medium"] + \
                    hard_completed * DIFFICULTY_SCORE["hard"]

                # Due to this field is added after some users have already been added,
                # it needs to be created and set to an empty dictionary
                # TODO: replace this with a function to automatically fill in missing fields
                if "history" not in stats:
                    data["users"][discord_id]["history"] = {}

                if "week_score" not in stats:
                    data["users"][discord_id]["week_score"] = 0

                if weekly_reset:
                    start_of_last_week = now - \
                        timedelta(days=now.weekday() % 7) - timedelta(days=7)

                    last_week_score = 0
                    while start_of_last_week <= now:
                        start_of_last_week_date = start_of_last_week.strftime(
                            "%d/%m/%Y")
                        if str(start_of_last_week_date) not in stats["history"]:
                            start_of_last_week += timedelta(days=1)
                            continue

                        start_of_last_week_easy_completed = stats["history"][str(
                            start_of_last_week_date)]['easy']
                        start_of_last_week_medium_completed = stats["history"][str(
                            start_of_last_week_date)]['medium']
                        start_of_last_week_hard_completed = stats["history"][str(
                            start_of_last_week_date)]['hard']

                        start_of_last_week_score = start_of_last_week_easy_completed * \
                            DIFFICULTY_SCORE["easy"] + start_of_last_week_medium_completed * \
                            DIFFICULTY_SCORE["medium"] + \
                            start_of_last_week_hard_completed * \
                            DIFFICULTY_SCORE["hard"]

                        last_week_score = total_score - start_of_last_week_score
                        break

                    data["users"][discord_id]["last_week_score"] = last_week_score

                start_of_week = now - timedelta(days=now.weekday() % 7)

                week_score = 0
                while start_of_week <= now:
                    start_of_week_date = start_of_week.strftime("%d/%m/%Y")
                    if str(start_of_week_date) not in stats["history"]:
                        start_of_week += timedelta(days=1)
                        continue

                    start_of_week_easy_completed = stats["history"][str(
                        start_of_week_date)]['easy']
                    start_of_week_medium_completed = stats["history"][str(
                        start_of_week_date)]['medium']
                    start_of_week_hard_completed = stats["history"][str(
                        start_of_week_date)]['hard']

                    start_of_week_score = start_of_week_easy_completed * \
                        DIFFICULTY_SCORE["easy"] + start_of_week_medium_completed * \
                        DIFFICULTY_SCORE["medium"] + \
                        start_of_week_hard_completed * \
                        DIFFICULTY_SCORE["hard"]

                    week_score = total_score - start_of_week_score
                    break

                data["users"][discord_id]["week_score"] = week_score

                if daily_reset:
                    yesterday = (now - timedelta(days=1)).strftime("%d/%m/%Y")

                    yesterday_score = 0

                    if str(yesterday) in stats["history"]:
                        yesterday_easy_completed = stats["history"][str(
                            yesterday)]['easy']
                        yesterday_medium_completed = stats["history"][str(
                            yesterday)]['medium']
                        yesterday_hard_completed = stats["history"][str(
                            yesterday)]['hard']

                        start_of_yesterday_points = yesterday_easy_completed * \
                            DIFFICULTY_SCORE["easy"] + yesterday_medium_completed * \
                            DIFFICULTY_SCORE["medium"] + \
                            yesterday_hard_completed * \
                            DIFFICULTY_SCORE["hard"]

                        yesterday_score = total_score - start_of_yesterday_points

                    data["users"][discord_id]["yesterday_score"] = yesterday_score

                today = now.strftime("%d/%m/%Y")

                today_score = 0

                if str(today) in stats["history"]:
                    today_easy_completed = stats["history"][str(today)]['easy']
                    today_medium_completed = stats["history"][str(
                        today)]['medium']
                    today_hard_completed = stats["history"][str(today)]['hard']

                    start_of_day_points = today_easy_completed * \
                        DIFFICULTY_SCORE["easy"] + today_medium_completed * \
                        DIFFICULTY_SCORE["medium"] + \
                        today_hard_completed * \
                        DIFFICULTY_SCORE["hard"]

                    today_score = total_score - start_of_day_points

                data["users"][discord_id]["rank"] = rank
                data["users"][discord_id]["easy"] = easy_completed
                data["users"][discord_id]["medium"] = medium_completed
                data["users"][discord_id]["hard"] = hard_completed
                data["users"][discord_id]["total_questions_done"] = total_questions_done
                data["users"][discord_id]["total_score"] = total_score
                data["users"][discord_id]["today_score"] = today_score

                if str(now.strftime("%d/%m/%Y")) not in stats["history"]:
                    data["users"][discord_id]["history"][str(now.strftime("%d/%m/%Y"))] = {
                        "easy": easy_completed, "medium": medium_completed, "hard": hard_completed}

                data["last_updated"] = now.strftime("%d/%m/%Y %H:%M")

                # update the json file
                await write_file(f"data/{server_id}_leetcode_stats.json", data)

                logger.info(
                    'file: cogs/stats.py ~ update_stats ~ user stats updated successfully: %s', leetcode_username)


async def update_stats_and_rankings(client: commands.Bot, now: datetime, daily_reset: bool = False, weekly_reset: bool = False) -> None:
    lock = asyncio.Lock()

    async with lock:
        await update_stats(client, now, daily_reset, weekly_reset)

    async with lock:
        await update_rankings(client, now, daily_reset, weekly_reset)
