from datetime import datetime

# ! replace commands.Bot with custom bot
from database.models import Record, Submissions, User

from utils.questions_utils import UserStats, fetch_problems_solved_and_rank
import aiohttp
from bot import DiscordBot


async def update_stats(
    bot: DiscordBot,
    client_session: aiohttp.ClientSession,
    user: User,
    daily_reset: bool = False,
) -> None:
    """
    Update a user's problem-solving statistics and optionally store them as a record.

    This function fetches updated statistics for a user, assigns the new values to the
    user's submission statistics, and optionally creates a record with the updated
    stats.

    :param user: The user whose stats are being updated.
    :param daily_reset: If `True`, a new record is created and stored with the updated
    stats.
    """

    stats: UserStats = await fetch_problems_solved_and_rank(
        bot, client_session, user.leetcode_id
    )

    if not stats:
        return

    user = await User.find_one(User.id == user.id)

    (
        user.stats.submissions.easy,
        user.stats.submissions.medium,
        user.stats.submissions.hard,
        user.stats.submissions.score,
    ) = (
        stats.submissions.easy,
        stats.submissions.medium,
        stats.submissions.hard,
        stats.submissions.score,
    )

    if daily_reset:
        record = Record(
            timestamp=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            user_id=user.id,
            submissions=Submissions(
                easy=stats.submissions.easy,
                medium=stats.submissions.medium,
                hard=stats.submissions.hard,
                score=stats.submissions.score,
            ),
        )

        await record.save()

    await user.save_changes()


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
