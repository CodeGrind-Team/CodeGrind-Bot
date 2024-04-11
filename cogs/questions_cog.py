import discord
from discord.ext import commands

from constants import Difficulty
from embeds.questions_embeds import (
    daily_question_embed,
    random_question_embed,
    search_question_embed,
)
from middleware import defer_interaction, track_analytics


class QuestionsCog(commands.GroupCog, name="question"):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @discord.app_commands.command(
        name="search", description="Search for a LeetCode question"
    )
    @defer_interaction()
    @track_analytics
    async def search_question(
        self, interaction: discord.Interaction, name_id_or_url: str
    ) -> None:
        """
        Command to search for a LeetCode question.

        :param interaction: The interaction context.
        :param name_id_or_url: The name, ID, or URL of the question to search.
        """
        embed = await search_question_embed(name_id_or_url)
        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="daily", description="Get the daily question")
    @defer_interaction()
    @track_analytics
    async def daily_question(self, interaction: discord.Interaction) -> None:
        """
        Command to get the daily question.

        :param interaction: The interaction context.
        """
        embed = await daily_question_embed()
        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(
        name="random", description="Get a random question of your desired difficulty"
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

        :param interaction: The interaction context.
        :param difficulty: The desired difficulty level of the question.
        """
        embed = await random_question_embed(difficulty)
        await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(QuestionsCog(client))
