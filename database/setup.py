import os

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from .models.analytics_model import Analytics
from .models.server_model import Server
from .models.user_model import User


async def init_mongodb_conn(mongodb_uri: str, global_leaderboard_id: int) -> None:
    """
    Initialize MongoDB connection and create the necessary collections.

    :param mongodb_uri: The MongoDB URI.
    """
    mongodb_client = AsyncIOMotorClient(mongodb_uri)

    await init_beanie(
        database=mongodb_client.bot, document_models=[Server, User, Analytics]
    )

    # Create global leaderboard 'server' with id 0.
    server = await Server.get(global_leaderboard_id)
    if not server:
        server = Server(id=0)
        await server.create()


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_mongodb_conn(os.getenv("MONGODB_URI"), 0))
