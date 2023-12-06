import discord

from utils.questions_utils import (get_daily_question, get_question_info_from_title,
                                   get_random_question, search_question)


async def daily_question_embed() -> discord.Embed:
    question_title = await get_daily_question()

    if not question_title:
        return question_error_embed()

    embed = await question_embed(question_title)
    return embed


async def search_question_embed(search_text) -> discord.Embed:
    question_title = await search_question(search_text)

    if not question_title:
        return question_error_embed()

    embed = await question_embed(question_title)
    return embed


async def random_question_embed(difficulty: str) -> discord.Embed:
    question_title = await get_random_question(difficulty)

    if not question_title:
        return question_error_embed()

    embed = await question_embed(question_title)
    return embed


async def question_embed(question_title: str) -> discord.Embed:
    info = await get_question_info_from_title(question_title)

    if not info:
        return question_error_embed()

    premium, question_id, difficulty, title, link, total_accepted, total_submission, ac_rate, question_rating, description, constraints = info

    color_dict = {"Easy": discord.Color.green(),
                  "Medium": discord.Color.orange(),
                  "Hard":  discord.Color.red()}
    color = color_dict[difficulty] if difficulty in color_dict else discord.Color.blue()

    if premium:
        return premium_question_embed(question_id, title, link, color)

    embed = discord.Embed(
        title=f"{question_id}. {title}", url=link, description=description, color=color)

    embed.add_field(name='Constraints: ', value=constraints, inline=False)

    embed.add_field(name='Difficulty: ', value=difficulty, inline=True)

    if question_rating is not None:
        embed.add_field(name="Zerotrac Rating: ",
                        value=question_rating, inline=True)

    embed.set_footer(
        text=f"Accepted: {total_accepted}  |  Submissions: {total_submission}  |  Acceptance Rate: {ac_rate}")

    return embed


def premium_question_embed(question_id, title, link, color: discord.Color) -> discord.Embed:
    embed = discord.Embed(
        title=f"{question_id}. {title}", url=link, color=color)

    embed.description = 'Cannot display premium questions'

    return embed


def question_error_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Question could not be found", color=discord.Color.red())
    return embed
