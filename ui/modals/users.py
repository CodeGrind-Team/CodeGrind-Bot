from typing import TYPE_CHECKING

import discord

from utils.users import register

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


class RegisterModal(
    discord.ui.Modal, title="Connect your LeetCode account to CodeGrind"
):
    leetcode_id_answer = discord.ui.TextInput(
        label="Enter your LeetCode ID:", style=discord.TextStyle.short, required=True
    )

    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await register(
            self.bot,
            interaction,
            interaction.response.send_message,
            interaction.guild.id,
            interaction.user.id,
            self.leetcode_id_answer.value,
        )
