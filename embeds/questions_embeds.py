from dis import disco

import discord
from utils.questions import (get_daily_question, get_question_info_from_title,
                             get_random_question, search_for_question)


def daily_problem_unsuccessful_embed() -> discord.Embed:
    embed = discord.Embed(title="Daily problem",
                          color=discord.Color.red())

    embed.description = "Daily problem could not be retrieved"

    return embed

def premium_question_embed(frontendId, title, link) -> discord.Embed:
    description = 'Cannot display premium questions.'
    embed = discord.Embed(title=f"{frontendId}. {title}", url=link, description=description, color=discord.Color.red())
    return embed

async def question_embed(question_id_or_title=None, random=False, difficulty="") -> discord.Embed:
    if random:
        question_title_slug = await get_random_question(difficulty)
    else:
        question_title_slug = await search_for_question(question_id_or_title)
    [premium, frontendId, description, constraints, difficulty, title, question_rating, link, total_accepted, total_submission, ac_rate] = await get_question_info_from_title(question_title_slug)

    if premium:
        return premium_question_embed(frontendId, title, link)


    color_dict = {"Easy": discord.Color.green(),
                  "Medium": discord.Color.orange(),
                  "Hard":  discord.Color.red()}

    color = color_dict[difficulty] if difficulty in color_dict else discord.Color.blue()

    embed = discord.Embed(title=f"{frontendId}. {title}", url=link, description=description, color=color)
    
    embed.add_field(name='Constraints: ', value=constraints, inline=False)

    embed.add_field(name='Difficulty: ', value=difficulty, inline=True)

    if question_rating is not None:
        embed.add_field(name="Zerotrac Rating: ", value=question_rating, inline=True)

    embed.set_footer(text=f"Accepted: {total_accepted}  |  Submissions: {total_submission}  |  Acceptance Rate: {ac_rate}")

    return embed

async def daily_question_embed() -> discord.Embed:
    question_title_slug = await get_daily_question()
    [premium, frontendId, description, constraints, difficulty, title, question_rating, link, total_accepted, total_submission, ac_rate] = await get_question_info_from_title(question_title_slug)

    color_dict = {"Easy": discord.Color.green(),
                  "Medium": discord.Color.orange(),
                  "Hard":  discord.Color.red()}

    color = color_dict[difficulty] if difficulty in color_dict else discord.Color.blue()

    embed = discord.Embed(title=f"{frontendId}. {title}", url=link, description=description, color=color)
    
    embed.add_field(name='Constraints: ', value=constraints, inline=False)

    embed.add_field(name='Difficulty: ', value=difficulty, inline=True)

    embed.set_author(name="Daily Question")

    if question_rating is not None:
        embed.add_field(name="Zerotrac Rating: ", value=question_rating, inline=True)

    embed.set_footer(text=f"Accepted: {total_accepted}  |  Submissions: {total_submission}  |  Acceptance Rate: {ac_rate}")

    return embed

def question_rating_embed(question_title: str, question_rating: str) -> discord.Embed:
    embed = discord.Embed(title="Zerotrac Rating",
                          color=discord.Color.magenta())

    embed.add_field(name="Question Name",
                    value=question_title.title(), inline=False)
    embed.add_field(name="Rating", value=question_rating, inline=False)

    return embed

def question_has_no_rating_embed() -> discord.Embed:
    embed = discord.Embed(title="Zerotrac Rating",
                          color=discord.Color.red())

    embed.description = "This question doesn't have a Zerotrac rating"

    return embed


