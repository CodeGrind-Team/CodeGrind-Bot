import os

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from models.server_model import Server
from models.user_model import User
from models.analytics_model import Analytics


async def init_mongodb_conn() -> None:
    mongodb_client = AsyncIOMotorClient(os.environ["MONGODB_URI"])

    await init_beanie(database=mongodb_client.bot,
                      document_models=[Server, User, Analytics])

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_mongodb_conn())
