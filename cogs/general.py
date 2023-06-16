import discord
from discord.ext import commands

from bot_globals import logger, DIFFICULTY_SCORE


class General(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="help", description="Displays the help menu")
    async def help(self, interaction: discord.Interaction) -> None:
        logger.info("file: cogs/help.py ~ help ~ run")

        embed = discord.Embed(title="LeetCode Bot Help",
                              color=discord.Color.blue())
        embed.add_field(
            name="Adding Your Account to the Leaderboard",
            value="Use `/add {username}` to add your account to the leaderboard. Say 'yes' to link your LeetCode account to the leaderboard and 'no' to not link your LeetCode account to the leaderboard.",
            inline=False)
        embed.add_field(
            name="Deleting Your Account from the Leaderboard",
            value="Use `/delete` to remove your account from the leaderboard.",
            inline=False)
        embed.add_field(
            name="Getting Your Stats",
            value="Use `/stats` to get your LeetCode statistics, *or* use `/stats {username}` to get the LeetCode statistics of another user.",
            inline=False)
        embed.add_field(
            name="Server Leaderboard",
            value="Use `/leaderboard {timeframe} {page}` to see the leaderboard of this server. \n Timeframes: alltime, weekly, daily. \n Page: the page of the leaderboard you want to see. \n Example: `/leaderboard weekly 1` will show the weekly leaderboard of this server on page 1.",
            inline=False)
        embed.add_field(
            name="Random Questions",
            value="Use `/question {difficulty}` to get a random question of that level, or random if you want a random question of any level.",
            inline=False)
        embed.add_field(
            name="Score Calculation",
            value=f"The score is calculated based on the amount of questions you have solved. Easy questions are worth {DIFFICULTY_SCORE['easy']} point, medium questions are worth {DIFFICULTY_SCORE['medium']} points, and hard questions are worth {DIFFICULTY_SCORE['hard']} points.",
            inline=False)
        embed.add_field(
            name="Daily LeetCode Question",
            value="Use `/daily` to get the daily LeetCode question.",
            inline=False)

        # for adminstrators
        if isinstance(interaction.user, discord.Member):
            if interaction.user.guild_permissions.administrator:
                embed.add_field(
                    name="Set Daily LeetCode Channel",
                    value="Use `/setdailychannel` to set the channel where the daily LeetCode question will be sent.",
                    inline=False)
                embed.add_field(
                    name="Remove Daily LeetCode Channel",
                    value="Use `/removedailychannel` to remove the channel where the daily LeetCode question will be sent.",
                    inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(General(client))
