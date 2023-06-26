from typing import Any

import requests

from bot_globals import logger


def get_problems_solved_and_rank(leetcode_username: str) -> dict[str, Any] | None:
    logger.info(
        "file: utils/questions.py ~ get_problems_solved_and_rank ~ run ~ leetcode_username: %s", leetcode_username)

    url = 'https://leetcode.com/graphql'

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'operationName': 'getProblemsSolvedAndRank',
        'query':
        '''query getProblemsSolvedAndRank($username: String!) {
            matchedUser(username: $username) {
                profile {
                    realName
                    ranking
                }
                submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
            }
        }
        ''',
        'variables': {'username': leetcode_username}
    }

    logger.info(
        "file: utils/questions.py ~ get_problems_solved_and_rank ~ data requesting ~ https://leetcode.com/%s", leetcode_username)

    try:
        response = requests.post(
            url, json=data, headers=headers, timeout=5)
    except Exception as e:
        logger.exception(
            "file: utils/questions.py ~ get_problems_solved_and_rank ~ exception: %s", e)
        return

    if response.status_code != 200:
        return

    response_data = response.json()

    if response_data["data"]["matchedUser"] is None:
        logger.warning(
            "file: utils/questions.py ~ get_problems_solved_and_rank ~ user not found ~ https://leetcode.com/%s", leetcode_username)
        return

    logger.info(
        "file: utils/questions.py ~ get_problems_solved_and_rank ~ data requested successfully ~ https://leetcode.com/%s", leetcode_username)

    stats = response_data["data"]["matchedUser"]

    questionsCompleted = {}

    for dic in stats["submitStatsGlobal"]["acSubmissionNum"]:
        questionsCompleted[dic["difficulty"]] = dic["count"]

    stats["submitStatsGlobal"]["acSubmissionNum"] = questionsCompleted

    return stats
