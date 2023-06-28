import discord
from discord.ext import commands

from bot_globals import logger
from models.server_model import Server
from utils.io_handling import read_file, write_file
from utils.middleware import admins_only, ensure_server_document
from utils.views import ChannelsSelect
from embeds.channels_embeds import channel_receiving_all_notification_types_embed, set_channels_instructions_embed


class Channels(commands.GroupCog, name="notifychannel"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="enable", description="Admins only: Set which channels should receive notifications")
    @ensure_server_document
    @admins_only
    async def enable(self, interaction: discord.Interaction, channel: discord.TextChannel | None = None) -> None:
        logger.info("file: cogs/channels.py ~ setdailychannel ~ run")

        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel) or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(contents="An error has occured! Please try again.", ephemeral=True)
            return

        if channel is None:
            channel = interaction.channel

        logger.info(
            "file: cogs/channels.py ~ setchannels ~ channel id: %s", channel.id)

        server_id = interaction.guild.id

        # TODO: add projection
        server = await Server.find_one(Server.id == server_id)

        if all(channel.id in notification_type[1] for notification_type in server.channels):
            embed = channel_receiving_all_notification_types_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        available_types = [
            notification_type[0] for notification_type in server.channels if channel.id not in notification_type[1]]

        embed = set_channels_instructions_embed(channel.name)
        await interaction.response.send_message(embed=embed, view=ChannelsSelect(server_id, channel.id, channel.name, available_types), ephemeral=True)

    @discord.app_commands.command(name="removedailychannel", description="Remove a daily channel")
    @ensure_server_document
    @admins_only
    async def removedailychannel(self, interaction: discord.Interaction, channel: discord.TextChannel | None = None) -> None:
        logger.info("file: cogs/channels.py ~ removedailychannel ~ run")

        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel) or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(contents="An error has occured! Please try again.", ephemeral=True)
            return

        if channel is None:
            channel = interaction.channel

        server_id = interaction.guild.id

        logger.info(
            "file: cogs/channels.py ~ removedailychannel ~ channel id: %s", channel.id)

        data = await read_file(f"data/{server_id}_leetcode_stats.json")

        if "channels" in data and channel.id in data["channels"]:
            data["channels"].remove(channel.id)

            await write_file(f"data/{server_id}_leetcode_stats.json", data)

            embed = discord.Embed(
                title="Success!",
                description="This channel has been removed!",
                color=discord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="Error!",
                description="This channel was not added!",
                color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(Channels(client))
