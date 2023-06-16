import asyncio
from datetime import datetime, timedelta

import discord
import requests

from bot_globals import TIMEZONE, client, logger
from cogs.stats import update_stats
from utils.leaderboards import send_leaderboard_winners


async def wait_until_next_half_hour():
    now = datetime.now(TIMEZONE)

    if now.minute < 30:
        next_half_hour = now.replace(minute=30, second=0, microsecond=30)
    else:
        next_half_hour = (now + timedelta(hours=1)).replace(minute=0,
                                                            second=0, microsecond=30)

    logger.info(
        "file: utils/message_scheduler.py ~ wait_until_next_half_hour ~ next_half_hour: %s", next_half_hour)

    seconds_to_wait = (next_half_hour - now).total_seconds()
    await asyncio.sleep(seconds_to_wait)


async def send_daily_question_and_update_stats():
    logger.info(
        "file: utils/message_scheduler.py ~ send_daily_question_and_update_stats ~ run")

    lock = asyncio.Lock()

    while not client.is_closed():
        # daily changes at midnight UTC rather than BST
        if datetime.utcnow().hour == 0 and datetime.utcnow().minute == 0:
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
                            "file: utils/message_scheduler.py ~ message not pinned due to missing permissions ~ exception: %s", e)

            logger.info(
                "file: utils/message_scheduler.py ~ daily retrieved and pinned")

        await wait_until_next_half_hour()

        now = datetime.now(TIMEZONE)
        daily_reset = now.hour == 0 and now.minute == 0
        weekly_reset = now.weekday() == 0 and now.hour == 0 and now.minute == 0

        async with lock:
            if daily_reset:
                await send_leaderboard_winners("daily")

            if weekly_reset:
                await send_leaderboard_winners("weekly")

        async with lock:
            await update_stats(client, now, daily_reset, weekly_reset)
