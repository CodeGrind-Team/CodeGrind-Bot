from typing import TYPE_CHECKING

import discord

from constants import Language
from ui.embeds.common import error_embed
from ui.embeds.problems import question_error_embed
from utils.neetcode import generate_neetcode_link
from utils.problems import fetch_question_info, search_question

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


async def search_neetcode_embed(
    bot: "DiscordBot", search_text: str, language: Language
) -> discord.Embed:

    question_info = await search_question(bot, search_text)
    if not question_info:
        return question_error_embed()

    question_title, question_id = question_info
    embed = await neetcode_embed(bot, question_id, question_title, language)
    return embed


async def neetcode_embed(
    bot: "DiscordBot", question_id: str, question_title: str, language: Language
) -> discord.Embed:
    info = await fetch_question_info(bot, question_title)
    neetcode_link = generate_neetcode_link(question_id, question_title, language)
    response_data = await bot.http_client.fetch_data(neetcode_link, timeout=10)
    if not response_data:
        return error_embed()

    embed = discord.Embed(
        title=f"{question_id}. {info.title} - NeetCode Solution "
        f"({language.value.capitalize()}) ",
        url="https://neetcode.io/",
        # `" " * 85` is needed to force the code block to span its max possible width.
        description=f"```{language.value}\n{' ' * 85}\n{response_data}\n```",
        colour=discord.Colour.light_embed(),
    )
    return embed
