from datetime import datetime

from beanie.odm.operators.update.general import Set
from utils.leaderboards import get_score

from bot_globals import calculate_scores, logger
from models.server_model import Rankings, Server, UserRank
from models.user_model import User
from utils.leaderboards import get_score
from utils.questions import get_problems_solved_and_rank


async def update_rankings(server: Server, now: datetime, timeframe: str) -> None:
    logger.info(
        "file: cogs/stats.py ~ update_rankings ~ run ~ timeframe: %s", timeframe)

    logger.info(
        'file: cogs/stats.py ~ update_rankings ~ current server ID: %s', server.id)

    if timeframe not in ["daily", "weekly"]:
        return

    score_field = {"daily": "yesterday", "weekly": "last_week"}

    users_sorted = sorted(server.users,
                          key=lambda user: get_score(server.timezone, user, score_field[timeframe]), reverse=True)

    lb_rankings = []
    place = 0
    prev_score = float("-inf")
    for user in users_sorted:
        total_score = get_score(server.timezone, user, score_field[timeframe])

        if total_score == 0:
            break

        if total_score != prev_score:
            place += 1

        user_rank = UserRank(user_id=user.id, rank=place)

        lb_rankings.append(user_rank)

    if len(lb_rankings) > 0:
        rankings = Rankings(date=now, timeframe=timeframe,
                            winner=rankings[0].user_id, rankings=lb_rankings)

        await Server.find_one(Server.id == server.id).update({Server.rankings: rankings})

    logger.info(
        'file: cogs/stats.py ~ update_rankings ~ rankings updated successfully for %s timeframe', timeframe)


async def update_stats(timezone: str, now: datetime, daily_reset: bool = False, weekly_reset: bool = False) -> None:
    logger.info("file: cogs/stats.py ~ update_stats ~ run ~ now: %s | daily_reset: %s | weekly_reset %s",
                now.strftime("%d/%m/%Y, %H:%M:%S"), daily_reset, weekly_reset)

    async for user in User.find(User.scores.timezone == timezone):
        leetcode_username = user.leetcode_username

        submissions_and_rank = get_problems_solved_and_rank(
            leetcode_username)

        if submissions_and_rank is None:
            continue

        rank = submissions_and_rank["profile"]["ranking"]

        easy = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Easy"]
        medium = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Medium"]
        hard = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Hard"]

        total_score = calculate_scores(easy, medium, hard)

        # update based on last_updated at
        # if weekly_reset:
        #     start_of_last_week_score = next(
        #         (score.start_of_last_week_score for score in user.scores if score.timezone == server.timezone), total_score)
        #     last_week_score = total_score - start_of_last_week_score

        #     await User.find_one(User.id == user.id, User.scores.timezone == server.timezone).update(Set({"scores.$.start_of_week_score": last_week_score}))

        # if daily_reset:
        #     start_of_week_score = next(
        #         (score.start_of_week_score for score in user.scores if score.timezone == server.timezone), total_score)
        #     yesterday_score = total_score - start_of_week_score

        #     await User.find_one(User.id == user.id, User.scores.timezone == server.timezone).update(Set({"scores.$.yesterday_score": yesterday_score}))

        # Week score
        # TODO: add projection
        user = await User.find_one(User.id == user.id)
        start_of_week_total_score = get_score(
            timezone, user, "start_of_week_total")

        week_score = total_score - start_of_week_total_score

        await User.find_one(User.id == user.id, User.scores.timezone == timezone).update(Set({"scores.$.week_score": week_score}))

        # Day score
        # TODO: add projection
        user = await User.find_one(User.id == user.id)
        start_of_day_total_score = get_score(
            timezone, user, "start_of_day_total")

        day_score = total_score - start_of_day_total_score

        await User.find_one(User.id == user.id, User.scores.timezone == timezone).update(Set({"scores.$.today_score": day_score}))
        print(user.id)
        await User.find_one(User.id == user.id, User.scores.timezone == timezone).update(Set({"scores.$.last_updated": now}))

        user = await User.find_one(User.id == user.id)
        user.rank = rank
        user.submissions.easy = easy
        user.submissions.medium = medium
        user.submissions.hard = hard
        user.submissions.total_score = total_score
        await user.save_changes()

        # TODO: Add to history
        # if str(now.strftime("%d/%m/%Y")) not in stats["history"]:
        #     data["users"][discord_id]["history"][str(now.strftime("%d/%m/%Y"))] = {
        #         "easy": easy, "medium": medium, "hard": hard}

        logger.info(
            'file: cogs/stats.py ~ update_stats ~ user stats updated successfully: %s', leetcode_username)


async def update_stats_and_rankings(server: Server, now: datetime, daily_reset: bool = False, weekly_reset: bool = False) -> None:
    await update_stats(server.timezone, now, daily_reset, weekly_reset)

    if daily_reset:
        await update_rankings(server, now, timeframe="daily")

    if weekly_reset:
        await update_rankings(server, now, timeframe="weekly")
