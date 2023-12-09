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
Please select a category from the dropdown to be shown all the commands related to the selected category.

## Privacy Policy
You can view our Privacy Policy [here](https://github.com/CodeGrind-Team/CodeGrind-Bot/blob/main/PRIVACY_POLICY.md).
""",
                      "Account": """
## Account

</add:1115756888185917542>: Adds your LeetCode account onto this server's leaderboards. 
>    - `leetcode_id`: Your permanent LeetCode ID you can find at https://leetcode.com/profile/account/.

</update:1127716432168362004>: Displays a prompt where you can update your account preferences.

</remove:1127663038514876540>: Removes your LeetCode account from this server.
>    - `permanently_delete` _(optional)_: Permanently delete all your CodeGrind information from all servers and unlink your LeetCode account from the bot.""",

                      "Leaderboard": """
## Leaderboard

### Server leaderboard
</leaderboard daily:1115756888664060015>: Returns today's leaderboard stats which resets at midnight (UTC)

</leaderboard weekly:1115756888664060015>: Returns the week's leaderboard stats which resets on Sunday at midnight (UTC)

</leaderboard alltime:1115756888664060015>: Returns the all-time leaderboard stats

### Global leaderboard (</vote:1122529789056647198> on top.gg to gain access to these commands)
</leaderboard global-daily:1115756888664060015>: Returns today's leaderboard stats which resets at midnight (UTC)

</leaderboard global-weekly:1115756888664060015>: Returns the week's leaderboard stats which resets on Sunday at midnight (UTC)

</leaderboard global-alltime:1115756888664060015>: Returns the all-time leaderboard stats

Note: stats for `daily` and `weekly` will only be calculated after an account is created. Any previous questions done that day or that week will not be calculated.""",

                      "Statistics": """
## Statistics

</stats:1115756888664060014>: Returns the statistics of your or someone else's LeetCode account.
>    - `user` _(optional)_: A user from the server. Default is your account.
>    - `display_publicly` _(optional)_: Whether you want everyone in the server to see the stats. Default is 'True'
>    - `heatmap` _(optional)_: Whether to display a heatmap of the user's submissions rather than the user's latest activity. Default is `False`.

Credit to [LeetCode Stats Card](https://github.com/JacobLinCool/LeetCode-Stats-Card) for generating the visuals.""",

                      "LeetCode Questions": """
## LeetCode Questions

</question daily:1150096353133875251>: Returns the LeetCode daily question.

</question random:1150096353133875251>: Returns a random question (difficulty can be specified).
>    - `difficulty` _(optional)_: A difficulty level ('easy', 'medium' or 'hard'). Default is a 'random' difficulty level.

</question search:1150096353133875251>: Returns the question according to the name, ID, or URL given
>    - `name_id_or_url` : The LeetCode question name, ID, or URL.""",

                      "Roles": """
## Roles

If an admin has enabled this feature using </roles enable:1147624135850197033>, you will receive the following roles.

`CodeGrind Verified`: Given to you if you've connected your account to the bot in this server using </add:1115756888185917542>.

`Point milestones`: Given to you depending on your total score. Here are the different milestones you could reach:
>    - Novice (1 pt)
>    - Apprentice (100 pts)
>    - Capable (300 pts)
>    - Competent (500 pts)
>    - Advanced (1000 pts)
>    - Expert (2000 pts)
>    - Master (4000 pts)
>    - Legend (6000 pts)

`New question streak`: Given to you depending on your new question streak. Your streak is incremented if you've completed a new leetcode question each day. Here are the different streaks you could get:
>    - Streak Initiate (3 Days)
>    - Streak Pursuer (7 Days)
>    - Streak Adventurer (14 Days)
>    - Streak Dominator (30 Days)
>    - Streak Legend (90 Days)""",

                      "Admin": """
# Admin commands
These commands are only available to administrators of this server.

## Roles

</roles enable:1147624135850197033>: Create and give verified user, point milestones, and streak roles that will be automatically updated at midday (UTC).
>    - `CodeGrind Verified`: Given to user's that have connected their LeetCode account to the bot in this server.
>    - `Point milestones`: Given to user's depending on their total CodeGrind score.
>    - `Streak`: Given to user's depending on their streak. Their streak is incremented each day if the user has completed a new LeetCode question (not necessarily the LeetCode daily question).

</roles disable:1147624135850197033> Delete and remove verified user, point milestones, and streak roles.

## Notifications

</notify-channel enable:1147630083704635392>: Set what notifications the channel receives.

</notify-channel disable:1147630083704635392>: Stop channel from receiving selected notifications.

>    - `channel` _(optional)_: The channel (e.g. "#home-channel"). Default is the channel where the command was ran.

Note: please press the 'save' button twice

## Settings

</settings timezone:1127663038514876538>: Change the timezone of the server.
>    - `timezone`: A timezone (case sensitive) from the following list of timeones: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568 .""",

                      "CodeGrind Team": """
## CodeGrind Team

### Developers
Nano (<@814656377188384810>)
Kevin (<@335154148976885770>)

### Contributors
[Shaan](<https://github.com/ShaanCoding>) (<@199662959964848128>): Created the </roles enable:1147624135850197033> and </roles disable:1147624135850197033> commands.
[Aalaap](<https://www.linkedin.com/in/aalaap-d-969703239/>) (<@635232267458969631>): Created the </question daily:1150096353133875251>, </question random:1150096353133875251>, and </question search:1150096353133875251> commands. 

Thank you to all the contributors for helping improve CodeGrind Bot!"""}


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
