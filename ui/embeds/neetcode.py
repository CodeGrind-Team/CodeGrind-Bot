import discord
from typing import TYPE_CHECKING
from constants import Language
from utils.problems import fetch_question_info, search_question
from utils.neetcode import generate_neetcode_link
from ui.embeds.problems import search_question, question_error_embed
if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot

# Neetcode Search by id
async def search_neetcode_embed(bot: "DiscordBot", search_text: str, language: Language) -> discord.Embed:

    try:
        question_title, question_id = await search_question(bot, search_text)
    except:
        return await question_error_embed()
    
    embed = await neetcode_embed(bot, question_id, question_title, language)
    return embed

async def neetcode_embed(bot: "DiscordBot", question_id: str, question_title: str, language: Language) -> discord.Embed:

    info = await fetch_question_info(bot, question_title)
    neetcode_link = await generate_neetcode_link(bot, question_id, question_title, language)
    response = await bot.http_client.fetch_data(neetcode_link, timeout=10)

    if "Not Found" in response:
        return await neetcode_error_embed()

    embed = discord.Embed(
        title=f"{question_id}. {info.title} - {language.value.capitalize()} Solution",
        url=info.link,
        description=f"```python\n{response}```",
        colour=discord.Colour.blue(),
    )
    return embed

async def neetcode_error_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Error",
        description="Failed to fetch Neetcode solution, or no solution exists",
        colour=discord.Colour.red(),
    )
    return embed