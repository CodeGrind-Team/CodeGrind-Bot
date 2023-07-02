import discord
from discord.ext import commands

from bot_globals import DIFFICULTY_SCORE, logger


class General(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="help", description="Displays the help menu")
    async def help(self, interaction: discord.Interaction) -> None:
        logger.info("file: cogs/help.py ~ help ~ run")

        embed = discord.Embed(title="LeetCode Bot Help",
                              color=discord.Color.blue())
        embed.add_field(
            name="Add your account to the Leaderboard",
            value="Use `/add <leetcode_username> <include_hyperlink>` - provide your LeetCode username and write 'yes' or 'no' if you want a hyperlink to your LeetCode account to be included on the leaderboard.",
            inline=False)
        embed.add_field(
            name="Delete your account from the Leaderboard",
            value="Use `/delete`",
            inline=False)
        embed.add_field(
            name="Display your stats",
            value="Use `/stats` to display your LeetCode statistics. \nUse `/stats <leetcode_username>` to display the LeetCode statistics of another user.",
            inline=False)
        embed.add_field(
            name="Display the Leaderboard",
            value="Use `/leaderboard [timeframe]` - available timeframes: `alltime`, `weekly`, or `daily`. \nNote: the user's daily and weekly scores will only start being calculated after an account is created.",
            inline=False)
        embed.add_field(
            name="Get the daily LeetCode question",
            value="Use `/daily`",
            inline=False)
        embed.add_field(
            name="Get a random LeetCode question",
            value="Use `/question <difficulty>` - specify the difficulty level of the question such as `easy`, `medium`, or `hard`. Use `random` for a question of any level.",
            inline=False)
        embed.add_field(
            name="Score calculation",
            value=f"The score is calculated based on the amount of questions you have solved. Easy questions are worth {DIFFICULTY_SCORE['easy']} point, medium questions are worth {DIFFICULTY_SCORE['medium']} points, and hard questions are worth {DIFFICULTY_SCORE['hard']} points.",
            inline=False)
        embed.add_field(
            name="Vote for the bot on top.gg",
            value="Love the bot? Vote for it on top.gg: https://top.gg/bot/1059122559066570885/vote",
            inline=False)
        embed.add_field(
            name="Get the Zerotrac Rating of a question",
            value="Use `/rating <question_id>` to get the Zerotrac Rating of a question.",
            inline=False)

        # for adminstrators
        if isinstance(interaction.user, discord.Member):
            if interaction.user.guild_permissions.administrator:
                embed.add_field(
                    name="Admins only: Set daily LeetCode channel",
                    value="Use `/setdailychannel <channel>` to set the channel where the daily question and the daily and weekly leaderboard will be sent to. If no channel is specified, the channel where the command was written in will be used.",
                    inline=False)
                embed.add_field(
                    name="Admins only: Remove daily LeetCode channel",
                    value="Use `/removedailychannel <channel>` to stop daily questions and the daily and weekly leaderboards being sent to the channel. If no channel is specified, the channel where the command was written in will be used.",
                    inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # command for voting
    @discord.app_commands.command(name="vote", description="Vote for the bot on top.gg")
    async def vote(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(title="Vote for the bot on top.gg: ",
                              description="https://top.gg/bot/1059122559066570885/vote",
                              color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(General(client))
