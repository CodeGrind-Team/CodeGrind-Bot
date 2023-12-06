import discord
import pytz
from beanie.odm.operators.update.general import Set
from discord.ext import commands

from bot_globals import logger
from database.models.server_model import Server
from embeds.admin_embeds import invalid_timezone_embed, timezone_updated_embed
from middleware import (admins_only, defer_interaction, ensure_server_document,
                        track_analytics)


class Channels(commands.GroupCog, name="settings"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="timezone", description="Admins only: Change the timezone")
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @admins_only
    @track_analytics
    async def set_timezone(self, interaction: discord.Interaction, timezone: str) -> None:
        logger.info("file: cogs/admin.py ~ settings timezone ~ run")

        if timezone not in pytz.all_timezones:
            embed = invalid_timezone_embed()
            await interaction.followup.send(embed=embed)
            return

        server_id = interaction.guild.id
        await Server.find_one(Server.id == server_id).update(Set({Server.timezone: timezone}))

        embed = timezone_updated_embed()
        await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Channels(client))
