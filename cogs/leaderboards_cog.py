import discord
from discord.ext import commands

from constants import Period
from middleware import defer_interaction, ensure_server_document, track_analytics
from utils.leaderboards_utils import generate_leaderboard_embed


class LeaderboardsGroupCog(commands.GroupCog, name="leaderboard"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

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
            interaction, Period.ALLTIME, page=page, global_leaderboard=True
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

        await self._generate_leaderboard_response(
            interaction, Period.MONTH, page, global_leaderboard=True
        )

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

        await self._generate_leaderboard_response(
            interaction, Period.WEEK, page, global_leaderboard=True
        )

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

        await self._generate_leaderboard_response(
            interaction, Period.DAY, page, global_leaderboard=True
        )

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

        embed, view = await generate_leaderboard_embed(
            period,
            interaction.guild.id,
            interaction.user.id,
            global_leaderboard=global_leaderboard,
            page=page,
        )

        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LeaderboardsGroupCog(bot))
