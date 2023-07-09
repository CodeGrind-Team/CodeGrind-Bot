import discord
from discord.ext import commands

from bot_globals import calculate_scores, logger
from embeds.stats_embeds import invalid_username_embed, stats_embed
from embeds.users_embeds import account_not_found_embed
from models.projections import LeetCodeUsernameProjection
from models.user_model import User
from utils.questions import get_problems_solved_and_rank


class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client

    @discord.app_commands.command(name="stats", description="Prints the stats of a user")
    async def stats(self, interaction: discord.Interaction, leetcode_username: str | None = None) -> None:
        logger.info(
            'file: cogs/stats.py ~ stats ~ run ~ leetcode_username: %s', leetcode_username)

        if not interaction.guild:
            return

        user_id = interaction.user.id

        if leetcode_username is None:
            user = await User.find_one(User.id == user_id).project(LeetCodeUsernameProjection)

            if not user:
                embed = account_not_found_embed()
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            leetcode_username = user.leetcode_username

        stats = get_problems_solved_and_rank(leetcode_username)

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

        embed = stats_embed(leetcode_username, rank, easy,
                            medium, hard, total_questions_done, total_score)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(Stats(client))
