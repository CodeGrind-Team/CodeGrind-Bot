import re

import discord
from discord.ext import commands

from bot_globals import client, logger
from embeds.questions_embeds import (daily_question_embed,
                                     random_question_embed,
                                     search_question_embed)
from embeds.stats_embeds import stats_embed
from utils.middleware import track_analytics


class Questions(commands.GroupCog, name="question"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="search", description="Search for a LeetCode question")
    @track_analytics
    async def search_question(self, interaction: discord.Interaction, name_id_or_url: str) -> None:
        logger.info("file: cogs/questions.py ~ display_question ~ run")

        await interaction.response.defer()

        embed = await search_question_embed(name_id_or_url)

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="daily", description="Get the daily question")
    @track_analytics
    async def daily_question(self, interaction: discord.Interaction) -> None:
        logger.info("file: cogs/questions.py ~ get_daily ~ run")

        await interaction.response.defer()

        embed = await daily_question_embed()

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="random", description="Get a random question of your desired difficulty")
    @track_analytics
    async def random_question(self, interaction: discord.Interaction, difficulty: str = "random") -> None:
        logger.info(
            "file: cogs/questions.py ~ question ~ run ~ difficulty: %s", difficulty)

        difficulty = difficulty.lower()

        await interaction.response.defer()

        embed = await random_question_embed(difficulty)

        await interaction.followup.send(embed=embed)


@client.event
async def on_message(message: discord.Message):
    question_pattern = r'https://leetcode.com/problems/([\w-]+)/'
    profile_pattern = r'https://leetcode.com/([\w-]+)/(?:\s|$)'

    if question_match := re.search(question_pattern, message.content):
        # group(1) will return the 1st capture (stuff within the brackets).
        question_title = question_match.group(1)

        logger.info(
            "file: cogs/questions.py ~ on_message ~ question match found: %s", question_title)

        embed = await search_question_embed(question_title)

        # Only surpress message if it only contains the url.
        if question_match == message.content:
            await message.edit(suppress=True)

        await message.channel.send(embed=embed, silent=True, reference=message)

        logger.info(
            "file: cogs/questions.py ~ on_message ~ question sent successfully: %s", question_title)

    elif profile_match := re.search(profile_pattern, message.content):
        leetcode_id = profile_match.group(1)

        embed, file = await stats_embed(leetcode_id, leetcode_id)

        # Only surpress message if it only contains the url.
        if question_match == message.content:
            await message.edit(suppress=True)

        if file is None:
            await message.channel.send(embed=embed, silent=True, reference=message)
        else:
            await message.channel.send(embed=embed, file=file, silent=True, reference=message)

        logger.info(
            "file: cogs/questions.py ~ on_message ~ profile sent successfully: %s", leetcode_id)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Questions(client))
