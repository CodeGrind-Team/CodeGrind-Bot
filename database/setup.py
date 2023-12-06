import os

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from database.models.analytics_model import Analytics
from database.models.server_model import Server
from database.models.user_model import User


async def init_mongodb_conn() -> None:
    mongodb_client = AsyncIOMotorClient(os.environ["MONGODB_URI"])

    await init_beanie(database=mongodb_client.bot,
                      document_models=[Server, User, Analytics])

    # Create global leaderboard 'server' with id 0.
    server = await Server.get(0)
    if not server:
        server = Server(id=0)
        await server.create()

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_mongodb_conn())
