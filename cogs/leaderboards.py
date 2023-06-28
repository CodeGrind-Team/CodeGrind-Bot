import discord
from discord.ext import commands

from bot_globals import logger
from utils.leaderboards import display_leaderboard
from utils.middleware import ensure_server_document


class Leaderboards(commands.GroupCog, name="leaderboard"):
    def __init__(self, client: commands.Bot):
        self.client = client
        super().__init__()

    @discord.app_commands.command(name="alltime", description="View the All-Time leaderboard")
    @ensure_server_document
    async def alltime(self, interaction: discord.Interaction, page: int = 1) -> None:
        logger.info("file: cogs/leaderboards.py ~ alltime ~ run")

        if not interaction.guild:
            await interaction.response.send_message(contents="An error has occured! Please try again.", ephemeral=True)
            return

        await display_leaderboard(interaction.response.send_message, interaction.guild.id, interaction.user.id, "alltime", page)

    @discord.app_commands.command(name="weekly", description="View the Weekly leaderboard")
    @ensure_server_document
    async def weekly(self, interaction: discord.Interaction, page: int = 1) -> None:
        logger.info("file: cogs/leaderboards.py ~ weekly ~ run")

        if not interaction.guild:
            await interaction.response.send_message(contents="An error has occured! Please try again.", ephemeral=True)
            return

        await display_leaderboard(interaction.response.send_message, interaction.guild.id, interaction.user.id, "weekly", page)

    @discord.app_commands.command(name="daily", description="View the Daily leaderboard")
    @ensure_server_document
    async def daily(self, interaction: discord.Interaction, page: int = 1) -> None:
        logger.info("file: cogs/leaderboards.py ~ daily ~ run")

        if not interaction.guild:
            await interaction.response.send_message(contents="An error has occured! Please try again.", ephemeral=True)
            return

        await display_leaderboard(interaction.response.send_message, interaction.guild.id, interaction.user.id, "daily", page)


async def setup(client: commands.Bot):
    await client.add_cog(Leaderboards(client))
