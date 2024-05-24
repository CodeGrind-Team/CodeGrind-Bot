from enum import Enum
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from constants import Period
from middleware import defer_interaction, ensure_server_document
from ui.constants import BooleanField
from utils.leaderboards import generate_leaderboard_embed

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


class LeaderboardsCog(commands.Cog):
    class TimeFrameField(Enum):
        Daily = Period.DAY
        Weekly = Period.WEEK
        Monthly = Period.MONTH
        AllTime = Period.ALLTIME

    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot

    @app_commands.command(name="leaderboard")
    @app_commands.rename(global_leaderboard="global")
    @defer_interaction(user_preferences_prompt=True)
    @ensure_server_document
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        timeframe: TimeFrameField,
        global_leaderboard: BooleanField = BooleanField.No,
    ) -> None:
        """
        View the leaderboard

        :param timeframe: Timeframe for the leaderboard
        :param global_leaderboard: Whether to display the global leaderboard
        """

        embed, view = await generate_leaderboard_embed(
            timeframe.value,
            interaction.guild.id,
            interaction.user.id,
            global_leaderboard=global_leaderboard.to_bool,
            page=1,
        )

        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(LeaderboardsCog(bot))
