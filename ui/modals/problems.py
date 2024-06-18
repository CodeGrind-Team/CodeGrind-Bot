from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


class ProblemSearchModal(discord.ui.Modal, title="Search for a LeetCode problem"):
    search_query_answer = discord.ui.TextInput(
        label="Enter problem name, ID, or URL:",
        style=discord.TextStyle.short,
        required=True,
    )

    def __init__(self, bot: "DiscordBot", search_embed_creator) -> None:
        self.bot = bot
        self.search_embed_creator = search_embed_creator
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        embed = await self.search_embed_creator(
            self.bot, self.search_query_answer.value
        )
        await interaction.followup.send(embed=embed)
