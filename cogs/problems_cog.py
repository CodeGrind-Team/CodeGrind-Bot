import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from bot import DiscordBot
from constants import Difficulty
from embeds.questions_embeds import daily_question_embed, random_question_embed
from middleware import defer_interaction
from modals.problems_modal import ProblemSearchModal


class ProblemsCog(commands.GroupCog, name="problem"):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    @app_commands.command(name="search")
    async def search_problem(self, interaction: discord.Interaction) -> None:
        """
        Search for a LeetCode problem
        """
        await interaction.response.send_modal(ProblemSearchModal(self.bot))

    @app_commands.command(name="daily")
    @defer_interaction()
    async def daily_problem(self, interaction: discord.Interaction) -> None:
        """
        Get LeetCode's problem of the day
        """
        async with aiohttp.ClientSession() as client_session:
            embed = await daily_question_embed(self.bot, client_session)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="random")
    @defer_interaction()
    async def random_problem(
        self,
        interaction: discord.Interaction,
        difficulty: Difficulty = Difficulty.RANDOM,
    ) -> None:
        """
        Get a random LeetCode problem of your chosen difficulty

        :param difficulty: The desired difficulty level for the problem
        """
        async with aiohttp.ClientSession() as client_session:
            embed = await random_question_embed(self.bot, client_session, difficulty)

        await interaction.followup.send(embed=embed)


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(ProblemsCog(bot))
