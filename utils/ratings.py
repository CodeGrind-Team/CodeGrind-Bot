import aiohttp
from discord.ext import tasks


class Ratings:
    @classmethod
    async def create(cls, filepath: str):
        self = cls()
        self.filepath = filepath
        self.ratings = {}
        await self.update_ratings()
        return self

    def fetch_rating(self, title: str) -> dict[str, float] | None:
        return self.ratings.get(title.lower())
    
    @tasks.loop(seconds=10)
    async def update_ratings_schedule(bot) -> None:
        # 168 hours = 1 week

    async def update_ratings(self) -> None:
        # TODO: add to schedule (1 week)
        url = """https://raw.githubusercontent.com/zerotrac/leetcode_problem_rating
        /main/ratings.txt"""
        print("YEEEHAAA")
        async with aiohttp.ClientSession() as client_session:
            try:
                response = await client_session.get(url)
                response.raise_for_status()
                data = await response.text()
                await self._parse_ratings(data)
            except aiohttp.ClientError as e:
                print(f"Failed to fetch ratings: {e}")

    async def _parse_ratings(self, data: str) -> dict:
        ratings = {}

        lines = data.splitlines()
        # Skip header line
        for line in lines[1:]:
            line_data = line.strip().split("\t")
            rating = float(line_data[0])
            title = line_data[2].strip().lower()
            ratings[title] = rating

        self.ratings = ratings
