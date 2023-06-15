import discord
from discord.ext import commands

from bot_globals import logger
from utils.io_handling import read_file, write_file


class Channels(commands.Cog):
    def __init__(self, client):
        self.client = client

    @discord.app_commands.command(name="setdailychannel", description="Set where the daily problem will be sent")
    async def setdailychannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        logger.info("file: cogs/channels.py ~ setdailychannel ~ run")

        if channel is None:
            channel = interaction.channel

        server_id = interaction.guild.id

        logger.info(
            "file: cogs/channels.py ~ setdailychannel ~ channel id: %s", channel.id)

        # only allow this command to be used by users with the administrator permission
        if interaction.user.guild_permissions.administrator:
            data = await read_file(f"data/{server_id}_leetcode_stats.json")

            if "channels" not in data:
                data["channels"] = []

            if channel.id in data["channels"]:
                embed = discord.Embed(
                    title="Error!",
                    description="This channel has already been added!",
                    color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            else:
                data["channels"].append(channel.id)

                await write_file(f"data/{server_id}_leetcode_stats.json", data)

                embed = discord.Embed(
                    title="Success!",
                    description="This channel has now been added!",
                    color=discord.Color.green())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        else:
            embed = discord.Embed(
                title="Error!",
                description="You do not have the administrator permission!",
                color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

    @discord.app_commands.command(name="removedailychannel", description="Remove a daily channel")
    async def removedailychannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        logger.info("file: cogs/channels.py ~ removedailychannel ~ run")

        if channel is None:
            channel = interaction.channel

        server_id = interaction.guild.id

        logger.info(
            "file: cogs/channels.py ~ removedailychannel ~ channel id: %s", channel.id)

        # only allow this command to be used by users with the administrator permission
        if interaction.user.guild_permissions.administrator:
            data = await read_file(f"data/{server_id}_leetcode_stats.json")

            if "channels" in data and channel.id in data["channels"]:
                data["channels"].remove(channel.id)

                await write_file(f"data/{server_id}_leetcode_stats.json", data)

                embed = discord.Embed(
                    title="Success!",
                    description="This channel has been removed!",
                    color=discord.Color.green())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            else:
                embed = discord.Embed(
                    title="Error!",
                    description="This channel was not added!",
                    color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        else:
            embed = discord.Embed(
                title="Error!",
                description="You do not have the administrator permission!",
                color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return


async def setup(client):
    await client.add_cog(Channels(client))
