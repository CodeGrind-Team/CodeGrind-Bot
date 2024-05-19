import discord
from discord.ext import commands

from constants import Period
from middleware import defer_interaction, ensure_server_document, track_analytics
from utils.leaderboards_utils import generate_leaderboard_embed


class LeaderboardsGroupCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command(
        name="leaderboard", description="View the leaderboard"
    )
    @defer_interaction(user_preferences_prompt=True)
    @ensure_server_document
    @track_analytics
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        period: Period,
        global_leaderboard: bool = False,
    ) -> None:
        """
        Command to view the AllTime leaderboard.

        :param interaction: The Discord interaction.
        :param global_leaderboard: Whether to display the server or global leaderboard.
        :param page: The page number of the leaderboard.
        """

        embed, view = await generate_leaderboard_embed(
            period,
            interaction.guild.id,
            interaction.user.id,
            global_leaderboard=global_leaderboard,
            page=1,
        )

        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LeaderboardsGroupCog(bot))
