import discord
from discord.ext import commands
from beanie.odm.operators.update.general import Set

from bot_globals import logger
from middleware import (
    defer_interaction,
    ensure_server_document,
    topgg_vote_required,
    track_analytics,
)
from database.models.user_model import User
from utils.competitions_utils import daily_completed


class Competitions(commands.GroupCog, name="competition"):
    def __init__(self, client: commands.Bot):
        self.client = client
        super().__init__()

    @discord.app_commands.command(name="daily-completed", description="Verify that you've completed the daily")
    @defer_interaction(user_preferences_prompt=True)
    @ensure_server_document
    @topgg_vote_required
    @track_analytics
    async def daily_completed(self, interaction: discord.Interaction) -> None:
        logger.info("file: cogs/competitions_cog.py ~ daily-completed ~ run")

        completed: bool = await daily_completed(interaction.user.id)

        await User.find_one(User.id == interaction.user.id).update(Set({User.scores.daily_completed: completed}))

        # TODO
        embed = daily_completed_embed(completed)
        await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Competitions(client))
