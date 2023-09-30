import discord
from discord.ext import commands

from bot_globals import logger
from embeds.misc_embeds import error_embed
from utils.leaderboards import display_leaderboard
from utils.middleware import ensure_server_document, track_analytics


class Leaderboards(commands.GroupCog, name="leaderboard"):
    def __init__(self, client: commands.Bot):
        self.client = client
        super().__init__()

    @discord.app_commands.command(name="alltime", description="View the All-Time leaderboard")
    @ensure_server_document
    @track_analytics
    async def alltime(self, interaction: discord.Interaction, page: int = 1) -> None:
        logger.info("file: cogs/leaderboards.py ~ alltime ~ run")

        await interaction.response.defer()

        if not interaction.guild:
            embed = error_embed()
            await interaction.followup.send(embed=embed)
            return

        await display_leaderboard(interaction.followup.send, interaction.guild.id, interaction.user.id, "alltime", page)

    @discord.app_commands.command(name="weekly", description="View the Weekly leaderboard")
    @ensure_server_document
    @track_analytics
    async def weekly(self, interaction: discord.Interaction, page: int = 1) -> None:
        logger.info("file: cogs/leaderboards.py ~ weekly ~ run")

        await interaction.response.defer()

        if not interaction.guild:
            embed = error_embed()
            await interaction.followup.send(embed=embed)
            return

        await display_leaderboard(interaction.followup.send, interaction.guild.id, interaction.user.id, "weekly", page)

    @discord.app_commands.command(name="daily", description="View the Daily leaderboard")
    @ensure_server_document
    @track_analytics
    async def daily(self, interaction: discord.Interaction, page: int = 1) -> None:
        logger.info("file: cogs/leaderboards.py ~ daily ~ run")

        await interaction.response.defer()

        if not interaction.guild:
            embed = error_embed()
            await interaction.followup.send(embed=embed)
            return

        await display_leaderboard(interaction.followup.send, interaction.guild.id, interaction.user.id, "daily", page)

    @discord.app_commands.command(name="global-alltime", description="View the Global All-Time leaderboard")
    @track_analytics
    async def global_alltime(self, interaction: discord.Interaction, page: int = 1) -> None:
        logger.info("file: cogs/leaderboards.py ~ global_alltime ~ run")

        await interaction.response.defer()

        if not interaction.guild:
            embed = error_embed()
            await interaction.followup.send(embed=embed)
            return

        # Default server_id is 0 which is the global leaderboard.
        await display_leaderboard(interaction.followup.send, user_id=interaction.user.id, timeframe="alltime", page=page, global_leaderboard=True)

    @discord.app_commands.command(name="global-weekly", description="View the Global Weekly leaderboard")
    @track_analytics
    async def global_weekly(self, interaction: discord.Interaction, page: int = 1) -> None:
        logger.info("file: cogs/leaderboards.py ~ global_weekly ~ run")

        await interaction.response.defer()

        if not interaction.guild:
            embed = error_embed()
            await interaction.followup.send(embed=embed)
            return

        # Default server_id is 0 which is the global leaderboard.
        await display_leaderboard(interaction.followup.send, user_id=interaction.user.id, timeframe="weekly", page=page, global_leaderboard=True)

    @discord.app_commands.command(name="global-daily", description="View the Global Daily leaderboard")
    @track_analytics
    async def global_daily(self, interaction: discord.Interaction, page: int = 1) -> None:
        logger.info("file: cogs/leaderboards.py ~ global_daily ~ run")

        await interaction.response.defer()

        if not interaction.guild:
            embed = error_embed()
            await interaction.followup.send(embed=embed)
            return

        # Default server_id is 0 which is the global leaderboard.
        await display_leaderboard(interaction.followup.send, user_id=interaction.user.id, timeframe="daily", page=page, global_leaderboard=True)


async def setup(client: commands.Bot):
    await client.add_cog(Leaderboards(client))
