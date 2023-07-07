import asyncio
import logging
import os
from datetime import datetime
from typing import Dict

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

file_lock = asyncio.Lock()

session = requests.Session()
intents = discord.Intents().all()
client = commands.Bot(command_prefix=',', intents=intents)

DIFFICULTY_SCORE = {"easy": 1, "medium": 3, "hard": 7}
RANK_EMOJI = {1: "🥇", 2: "🥈", 3: "🥉"}

TIMEFRAME_TITLE = {"alltime": {"field": "total_score", "title": "All-Time"},
                   "weekly": {"field": "week_score", "title": "Weekly"},
                   "daily": {"field": "today_score", "title": "Daily"},
                   "yesterday": {"field": "yesterday_score", "title": "Today's"},
                   "last_week": {"field": "last_week_score", "title": "Last Week's"}}


def read_ratings_txt() -> Dict:

    ratings = {}

    with open('ratings.txt', 'r', encoding="UTF-8") as file:
        lines = file.readlines()

        for line in lines:
            line_data = line.strip().split('\t')
            rating = float(line_data[0])
            question_id = int(line_data[1])
            question_name = line_data[2].strip().lower()

            ratings[question_id] = {
                'question_name': question_name,
                'rating': rating
            }

            ratings[question_name] = {
                'rating': rating
            }

    return ratings


RATINGS = read_ratings_txt()
