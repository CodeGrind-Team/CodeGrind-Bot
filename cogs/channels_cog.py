import discord
from discord.ext import commands

from bot_globals import logger
from database.models.server_model import Server
from embeds.channels_embeds import (
    channel_receiving_all_notification_types_embed,
    channel_receiving_no_notification_types_embed,
    set_channels_instructions_embed)
from middleware import (admins_only, defer_interaction, ensure_server_document,
                        track_analytics)
from utils.views_utils import ChannelsSelectView


class Channels(commands.GroupCog, name="notify-channel"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="enable", description="Admins only: Set which channels should receive notifications")
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @admins_only
    @track_analytics
    async def enable(self, interaction: discord.Interaction, channel: discord.TextChannel | None = None) -> None:
        logger.info("file: cogs/channels.py ~ notify-channel enable ~ run")

        if channel is None:
            channel = interaction.channel

        logger.info(
            "file: cogs/channels.py ~ notify-channel enable ~ channel id: %s", channel.id)

        server_id = interaction.guild.id

        # TODO: add projection
        server = await Server.find_one(Server.id == server_id)

        if all(channel.id in notification_type[1] for notification_type in server.channels):
            embed = channel_receiving_all_notification_types_embed()
            await interaction.followup.send(embed=embed)
            return

        available_types = [
            notification_type[0] for notification_type in server.channels if channel.id not in notification_type[1]]

        embed = set_channels_instructions_embed(channel.name, adding=True)
        await interaction.followup.send(embed=embed, view=ChannelsSelectView(server_id, channel.id, channel.name, available_types, adding=True))

    @discord.app_commands.command(name="disable", description="Admins only: Stop channel from receiving selected notification types")
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @admins_only
    @track_analytics
    async def disable(self, interaction: discord.Interaction, channel: discord.TextChannel | None = None) -> None:
        logger.info("file: cogs/channels.py ~ notify-channel disable ~ run")

        if channel is None:
            channel = interaction.channel

        logger.info(
            "file: cogs/channels.py ~ notify-channel disable ~ channel id: %s", channel.id)

        server_id = interaction.guild.id

        # TODO: add projection
        server = await Server.find_one(Server.id == server_id)

        if all(channel.id not in notification_type[1] for notification_type in server.channels):
            embed = channel_receiving_no_notification_types_embed()
            await interaction.followup.send(embed=embed)
            return

        available_types = [
            notification_type[0] for notification_type in server.channels if channel.id in notification_type[1]]

        embed = set_channels_instructions_embed(channel.name, adding=False)
        await interaction.followup.send(embed=embed, view=ChannelsSelectView(server_id, channel.id, channel.name, available_types, adding=False))


async def setup(client: commands.Bot):
    await client.add_cog(Channels(client))
