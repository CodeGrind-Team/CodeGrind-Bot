import ast
import random
import re
from typing import Any, List

import markdownify
import requests

import bot_globals

from bot_globals import logger
from utils.common_utils import to_thread
from utils.ratings_utils import get_rating_data


@to_thread
def get_random_question(difficulty: str) -> str | None:
    logger.info(
        "file: utils/questions_utils.py ~ get_random_question ~ run")

    try:
        response = requests.get(
            "https://leetcode.com/api/problems/all/", timeout=10)

    except Exception as e:
        logger.exception(
            "file: cogs/questions.py ~ An error occurred while trying to get the question from LeetCode: %s", e)

        return

    if response.status_code != 200:
        logger.exception(
            "file: cogs/questions.py ~ An error occurred while trying to get the question from LeetCode. Error code: %s", response.status_code)

    data = response.json()

    difficulty_dict = {"easy": 1, "medium": 2, "hard": 3}

    if difficulty in difficulty_dict:
        questions = [
            question for question in data['stat_status_pairs']
            if question['difficulty']['level'] == difficulty_dict[difficulty]
        ]
    else:
        questions = data['stat_status_pairs']

    question = random.choice(questions)

    question_title_slug = question['stat']['question__title_slug']

    return question_title_slug


@to_thread
def get_daily_question(store_question: bool = False) -> str | None:
    logger.info(
        "file: utils/questions_utils.py ~ get_daily_question ~ run")

    url = 'https://leetcode.com/graphql'

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'operationName': 'daily',
        'query':
        '''
        query daily {
            challenge: activeDailyCodingChallengeQuestion {
                date
                link
                question {
                    titleSlug
                }
            }
        }
    '''
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)

    except Exception as e:
        logger.exception(
            "file: cogs/questions.py ~ Daily problem could not be retrieved: %s", e)

        return

    if response.status_code != 200:
        logger.exception(
            "file: cogs/questions.py ~ Daily problem could not be retrieved. Error code: %s", response.status_code)

        return

    response_data = response.json()

    question_title_slug = response_data['data']['challenge']['question']['titleSlug']

    logger.info(
        "file: cogs/questions.py ~ Daily question titleSlug: %s", question_title_slug)

    if store_question:
        bot_globals.DAILY_QUESTION_TITLE_SLUG = question_title_slug

    return question_title_slug


@to_thread
def search_question(text: str) -> str | None:
    logger.info(
        "file: utils/questions_utils.py ~ search_question ~ run")

    url = 'https://leetcode.com/graphql'

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'operationName': 'problemsetQuestionList',
        'query':
        '''
        query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
            problemsetQuestionList: questionList(categorySlug: $categorySlug limit: $limit skip: $skip filters: $filters) {
            questions: 
                data {
                    titleSlug
                }
            }
        }
        ''',
        'variables': {'categorySlug': "", 'skip': 0, 'limit': 1, 'filters': {'searchKeywords': text}}
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)

    except Exception as e:
        logger.exception(
            "file: embeds/question_embeds.py ~ Daily problem could not be retrieved: %s", e)

        return

    if response.status_code != 200:
        logger.exception(
            "file: embeds/question_embeds.py ~ Daily problem could not be retrieved. Error code: %s", response.status_code)

        return

    response_data = response.json()

    questions_matched_list = response_data['data']['problemsetQuestionList']

    if not questions_matched_list:
        return

    question_title_slug = questions_matched_list['questions'][0]['titleSlug']

    return question_title_slug


@to_thread
def get_question_info_from_title(question_title_slug: str) -> List[int | str] | None:
    logger.info(
        "file: utils/questions_utils.py ~ get_question_info_from_title ~ run ~ question_title_slug: %s", question_title_slug)

    url = 'https://leetcode.com/graphql'

    headers = {
        'Content-Type': 'application/json',
    }

    # Get question info
    data = {
        'operationName': 'questionInfo',
        'query':
        '''
        query questionInfo($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionFrontendId
                title
                difficulty
                content
                likes
                dislikes
                stats
                isPaidOnly
            }
        }
        ''',
        'variables': {'titleSlug': question_title_slug}

    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)

    except Exception as e:
        logger.exception(
            "file: cogs/questions.py ~ Question could not be retrieved: %s", e)

        return

    if response.status_code != 200:
        logger.exception(
            "file: cogs/questions.py ~ Question could not be retrieved. Error code: %s", response.status_code)

        return

    # Extracting question details from content
    response_data = response.json()
    difficulty = response_data['data']['question']['difficulty']
    question_id = response_data['data']['question']['questionFrontendId']
    title = response_data['data']['question']['title']
    question_content = response_data['data']['question']['content']
    link = f'https://leetcode.com/problems/{question_title_slug}'
    question_stats = ast.literal_eval(
        response_data['data']['question']['stats'])
    total_accepted = question_stats['totalAccepted']
    total_submission = question_stats['totalSubmission']
    ac_rate = question_stats['acRate']
    premium = response_data['data']['question']['isPaidOnly']

    if premium:
        return premium, question_id, difficulty, title, link, total_accepted, total_submission, ac_rate, None, None, None

    rating_data = get_rating_data(title)

    question_rating = None
    if rating_data is not None:
        question_rating = f"||{int(rating_data['rating'])}||"

    example_position = question_content.find(
        '<strong class="example">')
    constraint_query_string = '<p><strong>Constraints:</strong></p>'
    constraints_position = question_content.find(constraint_query_string)

    description = question_content[:example_position]

    constraints = question_content[constraints_position +
                                   len(constraint_query_string):]

    description = html_to_markdown(description)
    constraints = html_to_markdown(constraints)

    return premium, question_id, difficulty, title, link, total_accepted, total_submission, ac_rate, question_rating, description, constraints


def html_to_markdown(html):
    # Remove all bold, italics, and underlines from code blocks as markdowns doesn't support this.
    html = re.sub(r'(<code>|<pre>)(.*?)(<[/]code>|<[/]pre>)', lambda m: m.group(0).replace('<b>', '').replace('</b>', '').replace(
        '<em>', '').replace('</em>', '').replace('<strong>', '').replace('</strong>', '').replace('<u>', '').replace('</u>', ''), html, flags=re.DOTALL)

    subsitutions = [
        (r'<sup>', r'^'),
        (r'</sup>', r''),
        # Replace image tag with the url src of that image
        (r'<img.*?src="(.*?)".*?>', r'\1'),
        (r'<style.*?>.*?</style>', r''),
        (r'&nbsp;', r' ')
    ]

    for pattern, replacement in subsitutions:
        html = re.sub(pattern, replacement, html, flags=re.DOTALL)

    markdown = markdownify.markdownify(html, heading_style="ATX")

    # Remove unnecessary extra lines
    markdown = re.sub(r'\n\n', '\n', markdown)

    return markdown


@to_thread
def get_problems_solved_and_rank(leetcode_username: str) -> dict[str, Any] | None:
    logger.info(
        "file: utils/questions_utils.py ~ get_problems_solved_and_rank ~ run ~ leetcode_username: %s", leetcode_username)

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
        "file: utils/questions_utils.py ~ get_problems_solved_and_rank ~ data requesting ~ https://leetcode.com/%s", leetcode_username)

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

    if response_data["data"]["matchedUser"] is None:
        logger.warning(
            "file: utils/questions_utils.py ~ get_problems_solved_and_rank ~ user not found ~ https://leetcode.com/%s", leetcode_username)
        return

    logger.info(
        "file: utils/questions_utils.py ~ get_problems_solved_and_rank ~ data requested successfully ~ https://leetcode.com/%s", leetcode_username)

    stats = response_data["data"]["matchedUser"]

    questionsCompleted = {}

    for dic in stats["submitStatsGlobal"]["acSubmissionNum"]:
        questionsCompleted[dic["difficulty"]] = dic["count"]

    stats["submitStatsGlobal"]["acSubmissionNum"] = questionsCompleted

    return stats
