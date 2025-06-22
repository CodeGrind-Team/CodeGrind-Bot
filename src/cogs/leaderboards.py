from enum import Enum
from typing import TYPE_CHECKING, cast

import discord
from discord import app_commands
from discord.ext import commands

from src.constants import LeaderboardSortBy, Period
from src.middleware import defer_interaction, ensure_server_document
from src.ui.constants import BooleanField
from src.utils.leaderboards import generate_leaderboard_embed

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot


class LeaderboardsCog(commands.Cog):
    class TimeFrameField(Enum):
        Daily = Period.DAY
        Weekly = Period.WEEK
        Monthly = Period.MONTH
        AllTime = Period.ALLTIME

    class SortByField(Enum):
        WinCount = LeaderboardSortBy.WIN_COUNT
        Score = LeaderboardSortBy.SCORE

    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot

    @app_commands.guild_only()
    @app_commands.command(name="leaderboard")
    @app_commands.rename(global_leaderboard="global")
    @app_commands.rename(sort_by="sorting")
    @defer_interaction(user_preferences_prompt=True)
    @ensure_server_document
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        timeframe: TimeFrameField,
        global_leaderboard: BooleanField = BooleanField.No,
        sort_by: SortByField = SortByField.Score,
    ) -> None:
        """
        View the leaderboard

        :param timeframe: Timeframe for the leaderboard
        :param global_leaderboard: Whether to display the global leaderboard
        :param sort_by: The sorting method
        """
        guild_id = cast(int, interaction.guild_id)

        embed, view = await generate_leaderboard_embed(
            timeframe.value,
            guild_id,
            sort_by.value,
            author_user_id=interaction.user.id,
            global_leaderboard=global_leaderboard.to_bool,
            page=1,
        )

        await interaction.followup.send(embed=embed, view=view)  # type: ignore


async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(LeaderboardsCog(bot))
