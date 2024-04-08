import discord
from enum import Enum


class Period(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALLTIME = "alltime"


class DifficultyScore(Enum):
    EASY = 1
    MEDIUM = 3
    HARD = 7


class RankEmoji(Enum):
    FIRST = "🥇"
    SECOND = "🥈"
    THIRD = "🥉"


class TimeframeTitle(Enum):
    ALLTIME = {"field": "total_score", "title": "All-Time"}
    WEEKLY = {"field": "week_score", "title": "Weekly"}
    DAILY = {"field": "day_score", "title": "Daily"}
    YESTERDAY = {"field": "yesterday_score", "title": "Today's"}
    LAST_WEEK = {"field": "last_week_score", "title": "This Week's"}


MILESTONE_ROLES = {
    1: ("Novice (1 pt)", discord.Color.dark_grey()),
    100: ("Apprentice (100 pts)", discord.Color.green()),
    300: ("Capable (300 pts)", discord.Color.blue()),
    500: ("Competent (500 pts)", discord.Color.dark_blue()),
    1000: ("Advanced (1000 pts)", discord.Color.orange()),
    2000: ("Expert (2000 pts)", discord.Color.red()),
    4000: ("Master (4000 pts)", discord.Color.purple()),
    8000: ("Legend (6000 pts)", discord.Color.gold())
}

STREAK_ROLES = {
    3: ("Streak Initiate (3 Days)", discord.Color.green()),
    7: ("Streak Pursuer (7 Days)", discord.Color.blue()),
    14: ("Streak Adventurer (14 Days)", discord.Color.red()),
    30: ("Streak Dominator (30 Days)", discord.Color.purple()),
    90: ("Streak Legend (90 Days)", discord.Color.gold()),
}

VERIFIED_ROLE = "CodeGrind Verified"
