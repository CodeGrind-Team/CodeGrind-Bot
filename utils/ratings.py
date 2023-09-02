from typing import Dict

from bot_globals import RATINGS
from utils.run_blocking import to_thread


def get_rating_data(title: str) -> Dict | None:
    if title.isnumeric():
        question_id = int(title)
        if question_id in RATINGS:
            rating_data = {
                "question_name": RATINGS[question_id]["question_name"],
                "rating": RATINGS[question_id]["rating"]
            }
            return rating_data

    # If the title is in the RATINGS dictionary, assume it's the question name
    elif title.lower() in RATINGS:
        rating_data = {
            "question_name": title,
            "rating": RATINGS[title.lower()]["rating"]
        }
        return rating_data


@to_thread
def get_rating_data_to_thread(title: str) -> Dict | None:
    return get_rating_data(title)


@to_thread
def read_ratings_txt() -> None:
    with open('ratings.txt', 'r', encoding="UTF-8") as file:
        lines = file.readlines()

        for line in lines:
            line_data = line.strip().split('\t')
            rating = float(line_data[0])
            question_id = int(line_data[1])
            question_name = line_data[2].strip().lower()

            RATINGS[question_id] = {
                'question_name': question_name,
                'rating': rating
            }

            RATINGS[question_name] = {
                'rating': rating
            }
