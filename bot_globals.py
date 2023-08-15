import logging
import os
from datetime import datetime

import discord
import pytz
from discord.ext import commands
from dotenv import load_dotenv
from html2image import Html2Image

load_dotenv()

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(filename=f"logs/{datetime.now(pytz.timezone('Europe/London')).strftime('%Y%m%d-%H%M%S')}.log",
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='w')

logger = logging.getLogger()

hti = Html2Image(
    browser_executable=os.environ["BROWSER_EXECUTABLE_PATH"])

intents = discord.Intents().all()
client = commands.Bot(command_prefix=',', intents=intents)

DIFFICULTY_SCORE = {"easy": 1, "medium": 3, "hard": 7}
RANK_EMOJI = {1: "🥇", 2: "🥈", 3: "🥉"}

TIMEFRAME_TITLE = {"alltime": {"field": "total_score", "title": "All-Time"},
                   "weekly": {"field": "week_score", "title": "Weekly"},
                   "daily": {"field": "day_score", "title": "Daily"},
                   "yesterday": {"field": "yesterday_score", "title": "Today's"},
                   "last_week": {"field": "last_week_score", "title": "This Week's"}}

RATINGS = {}

MILESTONE_ROLES = {
    1: ("Initiate (1 Point)", discord.Color.blue()),          # 1 Problem
    10: ("Problem Solver (10 Points)", discord.Color.green()),  # 10 Problems
    25: ("Algorithm Apprentice (25 Points)", discord.Color.gold()),  # 25 Problems
    50: ("Logic Guru (50 Points)", discord.Color.purple()),     # 50 Problems
    75: ("Code Crusader (75 Points)", discord.Color.orange()),  # 75 Problems
    100: ("LeetCode Legend (100 Points)", discord.Color.red()),  # 100 Problems
    150: ("Problem Connoisseur (150 Points)", discord.Color.teal()),  # 150 Problems
    200: ("Mastermind (200 Points)", discord.Color.dark_blue())  # 200 Problems
}

STREAK_ROLES = {
    3: ("Streak Starter (3 Days)", discord.Color.blue()),          # 3 Days
    7: ("Streak Challenger (7 Days)", discord.Color.green()),  # 7 Days
    14: ("Streak Conqueror (14 Days)", discord.Color.gold()),  # 14 Days
    30: ("Streak Legend (30 Days)", discord.Color.purple()),     # 30 Days
}

VERIFIED_ROLE = "CodeGrind Verified"


def calculate_scores(easy: int = 0, medium: int = 0, hard: int = 0) -> int:
    return easy * DIFFICULTY_SCORE['easy'] + medium * DIFFICULTY_SCORE['medium'] + hard * DIFFICULTY_SCORE['hard']
