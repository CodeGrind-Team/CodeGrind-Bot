import asyncio
import logging
import os
from datetime import datetime

import discord
import requests
from dotenv import load_dotenv

from bot_globals import client, logger
from cogs.stats import update_stats

load_dotenv()


async def send_message_at_midnight():
    await client.wait_until_ready()
    while not client.is_closed():
        await asyncio.sleep(3600)  # sleep for a hour
        now = datetime.utcnow()

        logger.debug("%s %s", now.hour, now.minute)
        if now.hour == 0:
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
                url, json=data, headers=headers, timeout=5)
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
                    await message.pin()

        if now.hour == 0 or now.hour == 6 or now.hour == 12 or now.hour == 18:
            weekly_reset = now.weekday() == 0 and now.hour == 0
            update_stats(client, weekly_reset)


@client.event
async def on_ready():
    logger.info("%s %s", datetime.utcnow().hour,
                datetime.utcnow().time)
    logger.info("Logged in as a bot %s", client.user)
    server_ids = [guild.id for guild in client.guilds]
    logger.info('Server IDs: %s', server_ids)

    update_stats(client, datetime.now())
    logger.info("Stats updated")

    try:
        synced = await client.tree.sync()
        logger.info("Synced %s commands", len(synced))
    except Exception as e:
        logger.exception(e)
    await send_message_at_midnight()


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
    logger.setLevel(logging.DEBUG)
    logger.info("Logger is in DEBUG mode")

    token = os.environ['TOKEN']

    asyncio.run(main(token))
