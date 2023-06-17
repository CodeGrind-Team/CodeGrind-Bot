import discord
from discord.ext import commands

from bot_globals import DIFFICULTY_SCORE, logger
from utils.io_handling import read_file
from utils.questions import get_problems_solved_and_rank


class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client

    @discord.app_commands.command(name="stats", description="Prints the stats of a user")
    async def stats(self, interaction: discord.Interaction, leetcode_username: str | None = None) -> None:
        logger.info(
            'file: cogs/stats.py ~ stats ~ run ~ leetcode_username: %s', leetcode_username)

        discord_user = interaction.user

        if not interaction.guild:
            return

        if leetcode_username is None:
            data = await read_file(f"data/{interaction.guild.id}_leetcode_stats.json")

            if str(discord_user.id) in data["users"]:
                leetcode_username = data["users"][str(
                    discord_user.id)]["leetcode_username"]
            else:
                logger.info(
                    'file: cogs/stats.py ~ stats ~ user not found: %s', leetcode_username)

                embed = discord.Embed(
                    title="Error!",
                    description="You have not added your LeetCode username yet!",
                    color=discord.Color.red())
                embed.add_field(name="Add your LeetCode username",
                                value="Use the `/add <username>` command to add your LeetCode username.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        if leetcode_username is None:
            await interaction.response.defer()
            return

        stats = get_problems_solved_and_rank(leetcode_username)

        if stats is not None:
            rank = stats["profile"]["ranking"]
            easy_completed = stats["submitStatsGlobal"]["acSubmissionNum"]["Easy"]
            medium_completed = stats["submitStatsGlobal"]["acSubmissionNum"]["Medium"]
            hard_completed = stats["submitStatsGlobal"]["acSubmissionNum"]["Hard"]
            total_questions_done = stats["submitStatsGlobal"]["acSubmissionNum"]["All"]

            total_questions_done = easy_completed + medium_completed + hard_completed
            total_score = easy_completed * DIFFICULTY_SCORE['easy'] + medium_completed * \
                DIFFICULTY_SCORE['medium'] + \
                hard_completed * DIFFICULTY_SCORE['hard']

            embed = discord.Embed(
                title=f"Rank: {rank}", color=discord.Color.green())
            embed.add_field(name="**Easy**",
                            value=f"{easy_completed}", inline=True)
            embed.add_field(name="**Medium**",
                            value=f"{medium_completed}", inline=True)
            embed.add_field(name="**Hard**",
                            value=f"{hard_completed}", inline=True)

            embed.set_footer(
                text=f"Total: {total_questions_done} | Score: {total_score}")

            embed.set_author(
                name=f"{leetcode_username}'s LeetCode Stats",
                icon_url="https://repository-images.githubusercontent.com/98157751/7e85df00-ec67-11e9-98d3-684a4b66ae37"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="Error!",
                description="The username you entered is invalid or LeetCode timed out. Try Again!",
                color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(Stats(client))
