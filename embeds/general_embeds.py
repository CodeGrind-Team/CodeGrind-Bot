import discord

from bot_globals import DIFFICULTY_SCORE

COMMAND_CATEGORIES = {"Home": f"""
# About CodeGrind Bot
CodeGrind Bot helps you master LeetCode by competing with your friends on daily, weekly and all-time server leaderboards. Simply connect your LeetCode account to this bot and you are ready to go!

This bot also provides you commands to get a random LeetCode question, the LeetCode daily question, retrieve the Zerotrac rating of a question, and receive a notification of the LeetCode daily question and the daily/weekly winners leaderboards.

## Score calculation
Each connected user is assigned a score which calculated based on the amount of questions you have solved. 
Here is how much each question difficulty is worth:
>    - Easy questions are worth {DIFFICULTY_SCORE['easy']} point
>    - Medium questions are worth {DIFFICULTY_SCORE['medium']} points
>    - Hard questions are worth {DIFFICULTY_SCORE['hard']} points

## Commands
Please select a category from the dropdown to be shown all the commands related to the selected category.""",
                      "Account": """
## Account

</add:1115756888185917542>: Adds your LeetCode account onto this server's leaderboards. 
>    - `leetcode_username`: Your permanent LeetCode username.
>    - `include_url` _(optional)_: Decide whether you want leaderboards in this server to include a hyperlink to your LeetCode profile or not. Default is 'True'.

</update:1127716432168362004>: Updates your account preferences for this server.
>    - `include_url` _(optional)_: Decide whether you want leaderboards in this server to include a hyperlink to your LeetCode profile or not. Default is 'True'.

</remove:1127663038514876540>: Removes your LeetCode account from this server.""",

                      "Leaderboard": """
## Leaderboard

</leaderboard daily:1115756888664060015>: Returns today's leaderboard stats which resets at midnight (UTC)

</leaderboard weekly:1115756888664060015>: Returns the week's leaderboard stats which resets on Sunday at midnight (UTC)

</leaderboard alltime:1115756888664060015>: Returns the all-time leaderboard stats

Note: stats for `daily` and `weekly` will only be calculated after an account is created. Any previous questions done that day or that week will not be calculated.""",

                      "Statistics": """
## Statistics

</stats:1115756888664060014>: Returns the statistics of your or someone else's LeetCode account.
>    - `user` _(optional)_: A user from the server. Default is your account.
>    - `display_publicly` _(optional)_: Whether you want everyone in the server to see the stats. Default is 'True'""",

                      "LeetCode Questions": """
## LeetCode Questions

</daily-question:1115756888185917544>: Returns the LeetCode daily question.

</random-question:1115756888185917545>: Returns a random question (difficulty can be specified).
>    - `difficulty` _(optional)_: A difficulty level ('easy', 'medium' or 'hard'). Default is a 'random' difficulty level.

</search-question:aalaap>: Returns the question according to the id/name given
>    - `name_or_id` : The LeetCode question ID or the question's name.
""",

                      "Admin": """
# Admin commands
These commands are only available to administrators of this server.
## Settings

</settings timezone:1127663038514876538>: Change the timezone of the server.
>    - `timezone`: A timezone (case sensitive) from the following list of timeones: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568 .

## Notifications

</notifychannel enable:1127663038514876541>: Set what notifications the channel receives.

</notifychannel disable:1127663038514876541>: Stop channel from receiving selected notifications.

>    - `channel` _(optional)_: The channel (e.g. "#home-channel"). Default is the channel where the command was ran.

Note: please press the 'save' button twice"""}


def help_embed(description: str) -> discord.Embed:
    embed = discord.Embed(title="CodeGrind Bot Info & Commands",
                          url="https://github.com/CodeGrind-Team/CodeGrind-Bot/wiki/Commands", color=discord.Color.blurple())

    embed.description = description

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
