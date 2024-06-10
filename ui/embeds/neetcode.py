import requests
import discord
from typing import TYPE_CHECKING
from ui.embeds.problems import search_question, question_error_embed
if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


# Neetcode Search by id
async def search_neetcode_embed(bot: "DiscordBot", search_text: str) -> discord.Embed:
    question_title, question_id = await search_question(bot, search_text)

    if not question_id:
        return question_error_embed()
    embed = await neetcode_embed(bot, question_id, question_title)
    return embed

async def neetcode_embed(bot: "DiscordBot", question_id: str, question_title: str) -> discord.Embed:

    question_number = question_id.zfill(4)
    neetcode_github_title = f"{question_number}-{question_title.replace(' ', '-').lower()}"
    neetcode_link = f"https://raw.githubusercontent.com/neetcode-gh/leetcode/main/python/{neetcode_github_title}.py"

    response = await bot.http_client.fetch_data(neetcode_link, timeout=10)
    if not response:
        return 

    embed = discord.Embed(
        title=f"{question_id}",
        description=f"{response}",
        colour=discord.Colour.blue(),
    )
    return embed