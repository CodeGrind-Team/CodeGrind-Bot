import discord
from discord.ext import commands

from bot_globals import logger


class Channels(commands.Cog):
    def __init__(self, client):
        self.client = client

    @discord.app_commands.command(name="setdailychannel", description="Set where the daily problem will be sent")
    async def setdailychannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if channel is None:
            channel = interaction.channel
        # only allow this command to be used by users with the administrator permission
        if interaction.user.guild_permissions.administrator:
            # open the dailychannels.txt file in append mode
            # check if the channel is already in the file
            with open("dailychannels.txt", "r", encoding="UTF-8") as file:
                channels = file.readlines()
                logger.debug(channels)
                logger.debug(channel.id)
                if str(channel.id) + "\n" in channels or channel.id in channels:
                    embed = discord.Embed(
                        title="Error!",
                        description="This channel is already set as the daily channel!",
                        color=discord.Color.red())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                else:
                    with open("dailychannels.txt", "a", encoding="UTF-8") as file:
                        file.write(f"{channel.id}\n")
                    embed = discord.Embed(
                        title="Success!",
                        description="This channel has been set as the daily channel!",
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
        if channel is None:
            channel = interaction.channel
        # only allow this command to be used by users with the administrator permission
        if interaction.user.guild_permissions.administrator:
            # open the dailychannels.txt file in append mode
            # check if the channel is already in the file
            with open("dailychannels.txt", "r", encoding="UTF-8") as file:
                channels = file.readlines()
                logger.debug(channels)
                logger.debug(channel.id)
                if str(channel.id) + "\n" in channels or channel.id in channels:
                    with open("dailychannels.txt", "w", encoding="UTF-8") as file:
                        for line in channels:
                            if line.strip("\n") != str(channel.id):
                                file.write(line)
                    embed = discord.Embed(
                        title="Success!",
                        description="This channel has been removed as the daily channel!",
                        color=discord.Color.green())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="This channel is not set as the daily channel!",
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
