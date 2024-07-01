import os

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from .models import Profile, Record, Server, User


async def initialise_mongodb_conn(
    mongodb_uri: str, global_leaderboard_id: int = 0
) -> None:
    """
    Initialise the MongoDB connection and create the necessary collections

    :param mongodb_uri: The MongoDB URI
    """
    mongodb_client = AsyncIOMotorClient(mongodb_uri)

    await init_beanie(
        database=mongodb_client.bot,
        document_models=[Profile, Record, Server, User],
    )

    server = await Server.get(global_leaderboard_id)
    if not server:
        server = Server(id=global_leaderboard_id)
        await server.create()


if __name__ == "__main__":
    import asyncio

    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
    asyncio.run(initialise_mongodb_conn(os.getenv("MONGODB_URI")))
