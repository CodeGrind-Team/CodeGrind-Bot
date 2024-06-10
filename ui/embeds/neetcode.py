import requests
import discord
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


async def neetcode_embed(bot: "DiscordBot", question_id: str, question_title: str) -> discord.Embed:

    question_number = question_id.zfill(4)
    neetcode_github_title = f"{question_number}-{question_title.replace(' ', '-').lower()}"
    bot.logger.info(neetcode_github_title)
    neetcode_link = f"https://raw.githubusercontent.com/neetcode-gh/leetcode/main/python/{neetcode_github_title}.py"

    response = requests.get(neetcode_link)

    embed = discord.Embed(
        title=f"{question_id}",
        description=f"{response.text}",
        colour=discord.Colour.blue(),
    )

    return embed
