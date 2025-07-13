from enum import Enum
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from src.constants import Difficulty, ProblemList
from src.middleware import defer_interaction
from src.ui.embeds.problems import (
    daily_question_embed,
    random_question_embed,
    search_question_embed,
)
from src.ui.modals.problems import ProblemSearchModal

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot


class ProblemsCog(commands.GroupCog, name="problem"):
    class DifficultyField(Enum):
        Easy = Difficulty.EASY
        Medium = Difficulty.MEDIUM
        Hard = Difficulty.HARD
        Random = Difficulty.RANDOM

    class ProblemListField(Enum):
        LeetCode_All = ProblemList.LEETCODE_ALL
        Grind_75 = ProblemList.GRIND_75
        Blind_75 = ProblemList.BLIND_75
        NeetCode_150 = ProblemList.NEETCODE_150
        NeetCode_250 = ProblemList.NEETCODE_250
        NeetCode_All = ProblemList.NEETCODE_ALL

    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot

    @app_commands.command(name="search")
    async def search_problem(self, interaction: discord.Interaction) -> None:
        """
        Search for a LeetCode problem
        """
        await interaction.response.send_modal(
            ProblemSearchModal(self.bot, search_question_embed)
        )

    @app_commands.command(name="daily")
    @defer_interaction()
    async def daily_problem(self, interaction: discord.Interaction) -> None:
        """
        Get LeetCode's problem of the day
        """
        embed = await daily_question_embed(self.bot)

        try:
            await interaction.followup.send(embed=embed)
        except discord.errors.HTTPException:
            self.bot.logger.exception(
                "HTTPException raised when trying to share daily questions to channel "
                f"with ID: {interaction.channel_id}. Embed length over limit."
            )

    @app_commands.command(name="random")
    @defer_interaction()
    async def random_problem(
        self,
        interaction: discord.Interaction,
        difficulty: DifficultyField = DifficultyField.Random,
        problem_list: ProblemListField = ProblemListField.LeetCode_All,
    ) -> None:
        """
        Get a random LeetCode problem of your chosen difficulty

        :param difficulty: The desired difficulty level
        :param problem_list: Grind 75, Blind 75, NeetCode 150, etc...
        """
        embed = await random_question_embed(
            self.bot, difficulty.value, problem_list.value
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(ProblemsCog(bot))
