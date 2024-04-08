import logging
import os
from datetime import datetime

import discord
import pytz
from discord.ext import commands
from dotenv import load_dotenv, find_dotenv
from html2image import Html2Image

load_dotenv(find_dotenv())

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(filename=f"logs/{datetime.now(pytz.timezone('Europe/London')).strftime('%Y%m%d-%H%M%S')}.log",
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='w')

logger = logging.getLogger()

hti = Html2Image(
    browser_executable=os.environ["BROWSER_EXECUTABLE_PATH"])

intents = discord.Intents().default()
intents.members = True
client = commands.Bot(command_prefix=',', intents=intents)

RATINGS = {}
