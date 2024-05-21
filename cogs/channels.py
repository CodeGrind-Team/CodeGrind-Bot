from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from middleware import defer_interaction, ensure_server_document
from ui.views.channels import SelectOperatorView

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


class NotificationsCog(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
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
        Admins only: enable/disable daily channel notifications

        :param channel: The text channel to enable notifications for.
        If none provided, defaults to the channel where the command was ran.
        """
        if not channel:
            channel = interaction.channel

        await interaction.followup.send(
            embed=discord.Embed(
                description=f"Select whether you want to enable or disable \
                    notifications in <#{channel.id}>"
            ),
            view=SelectOperatorView(self.bot, channel),
        )


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(NotificationsCog(bot))
