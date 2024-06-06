from typing import TYPE_CHECKING

import discord

from ui.embeds.problems import search_question_embed

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


class ProblemSearchModal(discord.ui.Modal, title="Search for a LeetCode problem"):
    search_query_answer = discord.ui.TextInput(
        label="Enter problem name, ID, or URL:",
        style=discord.TextStyle.short,
        required=True,
    )

    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        embed = await search_question_embed(self.bot, self.search_query_answer.value)

        await interaction.followup.send(embed=embed)
