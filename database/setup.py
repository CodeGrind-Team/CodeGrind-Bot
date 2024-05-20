import os

from beanie import init_beanie
from .models import Preference, Record, Server, User
from motor.motor_asyncio import AsyncIOMotorClient


async def initialise_mongodb_conn(mongodb_uri: str, global_leaderboard_id: int) -> None:
    """
    Initialise the MongoDB connection and create the necessary collections

    :param mongodb_uri: The MongoDB URI
    """
    mongodb_client = AsyncIOMotorClient(mongodb_uri)

    await init_beanie(
        database=mongodb_client.bot,
        document_models=[Preference, Record, Server, User],
    )

    # Create global leaderboard 'server' with id 0.
    server = await Server.get(global_leaderboard_id)
    if not server:
        server = Server(id=0)
        await server.create()


if __name__ == "__main__":
    import asyncio

    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
    asyncio.run(initialise_mongodb_conn(os.getenv("MONGODB_URI")))
