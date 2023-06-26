import random

import discord
import requests
from discord.ext import commands

from bot_globals import logger, session
from embeds.questions_embeds import daily_question_embed, question_embed


class Questions(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="daily", description="Returns the daily problem")
    async def daily(self, interaction: discord.Interaction) -> None:
        logger.info("file: cogs/questions.py ~ get_daily ~ run")

        embed = daily_question_embed()

        await interaction.response.send_message(embed=embed)
        return

    @discord.app_commands.command(
        name="question",
        description="Request a question based on difficulty or at random")
    async def question(self, interaction: discord.Interaction, difficulty: str = "random") -> None:
        logger.info(
            "file: cogs/questions.py ~ question ~ run ~ difficulty: %s", difficulty)

        difficulty = difficulty.lower()

        if difficulty not in ["easy", "medium", "hard"]:
            link = session.get(
                'https://leetcode.com/problems/random-one-question/all').url

            # TODO: add try catch

            question_title_slug = " ".join(
                link.split("/")[-2].split("-")).capitalize()

            embed = question_embed("random", question_title_slug, link)

            await interaction.response.send_message(embed=embed)
            return

        response = requests.get(
            "https://leetcode.com/api/problems/all/", timeout=5)

        if response.status_code != 200:
            await interaction.response.send_message(
                "An error occurred while trying to get the question from LeetCode")
            return

        data = response.json()

        difficulty_dict = {"easy": 1, "medium": 2, "hard": 3}

        questions = [
            question for question in data['stat_status_pairs']
            if question['difficulty']['level'] == difficulty_dict[difficulty]
        ]

        question = random.choice(questions)

        question_title = question['stat']['question__title']
        question_title_slug = question['stat']['question__title_slug']

        link = f"https://leetcode.com/problems/{question_title_slug}/"

        embed = question_embed(difficulty, question_title, link)
        await interaction.response.send_message(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Questions(client))
