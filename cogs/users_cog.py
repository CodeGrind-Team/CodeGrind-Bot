import discord
from discord import app_commands
from discord.ext import commands

from bot import DiscordBot
from database.models.user_model import User
from embeds.users_embeds import (
    account_not_found_embed,
    account_permanently_deleted_embed,
    account_removed_embed,
)
from middleware import defer_interaction, ensure_server_document
from middleware.database_middleware import update_user_preferences_prompt
from utils.users_utils import delete_user, login, unlink_user_from_server
from views.user_views import LoginView


class UsersCog(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    @app_commands.command(name="add")
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    async def add(self, interaction: discord.Interaction) -> None:
        """
        Connect your LeetCode account to this server's CodeGrind leaderboards
        """
        # TODO explain the whole thing and why it has been written the way it is.
        server_id = interaction.guild.id
        user_id = interaction.user.id

        user = await User.find_one(User.id == user_id)

        if user:
            await login(
                interaction,
                interaction.followup.send,
                user_id,
                server_id,
                interaction.user.display_name,
            )
        else:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Connect LeetCode Account",
                    description="Press the following button to start the process:",
                    colour=discord.Colour.blurple(),
                ),
                view=LoginView(self.bot),
            )

    @app_commands.command(name="update")
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    async def update(self, interaction: discord.Interaction) -> None:
        """
        Update your CodeGrind profile in this server
        """
        user_id = interaction.user.id

        user = await User.find_one(User.id == user_id)

        if user:
            await update_user_preferences_prompt(interaction)
            return

        embed = account_not_found_embed()
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="remove")
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    async def remove(
        self, interaction: discord.Interaction, permanently: bool = False
    ) -> None:
        """
        Remove your profile from this server's leaderboard

        :param permanently: Permanently delete all of CodeGrind's stored data on you.
        """
        server_id = interaction.guild.id
        user_id = interaction.user.id

        user = await User.find_one(User.id == user_id)

        if not user:
            await interaction.followup.send(embed=account_not_found_embed())
            return

        embed = None
        if permanently:
            await delete_user(user_id)
            embed = account_permanently_deleted_embed()

        else:
            await unlink_user_from_server(user_id, server_id)
            embed = account_removed_embed()

        await interaction.followup.send(embed=embed)


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(UsersCog(bot))
