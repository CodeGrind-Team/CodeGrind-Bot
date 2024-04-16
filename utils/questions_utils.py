import ast
import asyncio
import random
import re
from dataclasses import dataclass

import aiohttp
import backoff
import markdownify
import requests

from utils.common_utils import to_thread
from utils.ratings_utils import get_rating_data

URL = 'https://leetcode.com/graphql'
HEADERS = {
    'Content-Type': 'application/json',
    'Origin': 'https://leetcode.com',
    'Referer': 'https://leetcode.com',
    'Cookie': 'csrftoken=; LEETCODE_SESSION=;',
    'x-csrftoken': '',
    'user-agent': 'Mozilla/5.0 LeetCode API'
}


semaphore = asyncio.Semaphore(8)


@dataclass
class QuestionInfo:
    premium: bool
    question_id: int
    difficulty: str
    title: str
    link: str
    total_accepted: int
    total_submission: int
    ac_rate: float
    question_rating: int | None
    description: str | None
    constraints: str | None


@dataclass
class Submissions:
    easy: int
    medium: int
    hard: int


@dataclass
class UserStats:
    submissions: Submissions


class RateLimitReached(Exception):
    def __init__(self) -> None:
        super().__init__("ExceptionWithStatusCode. Error: 429. Rate Limited.")


@to_thread
def get_random_question(difficulty: str) -> str | None:
    """
    Fetches a random LeetCode question title slug based on the given difficulty.

    :param difficulty: The difficulty level of the question
                       ("easy", "medium", or "hard").

    :return: The title slug of a randomly selected question, or None if an error occurs.
    """
    logger.info(
        "file: utils/questions_utils.py ~ get_random_question ~ run")

    try:
        response = requests.get(
            "https://leetcode.com/api/problems/all/", timeout=10)
        response.raise_for_status()
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
        return question['stat']['question__title_slug']

    except requests.RequestException as e:
        logger.exception(
            "file: cogs/questions.py ~ An error occurred while trying to get the question from LeetCode: %s", e)

        return


@to_thread
def get_daily_question() -> str | None:
    """
    Fetches the title slug of the active daily coding challenge question.

    :return: The title slug of the daily coding challenge question,
             or None if an error occurs.
    """
    # ! Use aiohttp
    logger.info(
        "file: utils/questions_utils.py ~ get_daily_question ~ run")

    data = {
        'operationName': 'daily',
        'query':
        '''
        query daily {
            challenge: activeDailyCodingChallengeQuestion {
                question {
                    titleSlug
                }
            }
        }
    '''
    }

    try:
        response = requests.post(URL, json=data, headers=HEADERS, timeout=10)
        response.raise_for_status()
        response_data = response.json()

        return response_data['data']['challenge']['question']['titleSlug']

    except requests.RequestException as e:
        logger.exception(
            "file: cogs/questions.py ~ Daily problem could not be retrieved: %s", e)

        return


@to_thread
def search_question(text: str) -> str | None:
    """
    Searches for a LeetCode question title slug based on the provided text.

    :param text: The text to search for in the question titles.

    :return: The title slug of the matched question, or None if no match is found or an
             error occurs.
    """
    logger.info(
        "file: utils/questions_utils.py ~ search_question ~ run")

    data = {
        'operationName': 'problemsetQuestionList',
        'query':
        '''
        query problemsetQuestionList(
            $categorySlug: String,
            $limit: Int,
            $skip: Int,
            $filters: QuestionListFilterInput
        ) {
            problemsetQuestionList: questionList(
                categorySlug: $categorySlug,
                limit: $limit,
                skip: $skip,
                filters: $filters
            ) {
                questions:
                    data {
                        titleSlug
                    }
                }
            }
        ''',
        'variables': {
            'categorySlug': "",
            'skip': 0,
            'limit': 1,
            'filters': {'searchKeywords': text}
        }
    }

    try:
        response = requests.post(URL, json=data, headers=HEADERS, timeout=10)
        response.raise_for_status()
        response_data = response.json()

        questions_matched_list = response_data['data']['problemsetQuestionList']

        if not questions_matched_list:
            return

        question_title_slug = questions_matched_list['questions'][0]['titleSlug']

        return question_title_slug

    except requests.RequestException as e:
        logger.exception(
            "file: embeds/question_embeds.py ~ Daily problem could not be retrieved: %s", e)

        return


@to_thread
def get_question_info_from_title(question_title_slug: str) -> QuestionInfo | None:
    """
    Retrieves information about a LeetCode question based on its title slug.

    :param question_title_slug: The title slug of the LeetCode question.

    :return: Information about the LeetCode question, or None if an error occurs or no
             question is found.
    """

    logger.info(
        "file: utils/questions_utils.py ~ get_question_info_from_title ~ run ~ question_title_slug: %s", question_title_slug)

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
        response = requests.post(URL, json=data, headers=HEADERS, timeout=10)
        response.raise_for_status()

        response_data = response.json()
        question = response_data.get('data', {}).get('question')

        if not question:
            logger.warning("No question data found for %s",
                           question_title_slug)
            return None

        question_id = question['questionFrontendId']
        difficulty = question['difficulty']
        title = question['title']
        content = question['content']
        is_paid_only = question['isPaidOnly']
        link = f'https://leetcode.com/problems/{question_title_slug}'

        stats = ast.literal_eval(question['stats'])
        total_accepted = stats.get('totalAccepted', 0)
        total_submission = stats.get('totalSubmission', 0)
        ac_rate = stats.get('acRate', 0.0)

        # Get question rating
        question_rating = None
        if not is_paid_only:
            rating_data = get_rating_data(title)
            if rating_data:
                question_rating = int(rating_data['rating'])

        # Parse content for description and constraints
        description, constraints = parse_content(content)

        return QuestionInfo(premium=is_paid_only,
                            question_id=question_id,
                            difficulty=difficulty,
                            title=title,
                            link=link,
                            total_accepted=total_accepted,
                            total_submission=total_submission,
                            ac_rate=ac_rate,
                            question_rating=question_rating,
                            description=description,
                            constraints=constraints)

    except requests.RequestException as e:
        logger.exception(
            "file: cogs/questions.py ~ Question could not be retrieved: %s", e)
        return


def parse_content(content: str) -> tuple[str, str]:
    """
    Parses the content of a LeetCode question to extract description and constraints.

    :param content: The HTML content of the question.

    :return: A tuple containing the description and constraints of the question,
             or None if not found.
    """
    example_position = content.find(
        '<strong class="example">')
    constraint_query_string = '<p><strong>Constraints:</strong></p>'
    constraints_position = content.find(constraint_query_string)

    description = html_to_markdown(content[:example_position])
    constraints = html_to_markdown(
        content[constraints_position + len(constraint_query_string):])

    return description, constraints


def html_to_markdown(html: str) -> str:
    """
    Converts HTML content to Markdown.

    :param html: The HTML content to convert to Markdown.

    :return: The Markdown content.
    """
    # Remove all bold, italics, and underlines from code blocks as markdowns doesn't
    # support this.
    html = re.sub(r'(<code>|<pre>)(.*?)(<[/]code>|<[/]pre>)',
                  lambda m: m.group(0).replace('<b>', '').replace('</b>', '').replace(
                      '<em>', '').replace('</em>', '').replace('<strong>', '').replace('</strong>', '').replace('<u>', '').replace('</u>', ''),
                  html,
                  flags=re.DOTALL)

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


@backoff.on_exception(backoff.expo, RateLimitReached)
async def get_problems_solved_and_rank(client_session: aiohttp.ClientSession,
                                       leetcode_username: str) -> UserStats | None:
    """
    Retrieves the statistics of problems solved and rank of a LeetCode user.

    :param client_session: The aiohttp ClientSession to use for making requests.
    :param leetcode_username: The LeetCode username.

    :return: Statistics of problems solved and rank of the user, or None if an error occurs.
    """

    logger.info(
        "file: utils/questions_utils.py ~ get_problems_solved_and_rank ~ run ~ leetcode_username: %s", leetcode_username)

    data = {
        'operationName': 'getProblemsSolvedAndRank',
        'query':
        '''query getProblemsSolvedAndRank($username: String!) {
            matchedUser(username: $username) {
                profile {
                    realName
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

    async with semaphore:
        try:
            response = await client_session.post(
                URL, json=data, headers=HEADERS, timeout=10)

            # TODO: write why
            await asyncio.sleep(random.random())

        except aiohttp.ClientError as e:
            logger.exception(
                "file: utils/questions_utils.py ~ get_problems_solved_and_rank ~ \
                    exception: %s", e)

            return

    if response.status == 429:
        # Rate limit reached
        logger.exception(
            "file: utils/questions_utils.py ~ get_problems_solved_and_rank ~ LeetCode username: %s ~ Error code: %s", leetcode_username, response.status)

        client.channel_logger.rate_limited()
        raise RateLimitReached()
    elif response.status == 403:
        # Forbidden access
        logger.exception(
            "file: utils/questions_utils.py ~ get_problems_solved_and_rank ~ LeetCode username: %s ~ Error code: %s", leetcode_username, response.status)
        client.channel_logger.forbidden()
        return
    elif response.status != 200:
        logger.exception(
            "file: utils/questions_utils.py ~ get_problems_solved_and_rank ~ LeetCode username: %s ~ Error code: %s", leetcode_username, response.status)
        return

    response_data = await response.json()

    matched_user = response_data.get("data", {}).get("matchedUser")

    if not matched_user:
        logger.warning("User %s not found", leetcode_username)
        return

    submit_stats_global = matched_user.get("submitStatsGlobal", {})
    ac_submission_num = submit_stats_global.get("acSubmissionNum", [])

    easy_count = next(
        (item["count"]
         for item in ac_submission_num if item["difficulty"] == "easy"),
        0)
    medium_count = next(
        (item["count"]
         for item in ac_submission_num if item["difficulty"] == "medium"),
        0)
    hard_count = next(
        (item["count"]
         for item in ac_submission_num if item["difficulty"] == "hard"),
        0)

    return UserStats(submissions=Submissions(easy=easy_count,
                                             medium=medium_count,
                                             hard=hard_count))
