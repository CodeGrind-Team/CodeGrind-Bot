import random

import discord
import requests
from discord.ext import commands

from bot_globals import logger
from embeds.misc_embeds import error_embed
from embeds.questions_embeds import (daily_question_embed, question_embed,
                                     question_has_no_rating_embed,
                                     question_rating_embed)
from utils.ratings import get_rating_data_to_thread
from utils.middleware import track_analytics


class Questions(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="daily", description="Returns the daily problem")
    @track_analytics
    async def daily(self, interaction: discord.Interaction) -> None:
        logger.info("file: cogs/questions.py ~ get_daily ~ run")

        await interaction.response.defer()

        embed = await daily_question_embed()

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="rating", description="Returns the Zerotrac rating of the problem")
    @track_analytics
    async def rating(self, interaction: discord.Interaction, question_id_or_title: str) -> None:
        logger.info("file: cogs/questions.py ~ get_rating ~ run")

        await interaction.response.defer()

        rating_data = await get_rating_data_to_thread(question_id_or_title)

        rating_text = "Doesn't exist"

        if rating_data is not None:
            rating_text = f"||{int(rating_data['rating'])}||"

            embed = question_rating_embed(
                rating_data["question_name"], rating_text)

            await interaction.followup.send(embed=embed)
            return

        embed = question_has_no_rating_embed()
        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(
        name="question",
        description="Request a question based on difficulty or at random")
    @track_analytics
    async def get_question(self, interaction: discord.Interaction, difficulty: str = "random") -> None:
        logger.info(
            "file: cogs/questions.py ~ question ~ run ~ difficulty: %s", difficulty)

        difficulty = difficulty.lower()

        await interaction.response.defer()

        try:
            response = requests.get(
                "https://leetcode.com/api/problems/all/", timeout=10)

        except Exception as e:
            logger.exception(
                "file: cogs/questions.py ~ An error occurred while trying to get the question from LeetCode: %s", e)

            embed = error_embed(
                f"An error occurred while trying to get the question from LeetCode. LeetCode may be down.")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if response.status_code != 200:
            logger.exception(
                "file: cogs/questions.py ~ An error occurred while trying to get the question from LeetCode. Error code: %s", response.status_code)

            embed = error_embed(
                f"An error occurred while trying to get the question from LeetCode. LeetCode may be down.")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        data = response.json()

        difficulty_dict = {"easy": 1, "medium": 2, "hard": 3}

        if difficulty in difficulty_dict:
            questions = [
                question for question in data['stat_status_pairs']
                if question['difficulty']['level'] == difficulty_dict[difficulty]
            ]
        else:
            questions = data['stat_status_pairs']

        question = random.choice(questions)

        question_title = question['stat']['question__title']
        question_title_slug = question['stat']['question__title_slug']

        link = f"https://leetcode.com/problems/{question_title_slug}/"

        rating_data = await get_rating_data_to_thread(question_title)

        rating_text = "Doesn't exist"
        if rating_data is not None:
            rating_text = f"||{int(rating_data['rating'])}||"

        embed = question_embed(difficulty, question_title, rating_text, link)
        await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Questions(client))
