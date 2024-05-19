import aiohttp
import discord
from discord.ext import commands

from constants import Difficulty
from embeds.questions_embeds import (
    daily_question_embed,
    random_question_embed,
    search_question_embed,
)
from middleware import defer_interaction, track_analytics


class QuestionsCog(commands.GroupCog, name="problem"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command(
        name="search", description="Search for a LeetCode problem"
    )
    @defer_interaction()
    @track_analytics
    async def search_problem(
        self, interaction: discord.Interaction, name_id_or_url: str
    ) -> None:
        """
        Command to search for a LeetCode question.

        :param interaction: The Discord interaction.
        :param name_id_or_url: The name, ID, or URL of the question to search.
        """
        # TODO: use modal
        async with aiohttp.ClientSession() as client_session:
            # TODO rename to search_problem
            embed = await search_question_embed(
                self.bot, client_session, name_id_or_url
            )

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(
        name="daily", description="Get the problem of the day"
    )
    @defer_interaction()
    @track_analytics
    async def daily_question(self, interaction: discord.Interaction) -> None:
        """
        Command to get the daily question.

        :param interaction: The Discord interaction.
        """
        async with aiohttp.ClientSession() as client_session:
            embed = await daily_question_embed(self.bot, client_session)

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(
        name="random", description="Get a random problem of your chosen difficulty"
    )
    @defer_interaction()
    @track_analytics
    async def random_question(
        self,
        interaction: discord.Interaction,
        difficulty: Difficulty = Difficulty.RANDOM,
    ) -> None:
        """
        Command to get a random question of the selected difficulty.

        :param interaction: The Discord interaction.
        :param difficulty: The desired difficulty level of the question.
        """
        async with aiohttp.ClientSession() as client_session:
            embed = await random_question_embed(self.bot, client_session, difficulty)

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(QuestionsCog(bot))
