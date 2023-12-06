import re

import discord
from discord.ext import commands

from bot_globals import logger
from embeds.questions_embeds import (daily_question_embed,
                                     random_question_embed,
                                     search_question_embed)
from middleware import track_analytics, defer_interaction


class Questions(commands.GroupCog, name="question"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="search", description="Search for a LeetCode question")
    @defer_interaction()
    @track_analytics
    async def search_question(self, interaction: discord.Interaction, name_id_or_url: str) -> None:
        logger.info("file: cogs/questions.py ~ display_question ~ run")

        embed = await search_question_embed(name_id_or_url)

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="daily", description="Get the daily question")
    @defer_interaction()
    @track_analytics
    async def daily_question(self, interaction: discord.Interaction) -> None:
        logger.info("file: cogs/questions.py ~ get_daily ~ run")

        embed = await daily_question_embed()

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="random", description="Get a random question of your desired difficulty")
    @defer_interaction()
    @track_analytics
    async def random_question(self, interaction: discord.Interaction, difficulty: str = "random") -> None:
        logger.info(
            "file: cogs/questions.py ~ question ~ run ~ difficulty: %s", difficulty)

        difficulty = difficulty.lower()

        embed = await random_question_embed(difficulty)

        await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Questions(client))
