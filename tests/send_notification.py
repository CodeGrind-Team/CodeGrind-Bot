import asyncio
import io
import os
import sys

# Make the directory to the root folder so that the other files can be imported
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, '..'))
sys.path.append(parent_path)

import discord
from beanie import init_beanie
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from bot_globals import client
from models.server_model import Server
from models.user_model import User

load_dotenv()

def add_file(image_path: str | None = None) -> discord.File:
    with open(image_path, "rb") as f:
        # read the file contents
        data = f.read()
        # create a BytesIO object from the data
        image_binary = io.BytesIO(data)
        # move the cursor to the beginning
        image_binary.seek(0)

        file = discord.File(
            fp=image_binary, filename=f"image.png")

    return file

@client.event
async def on_ready() -> None:
    # Global variables
    message = """## CodeGrind Bot Update (14/08/2023): Improved </stats:1115756888664060014>

Hello everyone! We have overhauled the stats command with more statistics and a massively improved design.
Credit to github.com/JacobLinCool/LeetCode-Stats-Card for the LeetCode Stats Card endpoint!

Using </stats:1115756888664060014>, you can now easily select a specific user from the server if they've already connected their account to the server and their `include_url` setting is set to on.

Here's an example of how it now looks like:"""

    # Don't include a file by setting this to None
    file = add_file("C:/Users/kevro/Downloads/image.png")

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
                
                if not isinstance(channel, discord.TextChannel):
                    continue

                try:
                    if file:
                        await channel.send(content=message, file=file)
                    else:
                        await channel.send(content=message)

                except discord.errors.Forbidden as e:
                    print(e)

        elif "daily_question" in notification_type:
            for channel_id in server.channels.dail_question:
                channel = client.get_channel(channel_id)

                if not isinstance(channel, discord.TextChannel):
                    continue

                try:
                    if file:
                        await channel.send(content=message, file=file)
                    else:
                        await channel.send(content=message)
                except discord.errors.Forbidden as e:
                    print(e)

        elif "winner" in notification_type:
            for channel_id in server.channels.winner:
                channel = client.get_channel(channel_id)

                if not isinstance(channel, discord.TextChannel):
                    continue

                try:
                    if file:
                        await channel.send(content=message, file=file)
                    else:
                        await channel.send(content=message)
                except discord.errors.Forbidden as e:
                    print(e)

        
    print("DONE!")


async def main(token: str) -> None:
    async with client:
        await client.start(token)

#notification_types, message, file

if __name__ == "__main__":
    token = os.environ['TOKEN']
    asyncio.run(main(token))