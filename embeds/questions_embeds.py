import discord
import requests

from bot_globals import logger
from utils.ratings import get_rating_data


def daily_question_embed() -> discord.Embed:
    logger.info(
        "file: embeds/questions_embeds.py ~ daily_question_embed ~ run")

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
        response = requests.post(url, json=data, headers=headers, timeout=10)

    except Exception as e:
        logger.exception(
            "file: utils/questions.py ~ daily_question_embed ~ exception: %s", e)

        return daily_problem_unsuccessful_embed()

    if response.status_code != 200:
        return daily_problem_unsuccessful_embed()

    response_data = response.json()

    question_title = response_data['data']['challenge']['question']['title']
    difficulty = response_data['data']['challenge']['question']['difficulty']

    link = f"https://leetcode.com{response_data['data']['challenge']['link']}"

    rating_data = get_rating_data(question_title)

    rating_text = "Doesn't exist"
    if rating_data is not None:
        rating_text = f"||{int(rating_data['rating'])}||"

    return question_embed(difficulty, question_title, rating_text, link, daily_question=True)


def daily_problem_unsuccessful_embed() -> discord.Embed:
    embed = discord.Embed(title="Daily problem",
                          color=discord.Color.red())

    embed.description = "Daily problem could not be retrieved"

    return embed


def question_embed(difficulty: str, question_title: str, rating_text: str, link: str, daily_question: bool = False) -> discord.Embed:
    if daily_question:
        question_title = "Daily Question: " + question_title

    color_dict = {"easy": discord.Color.green(),
                  "medium": discord.Color.orange(),
                  "hard":  discord.Color.red()}

    color = color_dict[difficulty] if difficulty in color_dict else discord.Color.blue()

    embed = discord.Embed(title=question_title, color=color)

    embed.add_field(name=difficulty.capitalize(), value=link, inline=False)

    embed.add_field(name="Zerotrac Rating", value=rating_text, inline=False)

    return embed


def question_rating_embed(question_title: str, rating_text: str) -> discord.Embed:
    embed = discord.Embed(title="Zerotrac Rating",
                          color=discord.Color.magenta())

    embed.add_field(name="Question Name",
                    value=question_title.title(), inline=False)
    embed.add_field(name="Rating", value=rating_text, inline=False)

    return embed


def question_has_no_rating_embed() -> discord.Embed:
    embed = discord.Embed(title="Zerotrac Rating",
                          color=discord.Color.red())

    embed.description = "This question doesn't have a Zerotrac rating"

    return embed
