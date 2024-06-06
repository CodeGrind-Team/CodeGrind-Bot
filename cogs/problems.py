from enum import Enum
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from constants import Difficulty
from middleware import defer_interaction
from ui.embeds.problems import daily_question_embed, random_question_embed
from ui.modals.problems import ProblemSearchModal

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


class ProblemsCog(commands.GroupCog, name="problem"):
    class DifficultyField(Enum):
        Easy = Difficulty.EASY
        Medium = Difficulty.MEDIUM
        Hard = Difficulty.HARD
        Random = Difficulty.RANDOM

    def __init__(self, bot: "DiscordBot") -> None:
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
        embed = await daily_question_embed(self.bot)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="random")
    @defer_interaction()
    async def random_problem(
        self,
        interaction: discord.Interaction,
        difficulty: DifficultyField = DifficultyField.Random,
    ) -> None:
        """
        Get a random LeetCode problem of your chosen difficulty

        :param difficulty: The desired difficulty level
        """
        embed = await random_question_embed(self.bot, difficulty.value)
        await interaction.followup.send(embed=embed)


async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(ProblemsCog(bot))
