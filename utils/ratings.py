from typing import TYPE_CHECKING

import aiohttp
from discord.ext import tasks

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


@tasks.loop(hours=168)
async def schedule_update_ratings(bot: "DiscordBot") -> None:
    # 168 hours = 1 week.
    # Ratings get updated weekly.
    await bot.ratings.update_ratings()


class Ratings:
    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot
        self.ratings: dict[str, float] = {}

    def fetch_rating(self, title: str) -> dict[str, float] | None:
        return self.ratings.get(title.lower())

    async def update_ratings(self) -> None:
        url = """https://raw.githubusercontent.com/zerotrac/leetcode_problem_rating
        /main/ratings.txt"""

        async with aiohttp.ClientSession() as client_session:
            try:
                async with client_session.get(url) as response:
                    response.raise_for_status()
                    data = await response.text()

                self.ratings = self._parse_ratings(data)
            except aiohttp.ClientError as e:
                self.bot.logger.info(f"Failed to fetch ratings: {e}")

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
