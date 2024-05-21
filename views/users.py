import discord
from discord.ext import commands

from middleware import update_user_preferences_prompt
from modals.users import RegisterModal


class LoginView(discord.ui.View):
    def __init__(self, bot: commands.Bot, *, timeout=180) -> None:
        self.bot = bot
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Connect", style=discord.ButtonStyle.blurple)
    async def connect(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        await interaction.response.send_modal(RegisterModal(self.bot))
        await update_user_preferences_prompt(interaction)
