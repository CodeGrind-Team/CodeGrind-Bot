from typing import Any

import requests
import random

from bot_globals import logger
from embeds.misc_embeds import error_embed
from embeds.questions_embeds import question_embed
from utils.run_blocking import to_thread
from utils.ratings import get_rating_data
import re
import ast

@to_thread
def get_random_question(difficulty):
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

    return get_question_info_from_title(question_title_slug)


@to_thread
def get_daily_question():
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
                    difficulty
                    title
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
            "file: embeds/question_embeds.py ~ Daily problem could not be retrieved: %s", e)

        embed = error_embed("Daily problem could not be retrieved")
        return embed

    if response.status_code != 200:
        logger.exception(
            "file: embeds/question_embeds.py ~ Daily problem could not be retrieved. Error code: %s", response.status_code)

        embed = error_embed("Daily problem could not be retrieved")
        return embed

    response_data = response.json()

    question_title = response_data['data']['challenge']['question']['titleSlug']

    return get_question_info_from_title(question_title)

def get_question_info_from_title(question_title_slug):
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
            }
        }
        ''',
        'variables': {'titleSlug': question_title_slug}

    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)

    except Exception as e:
        logger.exception(
            "file: embeds/question_embeds.py ~ Question could not be retrieved: %s", e)

        embed = error_embed("Question could not be retrieved")
        return embed

    if response.status_code != 200:
        logger.exception(
            "file: embeds/question_embeds.py ~ Question could not be retrieved. Error code: %s", response.status_code)

        embed = error_embed("Question could not be retrieved")
        return embed

    response_data = response.json()
    question_difficulty = response_data['data']['question']['difficulty']
    question_id = response_data['data']['question']['questionFrontendId']
    question_title = response_data['data']['question']['title']
    question_content = response_data['data']['question']['content']
    question_link = f'https://leetcode.com/problems/{question_title_slug}'
    question_stats = ast.literal_eval(response_data['data']['question']['stats'])
    question_total_accepted = question_stats['totalAccepted']
    question_total_submission = question_stats['totalSubmission']
    question_ac_rate = question_stats['acRate']

    rating_data = get_rating_data(question_title)

    rating_text = "Doesn't exist"
    if rating_data is not None:
        rating_text = f"||{int(rating_data['rating'])}||"

    example_position = question_content.find('<p>&nbsp;</p>\n<p><strong class="example">')
    constraint_query_string = '<p><strong>Constraints:</strong></p>'
    constraints_position = question_content.find(constraint_query_string)

    question_description = question_content[:example_position]
    
    question_constraints = question_content[constraints_position + len(constraint_query_string):]

    subsitutions = [
        (r'\*', r'\\*'),
        (r'<p>', ''),
        (r'</p>', ''),
        (r'<code>', '`'),
        (r'</code>', '`'),
        (r'<strong>', '**'),
        (r'</strong>', '**'),
        (r'<b>', '**'),
        (r'</b>', '**'),
        (r'<em>', '*'),
        (r'</em>', '*'),
        (r'<span[^>]*>', ''),
        (r'</span>', ''),
        (r'&nbsp;', ' '),
        (r'<pre>', '```'),
        (r'</pre>', '```'),
        (r'&quot;', '"'),
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
    ]

    for pattern, replacement in subsitutions:
        question_description = re.sub(pattern, replacement, question_description)
        question_constraints = re.sub(pattern, replacement, question_constraints)


    return question_embed(question_id, question_description, question_constraints, question_difficulty, question_title, rating_text, question_link, question_total_accepted, question_total_submission, question_ac_rate, daily_question=False)

async def search_for_question(question_id_or_title):
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
            total: totalNum
            questions: 
                data {
                    acRate
                    difficulty
                    freqBar
                    frontendQuestionId: questionFrontendId
                    isFavor
                    paidOnly: isPaidOnly
                    status
                    title
                    titleSlug
                    topicTags {
                        name
                        id
                        slug
                    }  
                    hasSolution
                    hasVideoSolution
                }
            }
        }
        ''',
        'variables': {'categorySlug': "", 'skip': 0, 'limit': 5, 'filters': {'searchKeywords': question_id_or_title}}
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

    return get_question_info_from_title(question_title_slug)

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
