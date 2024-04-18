from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta

import discord
from sortedcollections import ValueSortedDict

from constants import Period, RankEmoji
from database.models.preference_model import Preference
from database.models.record_model import Record
from database.models.server_model import Server
from database.models.user_model import User
from embeds.leaderboards_embeds import (empty_leaderboard_embed,
                                        leaderboard_embed)
from utils.common_utils import convert_to_score, strftime_with_suffix
from views.leaderboard_view import LeaderboardPagination


class Leaderboard(ABC):
    def __init__(self) -> None:
        self.leaderboard = ValueSortedDict()

    def _get_score(self, user_id: int) -> int:
        """
        Get the score of a user for a leaderboard.

        :param user_id: The user's ID.

        :return: The user's score.
        """
        return self.leaderboard[user_id]

    def _update_score(self, user_id: int, score: int) -> None:
        """
        Update the score of a user for the leaderboard.

        :param user_id: The user's ID.
        :param score: The user's score.
        """
        self.leaderboard[user_id] = score

    def clear(self) -> None:
        """
        Clear a leaderboard.
        """
        self.leaderboard.clear()

    @abstractmethod
    async def calculate_score(self, user: User) -> int:
        """
        Calculate the user's score.

        :param user: The user.

        :return: The user's score.
        """
        pass


class DailyLeaderboard(Leaderboard):
    async def calculate_score(self, user: User) -> int:
        """
        Calculate the user's score for the day.

        :param user: The user.

        :return: The user's score for the day.
        """
        current_score = convert_to_score(**user.stats.submissions)

        timestamp = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=datetime.now().weekday())

        record = await Record.find_one(
            Record.user == user, Record.timestamp == timestamp
        )

        if not record:
            return current_score

        score_difference = current_score - \
            convert_to_score(**record.submissions)

        return score_difference


class WeeklyLeaderboard(Leaderboard):
    async def calculate_score(self, user: User) -> int:
        """
        Calculate the user's score for the week.

        :param user: The user.

        :return: The user's score for the week.
        """
        current_score = convert_to_score(**user.stats.submissions)

        timestamp = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=datetime.now().weekday())

        record = await Record.find_one(
            Record.user == user, Record.timestamp >= timestamp, sort=timestamp
        )

        if not record:
            return current_score

        score_difference = current_score - \
            convert_to_score(**record.submissions)

        return score_difference


class MonthlyLeaderboard(Leaderboard):
    async def calculate_score(self, user: User) -> int:
        """
        Calculate the user's score for the month.

        :param user: The user.

        :return: The user's score for the month.
        """
        current_score = convert_to_score(**user.stats.submissions)

        timestamp = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        record = await Record.find_one(
            Record.user == user, Record.timestamp >= timestamp, sort=timestamp
        )

        if not record:
            return current_score

        score_difference = current_score - \
            convert_to_score(**record.submissions)

        return score_difference


class AllTimeLeaderboard(Leaderboard):
    async def calculate_score(self, user: User) -> int:
        """
        Calculate the user's total score.

        :param user: The user.

        :return: The user's total score.
        """
        current_score = convert_to_score(**user.stats.submissions)
        return current_score


class Leaderboards:
    def __init__(self) -> None:
        self.leaderboards: dict[Period, Leaderboard] = {
            Period.WEEK: WeeklyLeaderboard(),
            Period.MONTH: MonthlyLeaderboard(),
            Period.ALLTIME: AllTimeLeaderboard(),
        }

    async def update_scores(self, periods: set[Period]) -> None:
        """
        Update scores for all users for selected periods.

        :param periods: The periods to update scores for.
        """
        async for user in User.all():
            for period in periods:
                leaderboard = self.leaderboards[period]
                await leaderboard.update_score(
                    user.id, await leaderboard.calculate_score(user)
                )

    def get_score(self, period: Period, user_id: int) -> int:
        """
        Get the score of a user for a specific period.

        :param period: The period.
        :param user_id: The user's ID.

        :return: The user's score.
        """
        leaderboard = self.leaderboards[period]
        return leaderboard._get_score(user_id)

    def clear(self, period: Period) -> None:
        """
        Clear a specific leaderboard.

        :param period: The period.
        """
        leaderboard = self.leaderboards[period]
        leaderboard.clear()

    def clear_all(self) -> None:
        """
        Clear all leaderboards.
        """
        for leaderboard in self.leaderboards.values():
            leaderboard.clear()


class LeaderboardManager:
    def __init__(self) -> None:
        self.leaderboard = Leaderboards(
            {Period.DAY, Period.WEEK, Period.MONTH, Period.ALLTIME}
        )

    async def generate_leaderboard_embed(
        self,
        period: Period,
        server: Server,
        author_user_id: int | None = None,
        winners_only: bool = False,
        global_leaderboard: bool = False,
        page: int = 1,
        users_per_page: int = 10,
    ) -> tuple[discord.Embed, discord.ui.View]:
        """
        Generate a leaderboard embed.

        :param period: The period.
        :param server: The server.
        :param author_user_id: The author's user ID.
        :param winners_only: Whether to display only the winners.
        :param global_leaderboard: Whether to display the global leaderboard.
        :param page: The page number.
        :param users_per_page: The number of users per page.

        :return: The leaderboard embed and view.
        """
        pages: list[discord.Embed] = []
        num_pages = -(-len(server.users) // users_per_page)

        place = 0
        prev_score = float("-inf")

        for page_index in range(num_pages):
            page, place, prev_score = await self._build_leaderboard_page(
                period,
                server,
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
        view = (
            None if winners_only else LeaderboardPagination(
                author_user_id, pages, page)
        )

        return pages[page], view

        # try:
        #     await send_message(embed=pages[page], view=view)
        # except discord.errors.Forbidden as e:
        #     logger.exception(
        #         "file: utils/leaderboards_utils.py ~ display_leaderboard ~ \
        #         missing permissions on server id %s. Error: %s",
        #         server.id,
        #         e,
        #     )

    async def _build_leaderboard_page(
        self,
        period: Period,
        server: Server,
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

        for user in server.users[
            page_index * users_per_page: page_index * users_per_page + users_per_page
        ]:

            profile_link = f"https://leetcode.com/{user.leetcode_username}"

            # ? Check if this is possible or if dbref needs to be
            # ? specified on the id
            preference = await Preference.find_one(
                Preference.user == user, Preference.server == server
            )

            if not preference:
                continue

            name = preference.name
            url = preference.url
            visible = preference.visible
            score = self._get_score(period, user.id)

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

            rank = self._get_rank_emoji(place, score)
            leaderboard.append(f"**{rank} {display_name}** - **{score}** pts")

        title = self._get_title(period, winners_only, global_leaderboard)

        return (
            leaderboard_embed(server, page_index, num_pages,
                              title, leaderboard),
            place,
            prev_score,
        )

    def _get_title(
        self, period: Period, winners_only: bool, global_leaderboard: bool
    ) -> str:
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
            title = self._get_winners_title(period)

        return title

    def _get_winners_title(self, period: Period) -> str:
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
                "{S} %b %Y", (datetime.now(UTC) -
                              timedelta(days=1)).replace(day=1)
            )
            end_timestamp = strftime_with_suffix(
                "{S} %b %Y", datetime.now(UTC) - timedelta(days=1)
            )
            return f"Last Month's Winners ({start_timestamp} - {end_timestamp})"

    def _get_rank_emoji(self, place: int, score: int) -> str:
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

        return f"{place}\."


# ! check this
# async def send_leaderboard_winners(server: Server, period: str) -> None:
#     for channel_id in server.channels.winners:
#         channel = client.get_channel(channel_id)

#         if not channel or not isinstance(channel, discord.TextChannel):
#             continue

#         try:
#             await display_leaderboard(
#                 channel.send, server.id, period=period, winners_only=True
#             )
#         except discord.errors.Forbidden as e:
#             logger.exception(
#                 "file: utils/leaderboards_utils.py ~ send_leaderboard_winners ~ missing permissions on channel id %s. Error: %s",
#                 channel.id,
#                 e,
#             )

#     logger.info(
#         "file: utils/leaderboards_utils.py ~ send_leaderboard_winners ~ %s winners leaderboard sent to channels",
#         period,
#     )


# async def update_global_leaderboard() -> None:
#     """Add all users to the global server in case anyone is missing."""
#     async for user in User.all():
#         await Server.find_one(Server.id == 0).update(AddToSet({Server.users: user}))
