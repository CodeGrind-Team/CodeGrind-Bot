import discord
from enum import Enum


class Period(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    ALLTIME = "alltime"


class DifficultyScore(Enum):
    EASY = 1
    MEDIUM = 3
    HARD = 7


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    RANDOM = 4


class RankEmoji(Enum):
    FIRST = "🥇"
    SECOND = "🥈"
    THIRD = "🥉"


class StatsCardOptions(Enum):
    ACTIVITY = 1
    HEATMAP = 2
    # TODO: COMPETITIONS = 3


class NotificationOptions(Enum):
    DAILY_QUESTION = "daily_question"
    WINNERS = "winners"
    MAINTENANCE = "maintenance"


GLOBAL_LEADERBOARD_ID = 0

MILESTONE_ROLES = {
    1: ("Novice (1 pt)", discord.Colour.dark_grey()),
    100: ("Apprentice (100 pts)", discord.Colour.green()),
    300: ("Capable (300 pts)", discord.Colour.blue()),
    500: ("Competent (500 pts)", discord.Colour.dark_blue()),
    1000: ("Advanced (1000 pts)", discord.Colour.orange()),
    2000: ("Expert (2000 pts)", discord.Colour.red()),
    4000: ("Master (4000 pts)", discord.Colour.purple()),
    8000: ("Legend (6000 pts)", discord.Colour.gold()),
}

STREAK_ROLES = {
    3: ("Streak Initiate (3 Days)", discord.Colour.green()),
    7: ("Streak Pursuer (7 Days)", discord.Colour.blue()),
    14: ("Streak Adventurer (14 Days)", discord.Colour.red()),
    30: ("Streak Dominator (30 Days)", discord.Colour.purple()),
    90: ("Streak Legend (90 Days)", discord.Colour.gold()),
}

VERIFIED_ROLE = "CodeGrind Verified"
