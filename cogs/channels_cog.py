import discord
from discord.ext import commands

from database.models.server_model import Server
from embeds.channels_embeds import (
    channel_receiving_all_notification_types_embed,
    channel_receiving_no_notification_types_embed,
    set_channels_instructions_embed,
)
from middleware import (
    admins_only,
    defer_interaction,
    ensure_server_document,
    track_analytics,
)
from views.channel_notification_select_view import ChannelsSelectView


class ChannelsGroupCog(commands.GroupCog, name="notify-channel"):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @discord.app_commands.command(
        name="enable",
        description="Admins only: Set which channels should receive notifications",
    )
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @admins_only
    @track_analytics
    async def enable(
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
        if channel is None:
            channel = interaction.channel

        server_id = interaction.guild.id

        server = await Server.find_one(Server.id == server_id)

        if all(
            channel.id in notification_type[1] for notification_type in server.channels
        ):
            embed = channel_receiving_all_notification_types_embed()
            await interaction.followup.send(embed=embed)
            return

        available_notification_types = [
            notification_type[0]
            for notification_type in server.channels
            if channel.id not in notification_type[1]
        ]

        embed = set_channels_instructions_embed(channel.name, adding=True)
        await interaction.followup.send(
            embed=embed,
            view=ChannelsSelectView(
                server_id,
                channel.id,
                channel.name,
                available_notification_types,
                adding=True,
            ),
        )

    @discord.app_commands.command(
        name="disable",
        description="Admins only: Stop channel from receiving selected notification types",
    )
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @admins_only
    @track_analytics
    async def disable(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | None = None,
    ) -> None:
        """
        Command to disable notification for a channel.

        :param interaction: The Discord interaction.
        :param channel: The text channel to disable notifications for.
        If None, defaults to the channel where the command was invoked.
        """
        if not channel:
            channel = interaction.channel

        server_id = interaction.guild.id

        server = await Server.find_one(Server.id == server_id)

        if all(
            channel.id not in notification_type[1]
            for notification_type in server.channels
        ):
            await interaction.followup.send(
                embed=channel_receiving_no_notification_types_embed()
            )
            return

        available_notification_types = [
            notification_type[0]
            for notification_type in server.channels
            if channel.id in notification_type[1]
        ]

        embed = set_channels_instructions_embed(channel.name, adding=False)
        await interaction.followup.send(
            embed=embed,
            view=ChannelsSelectView(
                server_id,
                channel.id,
                channel.name,
                available_notification_types,
                adding=False,
            ),
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(ChannelsGroupCog(client))
