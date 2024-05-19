from enum import Enum

import discord
from discord.ext import commands

from constants import Period
from middleware import defer_interaction, ensure_server_document
from utils.leaderboards_utils import generate_leaderboard_embed


class TimeFrame(Enum):
    Daily = Period.DAY
    Weekly = Period.WEEK
    Monthly = Period.MONTH
    AllTime = Period.ALLTIME


class LeaderboardsGroupCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command(
        name="leaderboard", description="View the leaderboard"
    )
    @discord.app_commands.rename(global_leaderboard="global")
    @defer_interaction(user_preferences_prompt=True)
    @ensure_server_document
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        timeframe: TimeFrame,
        global_leaderboard: bool = False,
    ) -> None:
        """
        Command to view the AllTime leaderboard.

        :param interaction: The Discord interaction.
        :param interaction: The period.
        :param period: Select the time period for the leaderboard.
        :param global_leaderboard: Whether to display the global leaderboard.
        """

        embed, view = await generate_leaderboard_embed(
            timeframe.value,
            interaction.guild.id,
            interaction.user.id,
            global_leaderboard,
            page=1,
        )

        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LeaderboardsGroupCog(bot))
