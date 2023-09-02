import ast
import random
import re
from typing import Any, List, Union

import discord
import requests
from bot_globals import logger
from embeds.misc_embeds import error_embed

from utils.ratings import get_rating_data
from utils.run_blocking import to_thread


async def get_random_question(difficulty: str) -> str:
    logger.info(
        "file: utils/questions.py ~ get_random_question ~ run")

    try:
        response = requests.get(
            "https://leetcode.com/api/problems/all/", timeout=10)

    except Exception as e:
        logger.exception(
            "file: cogs/questions.py ~ An error occurred while trying to get the question from LeetCode: %s", e)

        embed = error_embed("Random problem could not be retrieved")
        return embed

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
def get_daily_question() -> str:
    logger.info(
        "file: utils/questions.py ~ get_daily_question ~ run")

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

        embed = error_embed("Daily problem could not be retrieved")
        return embed

    if response.status_code != 200:
        logger.exception(
            "file: cogs/questions.py ~ Daily problem could not be retrieved. Error code: %s", response.status_code)

        embed = error_embed("Daily problem could not be retrieved")
        return embed

    response_data = response.json()

    question_title_slug = response_data['data']['challenge']['question']['titleSlug']

    return question_title_slug

async def get_question_info_from_title(question_title_slug: str) -> List[Union[int, str]]:
    logger.info(
        "file: utils/questions.py ~ get_question_info_from_title ~ run")
    
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

        embed = error_embed("Question could not be retrieved")
        return embed

    if response.status_code != 200:
        logger.exception(
            "file: cogs/questions.py ~ Question could not be retrieved. Error code: %s", response.status_code)

        embed = error_embed("Question could not be retrieved")
        return embed

    # Extracting question details from content
    response_data = response.json()
    difficulty = response_data['data']['question']['difficulty']
    frontendId = response_data['data']['question']['questionFrontendId']
    title = response_data['data']['question']['title']
    question_content = response_data['data']['question']['content']
    link = f'https://leetcode.com/problems/{question_title_slug}'
    question_stats = ast.literal_eval(response_data['data']['question']['stats'])
    total_accepted = question_stats['totalAccepted']
    total_submission = question_stats['totalSubmission']
    ac_rate = question_stats['acRate']
    premium = response_data['data']['question']['isPaidOnly']

    if premium:
        return [premium, frontendId, '', '', '', title, '', link, '', '', '']

    rating_data = get_rating_data(title)

    question_rating = None
    if rating_data is not None:
        question_rating = f"||{int(rating_data['rating'])}||"
    
    example_position = question_content.find('<p>&nbsp;</p>\n<p><strong class="example">')
    constraint_query_string = '<p><strong>Constraints:</strong></p>'
    constraints_position = question_content.find(constraint_query_string)


    description = question_content[:example_position]
    
    constraints = question_content[constraints_position + len(constraint_query_string):]

    subsitutions = [
        (r'\*', r'\\*'),
        (r'<p>', ''),
        (r'</p>', ''),
        (r'<a href="([^"]+)" target="_blank">([^<]+)</a>', r'[\2](\1)'),
        (r'<b>', '**'),
        (r'</b>', '**'),
        (r'<em>', '_'),
        (r'</em>', '_'),
        (r'<code>', '`'),
        (r'</code>', '`'),
        (r'<strong>', '**'),
        (r'</strong>', '**'),
        (r'<u>', '__'),
        (r'</u>', '__'),
        (r'<span[^>]*>', ''),
        (r'</span>', ''),
        (r'&nbsp;', ' '),
        (r'<pre>', '```'),
        (r'</pre>', '```'),
        (r'&quot;', '"'),
        (r'&ldquo;', '"'),
        (r'&rdquo;', '"'),
        (r'<sub>', '_'),
        (r'</sub>', ''),
        (r'&gt;', '>'),
        (r'&lt;', '<'),
        (r'<sup>', '^'),
        (r'</sup>', ''),
        (r'&#39;', "'"),
        (r'<ul>', ''),
        (r'</ul>', ''),
        (r'\t<li>', '- '),
        (r'</li>', ''),
        (r'<font[^>]*>', ''),
        (r'</font>', ''),
        (r'`([^`]+)\*([^`]+)`', r'`\1\2`')
    ]

    for pattern, replacement in subsitutions:
        description = re.sub(pattern, replacement, description)
        constraints = re.sub(pattern, replacement, constraints)

    question_info = [premium, frontendId, description, constraints, difficulty, title, question_rating, link, total_accepted, total_submission, ac_rate]


    return question_info

async def search_for_question(question_name_or_id: str) -> str:
    logger.info(
        "file: utils/questions.py ~ search_for_question ~ run")

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
        'variables': {'categorySlug': "", 'skip': 0, 'limit': 1, 'filters': {'searchKeywords': question_name_or_id}}
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)

    except Exception as e:
        logger.exception(
            "file: embeds/question_embeds.py ~ Daily problem could not be retrieved: %s", e)

        embed = error_embed("Daily problem could not be retrieved")
        return embed

    if response.status_code != 200:
        logger.exception(
            "file: embeds/question_embeds.py ~ Daily problem could not be retrieved. Error code: %s", response.status_code)

        embed = error_embed("Daily problem could not be retrieved")
        return embed

    response_data = response.json()

    question_title_slug = response_data['data']['problemsetQuestionList']['questions'][0]['titleSlug']

    return question_title_slug

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
        response = requests.post(url, json=data, headers=headers, timeout=10)

    except Exception as e:
        logger.exception(
            "file: utils/questions.py ~ get_problems_solved_and_rank ~ exception: %s", e)

        return

    if response.status_code != 200:
        logger.exception(
            "file: utils/questions.py ~ get_problems_solved_and_rank ~ Error code: %s", response.status_code)

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
