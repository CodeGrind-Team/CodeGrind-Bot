import discord
from discord.ext import commands

from bot_globals import logger
from embeds.questions_embeds import daily_question_embed, search_question_embed, random_question_embed
from utils.middleware import track_analytics


class Questions(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="search-question", description="Search for a LeetCode question")
    @track_analytics
    async def display_question(self, interaction: discord.Interaction, name_id_or_url: str) -> None:
        logger.info("file: cogs/questions.py ~ display_question ~ run")

        await interaction.response.defer()

        embed = await search_question_embed(name_id_or_url)

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="daily-question", description="Get the daily question")
    @track_analytics
    async def daily(self, interaction: discord.Interaction) -> None:
        logger.info("file: cogs/questions.py ~ get_daily ~ run")

        await interaction.response.defer()

        embed = await daily_question_embed()

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="random-question", description="Get a random question of your desired difficulty")
    @track_analytics
    async def get_question(self, interaction: discord.Interaction, difficulty: str = "random") -> None:
        logger.info(
            "file: cogs/questions.py ~ question ~ run ~ difficulty: %s", difficulty)

        difficulty = difficulty.lower()

        await interaction.response.defer()

        embed = await random_question_embed(difficulty)

        await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Questions(client))
