import aiohttp
from datetime import datetime


from beanie.odm.operators.update.array import AddToSet

from bot_globals import client, logger
from database.models.server_model import Rankings, Server, UserRank
from database.models.user_model import History, Submissions, User
from utils.common_utils import calculate_scores
from utils.leaderboards_utils import get_score
from utils.questions_utils import get_problems_solved_and_rank


async def update_rankings(server: Server, now: datetime, timeframe: str) -> None:
    logger.info(
        "file: cogs/stats_utils.py ~ update_rankings ~ run ~ timeframe: %s", timeframe)

    logger.info(
        'file: cogs/stats_utils.py ~ update_rankings ~ current server ID: %s', server.id)

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
        'file: cogs/stats_utils.py ~ update_rankings ~ rankings updated successfully for %s timeframe', timeframe)


async def update_stats(client_session: aiohttp.ClientSession, user: User, now: datetime, daily_reset: bool = False, weekly_reset: bool = False) -> None:
    logger.info("file: cogs/stats_utils.py ~ update_stats ~ run ~ now: %s | daily_reset: %s",
                now, daily_reset)

    leetcode_username = user.leetcode_username

    submissions_and_rank = await get_problems_solved_and_rank(client_session, leetcode_username)

    if submissions_and_rank is None:
        return

    rank = submissions_and_rank["profile"]["ranking"]

    easy = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Easy"]
    medium = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Medium"]
    hard = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Hard"]

    total_score = calculate_scores(easy, medium, hard)

    user = await User.find_one(User.id == user.id)

    start_of_week_total_score = get_score(user, "start_of_week_total")
    start_of_day_total_score = get_score(user, "start_of_day_total")

    week_score = total_score - start_of_week_total_score
    day_score = total_score - start_of_day_total_score

    user.scores.week_score = week_score
    user.scores.day_score = day_score
    user.scores.last_updated = now

    user.rank = rank
    user.submissions.easy = easy
    user.submissions.medium = medium
    user.submissions.hard = hard
    user.submissions.total_score = total_score

    await update_display_information_names(user)

    if daily_reset:
        # Increments the streak if the user has submitted a problem today
        if user.scores.day_score > 0:
            user.scores.streak += 1
        else:
            user.scores.streak = 0

        user.scores.yesterday_score = day_score
        user.scores.day_score = 0
        user.scores.start_of_day_total_score = total_score
        user.history.append(History(timestamp=now, submissions=Submissions(
            easy=easy, medium=medium, hard=hard, total_score=total_score), streak=user.scores.streak))

    if weekly_reset:
        user.scores.last_week_score = week_score
        user.scores.week_score = 0
        user.scores.start_of_week_total_score = total_score

    await user.save()

    logger.info(
        'file: cogs/stats_utils.py ~ update_stats ~ user stats updated successfully: %s', leetcode_username)


async def update_display_information_names(user: User) -> None:
    logger.info(
        "file: cogs/stats_utils.py ~ update_display_information_names ~ run ~ user: %s", user.id)

    for i in range(len(user.display_information)-1, -1, -1):
        if user.display_information[i].server_id == 0:
            discord_user = client.get_user(user.id)

            if discord_user:
                user.display_information[i].name = discord_user.name

            continue

        guild = client.get_guild(user.display_information[i].server_id)

        if not guild:
            continue

        member = guild.get_member(user.id)

        if not member:
            logger.info(
                "file: utils/stats.py ~ update_stats ~ user not a member of server ~ user_id: %s, server_id: %s", user.id, guild.id)
            continue

        user.display_information[i].name = member.display_name
