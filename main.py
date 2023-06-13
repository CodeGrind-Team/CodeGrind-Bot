import asyncio
import logging
import os
from datetime import datetime, timedelta

import discord
import requests
from dotenv import load_dotenv

from bot_globals import TIMEZONE, client, logger
from cogs.stats import update_stats

load_dotenv()


async def wait_until_next_hour():
    now = datetime.now(TIMEZONE)
    next_hour = (now + timedelta(hours=1)).replace(minute=0,
                                                   second=0, microsecond=30)

    logger.info(
        "file: main.py ~ wait_until_next_hour ~ next_hour: %s", next_hour)

    seconds_to_wait = (next_hour - now).total_seconds()
    await asyncio.sleep(seconds_to_wait)


async def send_daily_question_and_update_stats():
    logger.info("file: main.py ~ send_daily_question_and_update_stats ~ run")

    while not client.is_closed():
        now = datetime.now(TIMEZONE)

        logger.info(
            "file: main.py ~ send_daily_question_and_update_stats ~ %s:%s", now.minute, now.hour)

        # daily changes at midnight UTC rather than BST
        if datetime.utcnow().hour == 0:
            # get the channel object
            # send the message
            url = 'https://leetcode.com/graphql'

            headers = {
                'Content-Type': 'application/json',
            }

            data = {
                'operationName':
                'daily',
                'query':
                '''
                query daily {
                    challenge: activeDailyCodingChallengeQuestion {
                        date
                        link
                        question {
                            difficulty
                            title
                        }
                    }
                }
            '''
            }

            response = requests.post(
                url, json=data, headers=headers, timeout=10)
            response_data = response.json()

            # Extract and print the link
            link = response_data['data']['challenge']['link']
            link = f"https://leetcode.com{link}"
            # Extract and print the title
            title = response_data['data']['challenge']['question']['title']
            # Extract and print the difficulty
            difficulty = response_data['data']['challenge']['question']['difficulty']
            # Extract and print the date
            embed = discord.Embed(title=f"Daily Problem: {title}",
                                  color=discord.Color.blue())
            embed.add_field(name="**Difficulty**",
                            value=f"{difficulty}", inline=True)
            embed.add_field(name="**Link**", value=f"{link}", inline=False)
            # import channels from dailychannels.txt
            with open('dailychannels.txt', 'r', encoding="UTF-8") as f:
                channels = f.readlines()
            channels = [channel.strip() for channel in channels]
            for channel_id in channels:
                channel = client.get_channel(int(channel_id))
                await channel.send(embed=embed)
                # Pin the message
                async for message in channel.history(limit=1):
                    try:
                        await message.pin()
                    except discord.errors.Forbidden as e:
                        logger.exception(
                            "file: main.py ~ message not pinned due to missing permissions ~ exception: %s", e)

            logger.info("file: main.py ~ daily retrieved and pinned")

        daily_reset = now.hour == 0
        weekly_reset = now.weekday() == 0 and now.hour == 0
        await update_stats(client, now, daily_reset, weekly_reset)

        await wait_until_next_hour()


@client.event
async def on_ready():
    logger.info("file: main.py ~ on_ready ~ %s",
                datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
    logger.info("file: main.py ~ logged in as a bot %s", client.user)
    server_ids = [guild.id for guild in client.guilds]
    logger.info('file: main.py ~ server IDs: %s', server_ids)

    if os.environ["UPDATE_STATS_ON_START"] == "True":
        await update_stats(client, datetime.now(TIMEZONE))

    try:
        synced = await client.tree.sync()
        logger.info("file: main.py ~ synced %s commands", len(synced))
        await send_daily_question_and_update_stats()
    except Exception as e:
        logger.exception("file: main.py ~ on_ready ~ exception: %s", e)


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await client.load_extension(f"cogs.{filename[:-3]}")


async def main(token: str):
    async with client:
        await load_extensions()
        await client.start(token)


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logger.info("Logger is in DEBUG mode")

    token = os.environ['TOKEN']

    asyncio.run(main(token))
