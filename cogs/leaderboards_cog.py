import discord
from discord.ext import commands

from constants import Period
from middleware import (
    defer_interaction,
    ensure_server_document,
    track_analytics,
)
from utils.leaderboards_utils import LeaderboardManager
from database.models.server_model import Server


class LeaderboardsGroupCog(commands.GroupCog, name="leaderboard"):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.leaderboards_manager = LeaderboardManager()
        super().__init__()
        # TODO: Check if necessary

    @discord.app_commands.command(
        name="alltime", description="View the AllTime leaderboard"
    )
    @defer_interaction(user_preferences_prompt=True)
    @ensure_server_document
    @track_analytics
    async def alltime(self, interaction: discord.Interaction, page: int = 1) -> None:
        """
        Command to view the AllTime leaderboard.

        :param interaction: The Discord interaction.
        :param page: The page number of the leaderboard.
        """

        await self._generate_leaderboard_response(interaction, Period.ALLTIME, page)

    @discord.app_commands.command(
        name="monthly", description="View the Monthly leaderboard"
    )
    @defer_interaction(user_preferences_prompt=True)
    @ensure_server_document
    @track_analytics
    async def monthly(self, interaction: discord.Interaction, page: int = 1) -> None:
        """
        Command to view the Monthly leaderboard.

        :param interaction: The Discord interaction.
        :param page: The page number of the leaderboard.
        """

        await self._generate_leaderboard_response(interaction, Period.MONTH, page)

    @discord.app_commands.command(
        name="weekly", description="View the Weekly leaderboard"
    )
    @defer_interaction(user_preferences_prompt=True)
    @ensure_server_document
    @track_analytics
    async def weekly(self, interaction: discord.Interaction, page: int = 1) -> None:
        """
        Command to view the Weekly leaderboard.

        :param interaction: The Discord interaction.
        :param page: The page number of the leaderboard.
        """

        await self._generate_leaderboard_response(interaction, Period.WEEK, page)

    @discord.app_commands.command(
        name="daily", description="View the Daily leaderboard"
    )
    @defer_interaction(user_preferences_prompt=True)
    @ensure_server_document
    @track_analytics
    async def daily(self, interaction: discord.Interaction, page: int = 1) -> None:
        """
        Command to view the Daily leaderboard.

        :param interaction: The Discord interaction.
        :param page: The page number of the leaderboard.
        """

        await self._generate_leaderboard_response(interaction, Period.DAY, page)

    @discord.app_commands.command(
        name="global-alltime", description="View the Global All-Time leaderboard"
    )
    @defer_interaction(user_preferences_prompt=True)
    @track_analytics
    async def global_alltime(
        self, interaction: discord.Interaction, page: int = 1
    ) -> None:
        """
        Command to view the Global AllTime leaderboard.

        :param interaction: The Discord interaction.
        :param page: The page number of the leaderboard.
        """

        await self._generate_leaderboard_response(
            interaction, Period.ALLTIME, page, True
        )

    @discord.app_commands.command(
        name="global-monthly", description="View the Global Monthly leaderboard"
    )
    @defer_interaction(user_preferences_prompt=True)
    @track_analytics
    async def global_monthly(
        self, interaction: discord.Interaction, page: int = 1
    ) -> None:
        """
        Command to view the Global Monthly leaderboard.

        :param interaction: The Discord interaction.
        :param page: The page number of the leaderboard.
        """

        await self._generate_leaderboard_response(interaction, Period.MONTH, page, True)

    @discord.app_commands.command(
        name="global-weekly", description="View the Global Weekly leaderboard"
    )
    @defer_interaction(user_preferences_prompt=True)
    @track_analytics
    async def global_weekly(
        self, interaction: discord.Interaction, page: int = 1
    ) -> None:
        """
        Command to view the Global Weekly leaderboard.

        :param interaction: The Discord interaction.
        :param page: The page number of the leaderboard.
        """

        await self._generate_leaderboard_response(interaction, Period.WEEK, page, True)

    @discord.app_commands.command(
        name="global-daily", description="View the Global Daily leaderboard"
    )
    @defer_interaction(user_preferences_prompt=True)
    @track_analytics
    async def global_daily(
        self, interaction: discord.Interaction, page: int = 1
    ) -> None:
        """
        Command to view the Global Daily leaderboard.

        :param interaction: The Discord interaction.
        :param page: The page number of the leaderboard.
        """

        await self._generate_leaderboard_response(interaction, Period.DAY, page, True)

    async def _generate_leaderboard_response(
        self,
        interaction: discord.Interaction,
        period: Period,
        page: int = 1,
        global_leaderboard: bool = False,
    ) -> None:
        """
        Generates a response including the leaderboard embed.

        :param interaction: The Discord interaction.
        :param period: The period to generate the data for.
        :param page: The page number of the leaderboard.
        """
        server = await Server.find_one(Server.id == interaction.guild.id)

        embed, view = await self.leaderboards_manager.generate_leaderboard_embed(
            period,
            server,
            interaction.user.id,
            global_leaderboard,
            page,
        )

        await interaction.followup.send(embed=embed, view=view)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(LeaderboardsGroupCog(client))
