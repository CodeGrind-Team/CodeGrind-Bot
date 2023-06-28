from typing import Any

import discord
import requests

from bot_globals import logger
from utils.io_handling import read_ratings_txt


async def daily_question_embed() -> discord.Embed:
    logger.info(
        "file: utils/questions.py ~ daily_question_embed ~ run")

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
                }
            }
        }
    '''
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=5)
    except Exception as e:
        logger.exception(
            "file: utils/questions.py ~ daily_question_embed ~ exception: %s", e)

        embed = discord.Embed(title="Daily problem",
                              color=discord.Color.blue())

        embed.description = "Daily problem could not be retrieved"

        return embed

    if response.status_code != 200:
        embed = discord.Embed(title="Daily problem",
                              color=discord.Color.blue())

        embed.description = "Daily problem could not be retrieved"

    response_data = response.json()

    # Extract and print the link
    link = response_data['data']['challenge']['link']
    # Extract and print the title
    title = response_data['data']['challenge']['question']['title']
    # Extract and print the difficulty
    difficulty = response_data['data']['challenge']['question']['difficulty']
    # Extract and print the date
    # date = response_data['data']['challenge']['date']
    rating_id = await read_ratings_txt(title)
    link = f"https://leetcode.com{link}"
    embed = discord.Embed(title=f"Daily Problem: {title}",
                          color=discord.Color.blue())
    embed.add_field(name="**Difficulty**",
                    value=f"{difficulty}", inline=True)
    embed.add_field(name="**Zerotrac Rating**",
                    value=f"{rating_id}", inline=True)
    embed.add_field(name="**Link**", value=f"{link}", inline=False)
    return embed


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

    # Example data:
    # {
    #     "data": {
    #         "matchedUser": {
    #             "profile": { "ranking": 552105 , "realName": "XYZ"},
    #             "submitStatsGlobal": {
    #                 "acSubmissionNum": [
    #                 { "difficulty": "All", "count": 118 },
    #                 { "difficulty": "Easy", "count": 43 },
    #                 { "difficulty": "Medium", "count": 63 },
    #                 { "difficulty": "Hard", "count": 12 }
    #                 ]
    #             }
    #         }
    #     }
    # }

    logger.info(
        "file: utils/questions.py ~ get_problems_solved_and_rank ~ data requesting ~ https://leetcode.com/%s", leetcode_username)

    try:
        response = requests.post(
            url, json=data, headers=headers, timeout=5)
    except Exception as e:
        logger.exception(
            "file: utils/questions.py ~ get_problems_solved_and_rank ~ exception: %s", e)
        return None

    if response.status_code != 200:
        return None

    response_data = response.json()

    if response_data["data"]["matchedUser"] is None:
        logger.warning(
            "file: utils/questions.py ~ get_problems_solved_and_rank ~ user not found ~ https://leetcode.com/%s", leetcode_username)
        return None

    logger.info(
        "file: utils/questions.py ~ get_problems_solved_and_rank ~ data requested successfully ~ https://leetcode.com/%s", leetcode_username)

    stats = response_data["data"]["matchedUser"]

    questionsCompleted = {}

    for dic in stats["submitStatsGlobal"]["acSubmissionNum"]:
        questionsCompleted[dic["difficulty"]] = dic["count"]

    stats["submitStatsGlobal"]["acSubmissionNum"] = questionsCompleted

    return stats
