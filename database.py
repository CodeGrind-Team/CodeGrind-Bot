import asyncio
import os

from beanie import init_beanie
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from models.server_model import Server
from models.user_model import User

load_dotenv()


async def init_mongodb_conn():
    mongodb_client = AsyncIOMotorClient(os.environ["MONGODB_URI"])

    await init_beanie(database=mongodb_client.bot,
                      document_models=[Server, User])  # type: ignore

if __name__ == "__main__":
    asyncio.run(init_mongodb_conn())
