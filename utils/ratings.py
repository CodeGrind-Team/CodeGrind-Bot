from typing import Dict

from bot_globals import Rating

def get_rating_data(title: str) -> Dict[str, str | int] | None:
    if title.isnumeric():
        question_id = int(title)
        if question_id in RATINGS:
            rating_data = {
                "question_name": RATINGS[question_id]["question_name"].capitalize(),
                "rating": RATINGS[question_id]["rating"]
            }
            return rating_data

    # If the title is in the RATINGS dictionary, assume it's the question name
    elif title in RATINGS:
        rating_data = {
            "question_name": title.capitalize()
            "rating": RATINGS[title.lower()]["rating"]
        }
        return rating_data