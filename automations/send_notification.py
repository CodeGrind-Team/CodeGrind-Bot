import os
import sys

# Make the directory to the root folder so that the other files can be imported
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, '..'))
sys.path.append(parent_path)

import asyncio
import discord
from beanie import init_beanie
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from bot_globals import client
from database.models.server_model import Server
from database.models.user_model import User

load_dotenv()


@client.event
async def on_ready() -> None:
    # Global variables
    message = """## CodeGrind Bot Update (02/09/2023): Overhauled LeetCode Question Commands!

Hello everyone! We're excited to share the new </search-question:1147609257735364668>, </daily-question:1147609257735364669>, and </search-question:1147609257735364668> commands that will display
all the crucial information about the chosen LeetCode question directly in Discord.

Thank you to Aalaap (<https://www.linkedin.com/in/aalaap-d-969703239/>) for contributing this feature.

Note:
- /question, /random, and /rating commands have been removed in replace of the new question commands.

Here's an example of how it now looks:"""

    # Don't include a file by setting this to None
    image_path = "D:/Pictures/LeetCode Bot/question_commands.png"

    # The notification type(s) to send the message to. One from: "maintenance", "daily_question", "winner"
    notification_type = "maintenance"

    mongodb_client = AsyncIOMotorClient(os.environ["MONGODB_URI"])

    await init_beanie(database=mongodb_client.bot,
                      document_models=[Server, User])

    async for server in Server.all():
        if not server.channels:
            continue

        if "maintenance" in notification_type:
            for channel_id in server.channels.maintenance:
                channel = client.get_channel(channel_id)

                if not channel or not isinstance(channel, discord.TextChannel):
                    continue

                try:
                    if image_path:
                        await channel.send(content=message, file=discord.File(image_path))
                    else:
                        await channel.send(content=message)

                except discord.errors.Forbidden as e:
                    print(e)

        elif "daily_question" in notification_type:
            for channel_id in server.channels.dail_question:
                channel = client.get_channel(channel_id)

                if not channel or not isinstance(channel, discord.TextChannel):
                    continue

                try:
                    if image_path:
                        await channel.send(content=message, file=discord.File(image_path))
                    else:
                        await channel.send(content=message)
                except discord.errors.Forbidden as e:
                    print(e)

        elif "winner" in notification_type:
            for channel_id in server.channels.winner:
                channel = client.get_channel(channel_id)

                if not channel or not isinstance(channel, discord.TextChannel):
                    continue

                try:
                    if image_path:
                        await channel.send(content=message, file=discord.File(image_path))
                    else:
                        await channel.send(content=message)
                except discord.errors.Forbidden as e:
                    print(e)

    print("DONE!")


async def main(token: str) -> None:
    async with client:
        await client.start(token)

if __name__ == "__main__":
    token = os.environ['TOKEN']
    asyncio.run(main(token))
