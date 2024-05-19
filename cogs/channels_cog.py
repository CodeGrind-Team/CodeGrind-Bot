import discord
from discord.ext import commands

from middleware import (
    admins_only,
    defer_interaction,
    ensure_server_document,
)
from views.channels_views import SelectOperatorView


class NotificationsGroupCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command(
        name="notifications",
        description="Admins only: enable or disable channel notifications",
    )
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @admins_only
    async def notifications(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | None = None,
    ) -> None:
        """
        Command to enable notifications for a channel.

        :param interaction: The Discord interaction.
        :param channel: The text channel to enable notifications for.
        If None, defaults to the channel where the command was invoked.
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


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(NotificationsGroupCog(bot))
