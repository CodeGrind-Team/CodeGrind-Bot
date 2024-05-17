from utils.common_utils import to_thread


class Ratings:
    @classmethod
    async def create(cls, filename: str):
        self = cls()
        self.ratings = await self._read_ratings_txt(filename)
        return self

    def fetch_rating_data(self, title: str) -> dict | None:
        if title.isnumeric():
            question_id = int(title)
            if question_id in self.ratings:
                rating_data = {
                    "question_name": self.ratings[question_id]["question_name"],
                    "rating": self.ratings[question_id]["rating"],
                }
                return rating_data

        # If the title is in the self.ratings dictionary, assume it's the question name
        elif title.lower() in self.ratings:
            rating_data = {
                "question_name": title,
                "rating": self.ratings[title.lower()]["rating"],
            }
            return rating_data

    @to_thread
    def _read_ratings_txt(self, filename: str) -> None:
        ratings = {}

        with open(filename, "r", encoding="UTF-8") as file:
            lines = file.readlines()

            for line in lines:
                line_data = line.strip().split("\t")
                rating = float(line_data[0])
                question_id = int(line_data[1])
                question_name = line_data[2].strip().lower()

                ratings[question_id] = {
                    "question_name": question_name,
                    "rating": rating,
                }

                ratings[question_name] = {"rating": rating}

        return ratings
