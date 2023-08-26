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

intents = discord.Intents().default()
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


def calculate_scores(easy: int = 0, medium: int = 0, hard: int = 0) -> int:
    return easy * DIFFICULTY_SCORE['easy'] + medium * DIFFICULTY_SCORE['medium'] + hard * DIFFICULTY_SCORE['hard']
