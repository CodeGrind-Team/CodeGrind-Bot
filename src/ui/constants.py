from enum import Enum

from src.constants import DifficultyScore


class BooleanField(Enum):
    Yes = 1
    No = 0

    @property
    def to_bool(self):
        return self is BooleanField.Yes


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
    NEETCODE_SOLUTIONS = "NeetCode Solutions"
    ROLES = "Roles"
    ADMIN = "Admin"
    CODEGRIND_TEAM = "CodeGrind Team"


CATEGORY_DESCRIPTIONS = {
    CommandCategory.HOME: f"""
# About CodeGrind Bot
The all-in-one Discord bot for LeetCode users. Track and compare your LeetCode stats against friends in server leaderboards, alongside searching and viewing LeetCode questions directly within Discord.

> Please note: while the bot uses the LeetCode API for data, it's not officially affiliated with LeetCode.

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

</add:1204499698933563422>: Add/connect your LeetCode account to this server's CodeGrind leaderboards.

</update:1204499698933563423>: Update your local and global CodeGrind profile preferences.

</remove:1204499698933563424>: Remove your profile from this server's CodeGrind leaderboards.
>    - `permanently` _(optional)_: Permanently delete all information CodeGrind stores on you.""",
    CommandCategory.LEADERBOARD: """
## Leaderboard

### Server leaderboard
</leaderboard:1243301101634060409> Display the CodeGrind leaderboard.
>    - `timeframe`: The desired timeframe (daily, weekly, monthly, or all-time).
>    - `global` _(optional)_: Whether display the Global CodeGrind leaderboards or the default local (server-only) leaderboards.
>    - `sorting` _(optional)_: The sorting method (score or win count).

Note: scores for `daily`, `weekly`, and `monthly` leaderboards will only start being tracked after an account is created. Any previous questions done that day/week/month will not be calculated into your score.""",
    CommandCategory.STATISTICS: """
## Statistics

</stats:1204499698317262966>: Returns the statistics of your or someone else's LeetCode account.
>    - `extension`: The extra information to add to the stats card (activity, heatmap, contest, or none). 
>    - `user` _(optional)_: The user to display the stats of. By default, it will be your account.

Credit to [LeetCode Stats Card](https://github.com/JacobLinCool/LeetCode-Stats-Card) for generating the visuals.""",
    CommandCategory.LEETCODE_PROBLEMS: """
## LeetCode Problems

</problem daily:1243573686666137673>: Returns LeetCode's problem of the day

</problem random:1243573686666137673>: Returns a random LeetCode problem.
>    - `difficulty` _(optional)_: A difficulty level (easy, medium or hard). By default this will be set to a random difficulty level.

</problem search:1243573686666137673>: Display your searched LeetCode problem.""",
    CommandCategory.NEETCODE_SOLUTIONS: """
## NeetCode Solutions

</neetcode:1252639140478976010>: Display NeetCode's solution for your searched LeetCode problem.
>    - `language` _(optional)_: The desired programming language""",
    CommandCategory.ROLES: """
## Roles

If an admin has enabled this feature using </roles:1204499698317262965>, you will receive the following roles. If you're an admin, check out the admin commands section to learn how to enable this feature.

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

</setup-feature roles:1264609825631764480>: Enable/disable automatically giving verified CodeGrind user, score milestones, and streak roles that will be automatically updated each day at midday (UTC).

## Notifications

</setup-feature notifications:1264609825631764480>: Enable/disable daily notifications being sent at midnight (UTC) to a channel.
>    - `channel` _(optional)_: The channel (e.g. "#home-channel") to send notifications to. By default this will be the channel where you ran this command.

Note: please press the 'save' button twice!""",
    CommandCategory.CODEGRIND_TEAM: """
## CodeGrind Team

### Developers
Kevin (<@335154148976885770>)
Nano (<@814656377188384810>)
Liam (<@344132308644659201>)

### Contributors
[Aqiil](<https://www.linkedin.com/in/abubakar-aqiil/>) (<@411495236326653965>): Added win-count sorting option to /leaderboard.
[Chris](<https://www.linkedin.com/in/chris-fowler-b3b96a191/>) (<@586527718653558796>): Created the /neetcode command.
[Valgo](<https://github.com/svn27/>) (<@659535036206415883>): Implemented tracking of the LeetCode language and skills problem count.
[Aalaap](<https://www.linkedin.com/in/aalaap-d-969703239/>) (<@635232267458969631>): Created the /problem commands.
[Shaan](<https://github.com/ShaanCoding>) (<@199662959964848128>): Created the /roles command.

Thank you to all the contributors for helping improve CodeGrind Bot!

Link to the repository: https://github.com/CodeGrind-Team/CodeGrind-Bot""",
}
