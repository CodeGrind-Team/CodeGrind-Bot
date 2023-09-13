import discord
import pytz
from beanie.odm.operators.update.general import Set
from discord.ext import commands

from bot_globals import logger
from embeds.admin_embeds import invalid_timezone_embed, timezone_updated_embed
from embeds.misc_embeds import error_embed
from models.server_model import Server
from utils.middleware import (admins_only, ensure_server_document,
                              track_analytics)


class Channels(commands.GroupCog, name="settings"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="timezone", description="Admins only: Change the timezone")
    @ensure_server_document
    @admins_only
    @track_analytics
    async def set_timezone(self, interaction: discord.Interaction, timezone: str) -> None:
        logger.info("file: cogs/admin.py ~ settings timezone ~ run")

        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel) or not isinstance(interaction.user, discord.Member):
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if timezone not in pytz.all_timezones:
            embed = invalid_timezone_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        server_id = interaction.guild.id
        await Server.find_one(Server.id == server_id).update(Set({Server.timezone: timezone}))

        embed = timezone_updated_embed()
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(Channels(client))
