import discord

from bot_globals import DIFFICULTY_SCORE


def help_embed(is_admin: bool = False) -> discord.Embed:
    embed = discord.Embed(title="LeetCode Bot Help",
                          color=discord.Color.blurple())

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

    if is_admin:
        embed.add_field(
            name="Admins only: Set daily LeetCode channel",
            value="Use `/setdailychannel <channel>` to set the channel where the daily question and the daily and weekly leaderboard will be sent to. If no channel is specified, the channel where the command was written in will be used.",
            inline=False)

        embed.add_field(
            name="Admins only: Remove daily LeetCode channel",
            value="Use `/removedailychannel <channel>` to stop daily questions and the daily and weekly leaderboards being sent to the channel. If no channel is specified, the channel where the command was written in will be used.",
            inline=False)

    return embed


def not_admin_embed() -> discord.Embed:
    embed = discord.Embed(title="Only admins can use this command",
                          color=discord.Color.red())

    return embed


def not_creator_embed() -> discord.Embed:
    embed = discord.Embed(title="Action denied",
                          color=discord.Color.red())

    embed.description = "Only the person who used the command can use the buttons on this leaderboard"

    return embed
