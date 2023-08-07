import discord
from discord.ext import commands

from bot_globals import calculate_scores, logger
from embeds.stats_embeds import invalid_username_embed, stats_embed, account_hidden_embed
from embeds.users_embeds import account_not_found_embed
from models.user_model import User
from utils.middleware import track_analytics
from utils.questions import get_problems_solved_and_rank


class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client

    @discord.app_commands.command(name="stats", description="Displays the stats of a user")
    @track_analytics
    async def stats(self, interaction: discord.Interaction, user: discord.Member | None = None, display_publicly: bool = False) -> None:
        logger.info('file: cogs/stats.py ~ stats ~ run')

        if not interaction.guild:
            return

        if user:
            user_id = user.id
        else:
            user_id = interaction.user.id

        user = await User.find_one(User.id == user_id)

        if not user:
            embed = account_not_found_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        display_information = next(
            (di for di in user.display_information if di.server_id == interaction.guild.id), None)

        if user.id != interaction.user.id and not display_information.url:
            embed = account_hidden_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        stats = get_problems_solved_and_rank(user.leetcode_username)

        if not stats:
            embed = invalid_username_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        rank = stats["profile"]["ranking"]
        easy = stats["submitStatsGlobal"]["acSubmissionNum"]["Easy"]
        medium = stats["submitStatsGlobal"]["acSubmissionNum"]["Medium"]
        hard = stats["submitStatsGlobal"]["acSubmissionNum"]["Hard"]
        total_questions_done = stats["submitStatsGlobal"]["acSubmissionNum"]["All"]

        total_score = calculate_scores(easy, medium, hard)

        embed = stats_embed(user.leetcode_username, rank, easy,
                            medium, hard, total_questions_done, total_score)
        await interaction.response.send_message(embed=embed, ephemeral=not display_publicly)


async def setup(client: commands.Bot):
    await client.add_cog(Stats(client))
