from typing import TYPE_CHECKING

from discord.ext import tasks

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


class Ratings:
    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot
        self.ratings: dict[str, float] = {}

    def fetch_rating(self, title: str) -> dict[str, float] | None:
        return self.ratings.get(title.lower())

    async def update_ratings(self) -> None:
        url = """https://raw.githubusercontent.com/zerotrac/leetcode_problem_rating
        /main/ratings.txt"""

        response_data = await self.bot.fetch_data(url)
        if not response_data:
            return

        self.ratings = self._parse_ratings(response_data)
        self.bot.logger.info("Updated ratings")

    def _parse_ratings(self, data: str) -> dict[str, float]:
        ratings = {}

        lines = data.splitlines()
        # Skip header line
        for line in lines[1:]:
            line_data = line.strip().split("\t")
            rating = float(line_data[0])
            title = line_data[2].strip().lower()
            ratings[title] = rating

        return ratings


@tasks.loop(hours=168)
async def schedule_update_ratings(bot: "DiscordBot") -> None:
    # 168 hours = 1 week.
    # Ratings get updated weekly.
    await bot.ratings.update_ratings()
