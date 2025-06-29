from typing import TYPE_CHECKING, cast

import discord
from discord import app_commands
from discord.ext import commands

from src.database.models import User
from src.middleware import defer_interaction, ensure_server_document
from src.ui.constants import BooleanField
from src.ui.embeds.users import (
    account_not_found_embed,
    account_permanently_deleted_embed,
    account_process_start_embed,
    account_removed_embed,
)
from src.utils.common import GuildInteraction
from src.ui.views.users import LoginView
from src.utils.preferences import update_user_preferences_prompt
from src.utils.users import delete_user, login, unlink_user_from_server

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot


class UsersCog(commands.Cog):
    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot

    @app_commands.guild_only()
    @app_commands.command(name="add")
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    async def add(self, interaction: discord.Interaction) -> None:
        """
        Connect your LeetCode account to this server's CodeGrind leaderboards
        """
        guild = cast(discord.Guild, interaction.guild)
        member = cast(discord.Member, interaction.user)

        db_user = await User.find_one(User.id == member.id)

        if db_user:
            await login(
                guild,
                member,
                interaction.followup.send,
            )
        else:
            await interaction.followup.send(
                embed=account_process_start_embed(),
                view=LoginView(self.bot),
            )

    @app_commands.guild_only()
    @app_commands.command(name="update")
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    async def update(self, interaction: discord.Interaction) -> None:
        """
        Update your CodeGrind profile in this server
        """
        user_id = interaction.user.id

        db_user = await User.find_one(User.id == user_id)

        if db_user:
            await update_user_preferences_prompt(cast(GuildInteraction, interaction))
            return

        embed = account_not_found_embed()
        await interaction.followup.send(embed=embed)

    @app_commands.guild_only()
    @app_commands.command(name="remove")
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    async def remove(
        self,
        interaction: discord.Interaction,
        permanently: BooleanField = BooleanField.No,
    ) -> None:
        """
        Remove your profile from this server's leaderboard

        :param permanently: Permanently delete all CodeGrind's stored data on you
        """
        server_id = cast(int, interaction.guild_id)
        user_id = interaction.user.id

        db_user = await User.find_one(User.id == user_id)

        if not db_user:
            await interaction.followup.send(embed=account_not_found_embed())
            return

        embed = None
        if permanently.to_bool:
            await delete_user(user_id)
            embed = account_permanently_deleted_embed()

        else:
            await unlink_user_from_server(user_id, server_id)
            embed = account_removed_embed()

        await interaction.followup.send(embed=embed)


async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(UsersCog(bot))
