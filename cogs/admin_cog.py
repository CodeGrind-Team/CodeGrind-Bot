import discord
import pytz
from beanie.odm.operators.update.general import Set
from discord.ext import commands

from database.models.server_model import Server
from embeds.admin_embeds import invalid_timezone_embed, timezone_updated_embed
from middleware import (
    admins_only,
    defer_interaction,
    ensure_server_document,
)


class AdminGroupCog(commands.GroupCog, name="settings"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command(
        name="timezone", description="Admins only: Change the server's timezone"
    )
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @admins_only
    async def set_timezone(
        self, interaction: discord.Interaction, timezone: str
    ) -> None:
        """
        Command to change the server timezone.

        :param interaction: The Discord interaction.
        :param timezone: The PYTZ timezone to set on the server.
        """
        if timezone not in pytz.all_timezones:
            embed = invalid_timezone_embed()
            await interaction.followup.send(embed=embed)
            return

        await Server.find_one(Server.id == interaction.guild.id).update(
            Set({Server.timezone: timezone})
        )

        await interaction.followup.send(embed=timezone_updated_embed())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminGroupCog(bot))
