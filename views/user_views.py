import discord
from discord.ext import commands

from database.models.user_model import User
from middleware.database_middleware import update_user_preferences_prompt
from modals.register_modal import RegisterModal
from utils.users_utils import login


class RegisterOrLoginView(discord.ui.View):
    def __init__(self, bot: commands.Bot, *, timeout=180) -> None:
        self.bot = bot
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Connect", style=discord.ButtonStyle.blurple)
    async def connect(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        server_id = interaction.guild.id
        user_id = interaction.user.id

        user = await User.find_one(User.id == user_id)

        if user:
            await login(
                interaction,
                interaction.response.send_message,
                user_id,
                server_id,
                interaction.user.display_name,
            )
        else:
            await interaction.response.send_modal(RegisterModal(self.bot))

        await update_user_preferences_prompt(interaction)
