from typing import TYPE_CHECKING, cast

import discord

from src.utils.users import register
from src.utils.common import GuildInteraction

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot


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
        guild_interaction = cast(GuildInteraction, interaction)
        await register(
            self.bot,
            guild_interaction.guild,
            guild_interaction.user,
            guild_interaction.response.send_message,
            guild_interaction.edit_original_response,
            self.leetcode_id_answer.value,
        )
