import discord
from discord.ext import commands

from bot_globals import logger
from middleware import (
    defer_interaction,
    ensure_server_document,
    track_analytics,
)
from database.models.user_model import User
from embeds.competitions_embeds import daily_completed_embed
from embeds.misc_embeds import error_embed
from embeds.users_embeds import account_not_found_embed
from utils.competitions_utils import daily_completed


class Competitions(commands.GroupCog, name="competition"):
    def __init__(self, client: commands.Bot):
        self.client = client
        super().__init__()

    @discord.app_commands.command(name="leaderboard", description="Displays the competition leaderboard")
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @track_analytics
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        logger.info("file: cogs/competitions_cog.py ~ leaderboard ~ run")

    @discord.app_commands.command(name="daily-completed", description="Verify that you've completed the daily")
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @track_analytics
    async def daily_completed(self, interaction: discord.Interaction) -> None:
        logger.info("file: cogs/competitions_cog.py ~ daily_completed ~ run")

        user = await User.find_one(User.id == interaction.user.id)

        if not user:
            embed = account_not_found_embed()
            await interaction.followup.send(embed=embed)
            return

        completed = await daily_completed(user.leetcode_username)

        if completed is None:
            embed = error_embed()
            await interaction.followup.send(embed=embed)
            return

        embed = daily_completed_embed(completed)

        # TODO send questions completed by user notification to that server.
        await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Competitions(client))
