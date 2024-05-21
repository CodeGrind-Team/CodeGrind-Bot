import aiofiles


class Ratings:
    @classmethod
    async def create(cls, filename: str):
        self = cls()
        self.ratings = await self._read_ratings_txt(filename)
        return self

    def fetch_rating(self, title: str) -> dict[str, float] | None:
        if title.lower() in self.ratings:
            return self.ratings[title.lower()]

    async def _read_ratings_txt(self, filename: str) -> dict:
        ratings = {}

        async with aiofiles.open(filename, mode="r", encoding="UTF-8") as file:
            # Skip header line
            await file.readline()

            async for line in file:
                line_data = line.strip().split("\t")
                rating = float(line_data[0])
                title = line_data[2].strip().lower()

                ratings[title] = rating

        return ratings
