from typing import TYPE_CHECKING, cast

import discord

from src.ui.modals.users import RegisterModal
from src.utils.common import GuildInteraction
from src.utils.preferences import update_user_preferences_prompt

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot


class LoginView(discord.ui.View):
    def __init__(self, bot: "DiscordBot", *, timeout=180) -> None:
        self.bot = bot
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Connect", style=discord.ButtonStyle.blurple)
    async def connect(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        await interaction.response.send_modal(RegisterModal(self.bot))
        await update_user_preferences_prompt(cast(GuildInteraction, interaction))
