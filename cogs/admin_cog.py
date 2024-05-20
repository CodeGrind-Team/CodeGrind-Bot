import discord
import pytz
from beanie.odm.operators.update.general import Set
from discord.ext import commands

from bot import DiscordBot
from database.models.server_model import Server
from embeds.admin_embeds import invalid_timezone_embed, timezone_updated_embed
from middleware import defer_interaction, ensure_server_document


class AdminGroupCog(commands.GroupCog, name="settings"):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    async def _timezone_autocomplete(
        self, _: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice[str]]:
        """
        Autocomplete handler for timezone selection.
        """
        # Doesn't show anything if nothing was typed in the field.
        if not current:
            return []

        # Number of choices is capped at 25.
        choices = [
            discord.app_commands.Choice(name=choice, value=choice)
            for choice in pytz.common_timezones_set
            if current.lower() in choice.lower()
        ][:25]

        return choices

    @discord.app_commands.command(
        name="timezone", description="Admins only: Change the server's timezone"
    )
    @discord.app_commands.autocomplete(timezone=_timezone_autocomplete)
    @commands.has_permissions(administrator=True)
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    async def set_timezone(
        self, interaction: discord.Interaction, timezone: str
    ) -> None:
        """
        Admins only: change the leaderboards' timezone.

        :param timezone: Type your timezone.
        """
        if timezone not in pytz.common_timezones_set:
            await interaction.followup.send(embed=invalid_timezone_embed())
            return

        # Update server's timezone field.
        await Server.find_one(Server.id == interaction.guild.id).update(
            Set({Server.timezone: timezone})
        )

        await interaction.followup.send(embed=timezone_updated_embed())


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(AdminGroupCog(bot))
