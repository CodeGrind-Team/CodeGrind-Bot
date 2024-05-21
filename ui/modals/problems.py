import aiohttp
import discord
from discord.ext import commands

from ui.embeds.problems import search_question_embed


class ProblemSearchModal(discord.ui.Modal, title="Search for a LeetCode problem"):
    search_query_answer = discord.ui.TextInput(
        label="Enter problem name, ID, or URL:",
        style=discord.TextStyle.short,
        required=True,
    )

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        async with aiohttp.ClientSession() as client_session:
            embed = await search_question_embed(
                self.bot, client_session, self.search_query_answer.value
            )

        await interaction.followup.send(embed=embed)
