from datetime import datetime

# ! replace commands.Bot with custom bot
from database.models.record_model import Record
from database.models.user_model import Submissions, User
from utils.common_utils import convert_to_score
from utils.questions_utils import UserStats, fetch_problems_solved_and_rank


async def update_stats(user: User, store: bool = False) -> None:
    """
    Update a user's problem-solving statistics and optionally store them as a record.

    This function fetches updated statistics for a user, assigns the new values to the
    user's submission statistics, and optionally creates a record with the updated
    stats. If the fetched stats are invalid or not found, the function exits early.

    :param user: The user whose stats are being updated.
    :param store: If `True`, a new record is created and stored with the updated
    statistics.
    """

    stats: UserStats = await fetch_problems_solved_and_rank()

    if not stats:
        return

    user = await User.find_one(User.id == user.id)

    (
        user.stats.submissions.easy,
        user.stats.submissions.medium,
        user.stats.submissions.hard,
        user.stats.submissions.score,
    ) = (
        UserStats.submissions.easy,
        UserStats.submissions.medium,
        UserStats.submissions.hard,
        UserStats.submissions.score,
    )

    if store:
        record = Record(
            timestamp=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            user_id=user.id,
            submissions=Submissions(
                easy=stats.submissions.easy,
                medium=stats.submissions.medium,
                hard=stats.submissions.hard,
                score=convert_to_score(**stats.submissions),
            ),
        )

    await record.save()
    await user.save_changes()

    # TODO: not needed anymore
    # await update_display_information_names(user)

    # TODO: not needed / move somewhere else
    # if Period.DAY in reset_periods:
    #     # Increments the streak if the user has submitted a problem today
    #     user.scores.streak += user.scores.day_score > 0

    #     user.scores.yesterday_score = day_score
    #     user.scores.day_score = 0
    #     user.scores.start_of_day_total_score = total_score

    # if Period.WEEK in reset_periods:
    #     user.scores.last_week_score = week_score
    #     user.scores.week_score = 0
    #     user.scores.start_of_week_total_score = total_score


# async def update_display_information_names(bot: commands.Bot, user: User) -> None:
#     for i in range(len(user.display_information) - 1, -1, -1):
#         if user.display_information[i].server_id == 0:
#             discord_user = bot.get_user(user.id)

#             if discord_user:
#                 user.display_information[i].name = discord_user.name

#             continue

#         guild = bot.get_guild(user.display_information[i].server_id)

#         if not guild:
#             continue

#         member = guild.get_member(user.id)

#         if not member:
#             continue

#         user.display_information[i].name = member.display_name
