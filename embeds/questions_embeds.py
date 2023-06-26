import discord
import requests

from bot_globals import logger


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
        response = requests.post(url, json=data, headers=headers, timeout=5)

    except Exception as e:
        logger.exception(
            "file: utils/questions.py ~ daily_question_embed ~ exception: %s", e)

        return daily_problem_unsuccessful_embed()

    if response.status_code != 200:
        return daily_problem_unsuccessful_embed()

    response_data = response.json()

    question_name = response_data['data']['challenge']['question']['title']
    difficulty = response_data['data']['challenge']['question']['difficulty']

    link = f"https://leetcode.com{response_data['data']['challenge']['link']}"

    return daily_problem_successful_embed(link, question_name, difficulty)


def daily_problem_successful_embed(link: str, question_name: str, difficulty: str) -> discord.Embed:
    embed = discord.Embed(title=f"Daily Problem: {question_name}",
                          color=discord.Color.blue())
    embed.add_field(name="**Difficulty**",
                    value=f"{difficulty}", inline=True)
    embed.add_field(name="**Link**", value=f"{link}", inline=False)

    return embed


def daily_problem_unsuccessful_embed() -> discord.Embed:
    embed = discord.Embed(title="Daily problem",
                          color=discord.Color.red())

    embed.description = "Daily problem could not be retrieved"

    return embed


def question_embed(difficulty: str, question_title: str, link: str) -> discord.Embed:
    color_dict = {"easy": discord.Color.green(),
                  "medium": discord.Color.orange(),
                  "hard":  discord.Color.red()}

    color = color_dict[difficulty] if difficulty in color_dict else discord.Color.blue()

    embed = discord.Embed(title=question_title,
                          color=color)
    embed.add_field(name=difficulty.capitalize(),
                    value=link, inline=False)

    return embed
