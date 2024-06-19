from typing import TYPE_CHECKING

import discord

from constants import Language
from ui.embeds.common import error_embed, failure_embed
from ui.embeds.problems import question_error_embed
from utils.neetcode import neetcode_solution_github_link
from utils.problems import search_question

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


async def search_neetcode_embed(
    bot: "DiscordBot", search_text: str, language: Language
) -> discord.Embed:

    question_title = await search_question(bot, search_text)
    if not question_title:
        return question_error_embed()

    embed = await neetcode_embed(bot, question_title, language)
    return embed


async def neetcode_embed(
    bot: "DiscordBot", question_title: str, language: Language
) -> discord.Embed:
    if question_title not in bot.neetcode.solutions:
        return failure_embed(title="No NeetCode solution exists for this problem")

    info = bot.neetcode.solutions[question_title]
    code_link = neetcode_solution_github_link(info.code, language)
    response_data = await bot.http_client.fetch_data(code_link, timeout=10)
    if not response_data:
        return error_embed()

    if "||" in response_data:
        # `U+200B` is a zero-width space character, this prevents Discord from
        # collapsing the spoiler tag early.
        response_data = response_data.replace("||", "|\u200b|")

    # `" " * 85` is needed to force the code block to span its max possible width.
    code_block = (
        f"**Click to reveal the solution**:\n||```{language.value}\n{' ' * 85}"
        f"\n{response_data}\n```||"
    )

    embed = discord.Embed(
        title=f"{info.problem_id}. {info.name} - NeetCode Solution "
        f"({language.value.capitalize()}) ",
        url="https://neetcode.io/",
        description=code_block,
        colour=discord.Colour.light_embed(),
    )
    embed.add_field(
        name="Video solution", value=f"https://www.youtube.com/embed/{info.video}"
    )
    embed.add_field(name="Pattern", value=f"||{info.pattern}||")

    compiled_groups = []
    if info.blind75:
        compiled_groups.append("Blind 75")
    if info.neetcode150:
        compiled_groups.append("NeetCode 150")

    embed.set_footer(
        text=(
            "This problem is part of " + " and ".join(compiled_groups)
            if compiled_groups
            else ""
        )
    )
    return embed
