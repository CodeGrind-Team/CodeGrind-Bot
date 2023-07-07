from typing import Dict

from bot_globals import RATINGS
from utils.run_blocking import to_thread


@to_thread
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
