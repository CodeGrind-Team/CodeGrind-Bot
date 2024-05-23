from enum import Enum

from constants import DifficultyScore


class PreferenceField(Enum):
    GLOBAL_ANONYMOUS = 1
    GLOBAL_URL = 2
    LOCAL_URL = 3


class CommandCategory(Enum):
    HOME = "Home"
    ACCOUNT = "Account"
    LEADERBOARD = "Leaderboard"
    STATISTICS = "Statistics"
    LEETCODE_PROBLEMS = "LeetCode Questions"
    ROLES = "Roles"
    ADMIN = "Admin"
    CODEGRIND_TEAM = "CodeGrind Team"


CATEGORY_DESCRIPTIONS = {
    CommandCategory.HOME: f"""
# About CodeGrind Bot
CodeGrind Bot helps you master LeetCode by engaging in friendly competition with your friends through daily, weekly, monthly, and all-time server leaderboards. Simply connect your LeetCode account to this bot and you are ready to go!

This bot also provides you commands to get a random LeetCode question, the LeetCode daily question, retrieve the Zerotrac rating of a question, and receive a notification of the LeetCode daily question and the daily/weekly winners leaderboards.

## Score calculation
Each connected user is assigned a score which calculated based on the amount of questions they have solved. 
Here is how much each question difficulty is worth:
>    - Easy questions are worth {DifficultyScore.EASY.value} point
>    - Medium questions are worth {DifficultyScore.MEDIUM.value} points
>    - Hard questions are worth {DifficultyScore.HARD.value} points

## Commands
Select a category from the dropdown below to see all the commands in that category.

## Privacy Policy
You can view our Privacy Policy [here](https://github.com/CodeGrind-Team/CodeGrind-Bot/blob/main/PRIVACY_POLICY.md).
""",
    CommandCategory.ACCOUNT: """
## Account

</add:TODO>: Add/connect your LeetCode account to this server's CodeGrind leaderboards.

</update:TODO>: Update your local and global CodeGrind profile preferences.

</remove:TODO>: Remove your profile from this server's CodeGrind leaderboards.
>    - `permanently` _(optional)_: Permanently delete all information CodeGrind stores on you.""",
    CommandCategory.LEADERBOARD: """
## Leaderboard

### Server leaderboard
</leaderboard:TODO> Display the CodeGrind leaderboard.
>    - `timeframe`: The desired timeframe (daily, weekly, monthly, or all-time).
>    - `global` _(optional)_: Whether display the Global CodeGrind leaderboards or the default local (server-only) leaderboards.

Note: scores for `daily`, `weekly`, and `monthly` leaderboards will only start being tracked after an account is created. Any previous questions done that day/week/month will not be calculated into your score.""",
    CommandCategory.STATISTICS: """
## Statistics

</stats:TODO>: Returns the statistics of your or someone else's LeetCode account.
>    - `extension`: The extra information to add to the stats card (activity, heatmap, contest, or none). 
>    - `user` _(optional)_: The user to display the stats of. By default, it will be your account.

Credit to [LeetCode Stats Card](https://github.com/JacobLinCool/LeetCode-Stats-Card) for generating the visuals.""",
    CommandCategory.LEETCODE_PROBLEMS: """
## LeetCode Problems

</problem daily:TODO>: Returns LeetCode's problem of the day

</problem random:TODO>: Returns a random LeetCode question.
>    - `difficulty` _(optional)_: A difficulty level (easy, medium or hard). By default this will be set to a random difficulty level.

</problem search:TODO>: Display your searched LeetCode question.""",
    CommandCategory.ROLES: """
## Roles

If an admin has enabled this feature using </roles:TODO>, you will receive the following roles. If you're an admin, check out the admin commands section to learn how to enable this feature.

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

`New question streak`: Given to you depending on your new question streak. Your streak is incremented if you've completed a **new leetcode question each day**, not to be confused with completing the problem of the day. Here are the different streaks you could get:
>    - Streak Initiate (3 Days)
>    - Streak Pursuer (7 Days)
>    - Streak Adventurer (14 Days)
>    - Streak Dominator (30 Days)
>    - Streak Legend (90 Days)""",
    CommandCategory.ADMIN: """
# Admin commands
These commands are only available to administrators of this server.

## Roles

</roles:TODO>: Creates and gives verified CodeGrind user, score milestones, and streak roles that will be automatically updated each day at midday (UTC).

## Notifications

</notifications:TODO>: Sends daily notifications at midnight (UTC) to the specified channel.
>    - `channel` _(optional)_: The channel (e.g. "#home-channel") to send notifications to. By default this will be the channel where you ran this command.

Note: please press the 'save' button twice!

## Settings

</settings timezone:TODO>: Change the timezone of this server's leaderboards.
>    - `timezone`: A timezone from the following list of timezones: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568 .""",
    CommandCategory.CODEGRIND_TEAM: """
## CodeGrind Team

### Developers
Nano (<@814656377188384810>)
Kevin (<@335154148976885770>)

### Contributors
[Shaan](<https://github.com/ShaanCoding>) (<@199662959964848128>): Created the </roles:TODO> command.
[Aalaap](<https://www.linkedin.com/in/aalaap-d-969703239/>) (<@635232267458969631>): Created the </problem:TODO> commands. 

Thank you to all the contributors for helping improve CodeGrind Bot!

Link to the repository: https://github.com/CodeGrind-Team/CodeGrind-Bot""",
}
