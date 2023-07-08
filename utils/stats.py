from datetime import datetime

from beanie.odm.operators.update.array import AddToSet
from beanie.odm.operators.update.general import Set

from bot_globals import calculate_scores, logger
from models.server_model import Rankings, Server, UserRank
from models.user_model import User, History, Submissions
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
                          key=lambda user: get_score(user, score_field[timeframe]), reverse=True)

    lb_rankings = []
    place = 0
    prev_score = float("-inf")
    for user in users_sorted:
        total_score = get_score(user, score_field[timeframe])

        if total_score == 0:
            break

        if total_score != prev_score:
            place += 1

        user_rank = UserRank(user_id=user.id, rank=place)
        lb_rankings.append(user_rank)

    if len(lb_rankings) > 0:
        rankings = Rankings(date=now, timeframe=timeframe,
                            winner=lb_rankings[0].user_id, rankings_order=lb_rankings)

        await Server.find_one(Server.id == server.id).update(AddToSet({Server.rankings: rankings}))

    logger.info(
        'file: cogs/stats.py ~ update_rankings ~ rankings updated successfully for %s timeframe', timeframe)


async def update_stats(user: User, now: datetime, daily_reset: bool = False, weekly_reset: bool = False) -> None:
    logger.info("file: cogs/stats.py ~ update_stats ~ run ~ now: %s | daily_reset: %s",
                now, daily_reset)

    leetcode_username = user.leetcode_username

    submissions_and_rank = get_problems_solved_and_rank(
        leetcode_username)

    if submissions_and_rank is None:
        return

    rank = submissions_and_rank["profile"]["ranking"]

    easy = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Easy"]
    medium = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Medium"]
    hard = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Hard"]

    total_score = calculate_scores(easy, medium, hard)

    # Week score
    # TODO: add projection
    user = await User.find_one(User.id == user.id)
    start_of_week_total_score = get_score(user, "start_of_week_total")

    week_score = total_score - start_of_week_total_score

    await User.find_one(User.id == user.id).update(Set({User.scores.week_score: week_score}))

    # Day score
    # TODO: add projection
    user = await User.find_one(User.id == user.id)
    start_of_day_total_score = get_score(user, "start_of_day_total")

    day_score = total_score - start_of_day_total_score

    await User.find_one(User.id == user.id).update(Set({User.scores.today_score: day_score}))

    await User.find_one(User.id == user.id).update(Set({User.scores.last_updated: now}))

    user = await User.find_one(User.id == user.id)
    user.rank = rank
    user.submissions.easy = easy
    user.submissions.medium = medium
    user.submissions.hard = hard
    user.submissions.total_score = total_score

    if daily_reset:
        user.scores.yesterday_score = day_score
        user.scores.today_score = 0
        user.scores.start_of_day_total_score = 0

    if weekly_reset:
        user.scores.last_week_score = week_score
        user.scores.week_score = 0
        user.scores.start_of_week_total_score = 0

    user.history.append(History(timestamp=now, submissions=Submissions(
        easy=easy, medium=medium, hard=hard, total_score=total_score)))

    await user.save_changes()

    logger.info(
        'file: cogs/stats.py ~ update_stats ~ user stats updated successfully: %s', leetcode_username)
