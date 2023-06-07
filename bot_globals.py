import logging
from datetime import datetime

import discord
import requests
from discord.ext import commands


logging.basicConfig(filename=f"logs/{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.log",
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='w')

logger = logging.getLogger()

session = requests.Session()
intents = discord.Intents().all()
client = commands.Bot(command_prefix=',', intents=intents)

DIFFICULTY_SCORE = {"easy": 1, "medium": 3, "hard": 7}
RANK_EMOJI = {1: "🥇", 2: "🥈", 3: "🥉"}

TIMEFRAME_TITLE = {"alltime": {"field": "total_score",
                               "title": "All-Time"}, "weekly": {"field": "week_score", "title": "Weekly"}}
