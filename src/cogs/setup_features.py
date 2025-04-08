from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from src.middleware import defer_interaction, ensure_server_document
from src.ui.embeds.roles import roles_menu_embed
from src.ui.views.notifications import SelectOperatorView
from src.ui.views.roles import RolesView

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot


class SetupFeatureGroupCog(commands.GroupCog, name="setup-feature"):
    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot

    @app_commands.command(name="notifications")
    @commands.has_permissions(administrator=True)
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    async def notifications(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | None = None,
    ) -> None:
        """
        Admins only: Enable or disable daily channel notifications

        :param channel: The text channel for notifications. Defaults to the current
        channel if not provided.
        """
        if not channel:
            channel = interaction.channel

        await interaction.followup.send(
            embed=discord.Embed(
                description=f"Select whether you want to enable or disable "
                f"notifications in <#{channel.id}>"
            ),
            view=SelectOperatorView(self.bot, channel),
        )

    @app_commands.command(name="roles")
    @commands.has_permissions(administrator=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    async def roles(self, interaction: discord.Interaction) -> None:
        """
        Admins only: Enable or disable CodeGrind roles
        """
        await interaction.followup.send(embed=roles_menu_embed(), view=RolesView())


async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(SetupFeatureGroupCog(bot))
