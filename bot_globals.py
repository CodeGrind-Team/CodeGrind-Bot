import logging
import os
from datetime import datetime

import discord
import pytz
import requests
from discord.ext import commands

if not os.path.exists('data'):
    os.makedirs('data')

if not os.path.exists('logs'):
    os.makedirs('logs')

TIMEZONE = pytz.timezone('Europe/London')

logging.basicConfig(filename=f"logs/{datetime.now(TIMEZONE).strftime('%Y%m%d-%H%M%S')}.log",
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='w')

logger = logging.getLogger()

session = requests.Session()
intents = discord.Intents().all()
client = commands.Bot(command_prefix=',', intents=intents)

DIFFICULTY_SCORE = {"easy": 1, "medium": 3, "hard": 7}
RANK_EMOJI = {1: "🥇", 2: "🥈", 3: "🥉"}

TIMEFRAME_TITLE = {"alltime": {"field": "total_score",
                               "title": "All-Time"}, "weekly": {"field": "week_score", "title": "Weekly"}, "daily": {"field": "today_score", "title": "Daily"}}
