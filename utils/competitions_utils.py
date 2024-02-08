import requests
from datetime import datetime

import bot_globals

from bot_globals import logger
from utils.common_utils import to_thread


@to_thread
def daily_completed(leetcode_username: str) -> bool | None:
    logger.info(
        "file: utils/competitions_utils.py ~ daily_completed ~ run")

    url = 'https://leetcode.com/graphql'

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'operationName': 'getDailyCompleted',
        'query':
        '''query getDailyCompleted($username: String!, $limit: Int!) {
            recentAcSubmissionList(username: $username, limit: $limit) {
                titleSlug
                timestamp
            }
        }
        ''',
        'variables': {'username': leetcode_username, 'limit': 1}
    }

    logger.info(
        "file: utils/competitions_utils.py ~ daily_completed ~ data requesting ~ https://leetcode.com/%s", leetcode_username)

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)

    except Exception as e:
        logger.exception(
            "file: utils/questions_utils.py ~ get_problems_solved_and_rank ~ exception: %s", e)

        return

    if response.status_code != 200:
        logger.exception(
            "file: utils/questions_utils.py ~ get_problems_solved_and_rank ~ Error code: %s", response.status_code)

        return

    response_data = response.json()

    if response_data["data"]["recentAcSubmissionList"] is None:
        logger.warning(
            "file: utils/competitions_utils.py ~ daily_completed ~ user not found ~ https://leetcode.com/%s", leetcode_username)
        return

    logger.info(
        "file: utils/competitions_utils.py ~ daily_completed ~ data requested successfully ~ https://leetcode.com/%s", leetcode_username)

    recentAcSubmissionList = response_data["data"]["recentAcSubmissionList"]

    if not recentAcSubmissionList:
        return

    question_title_slug, timestamp = recentAcSubmissionList[
        0]["titleSlug"], recentAcSubmissionList[0]["timestamp"]

    last_submission_is_daily = question_title_slug == bot_globals.DAILY_QUESTION_TITLE_SLUG
    question_completed_today = datetime.fromtimestamp(
        int(timestamp)).date() == datetime.utcnow().date()

    return last_submission_is_daily and question_completed_today
