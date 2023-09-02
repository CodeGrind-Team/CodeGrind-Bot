import discord
from bot_globals import logger
from discord.ext import commands
from embeds.general_embeds import COMMAND_CATEGORIES, help_embed
from utils.middleware import track_analytics
from utils.views import CommandTypeSelectView


class General(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="help", description="Help for CodeGrind Bot")
    @track_analytics
    async def help(self, interaction: discord.Interaction) -> None:
        logger.info("file: cogs/help.py ~ help ~ run")

        embed = help_embed(COMMAND_CATEGORIES["Home"])
        embed.set_footer(
            text="Love our bot? Vote on top.gg using /vote")

        await interaction.response.send_message(embed=embed, view=CommandTypeSelectView(COMMAND_CATEGORIES), ephemeral=True)

    @discord.app_commands.command(name="vote", description="Vote for the bot on top.gg")
    @track_analytics
    async def vote(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(title="Vote for the bot on top.gg: ",
                              description="https://top.gg/bot/1059122559066570885/vote",
                              color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(General(client))
