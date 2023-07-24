import os
import sys

# Make the directory to the root folder so that the other files can be imported
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, '../..'))
sys.path.append(parent_path)

from random import randint

from beanie import init_beanie
from beanie.odm.fields import WriteRules
from beanie.odm.operators.update.array import AddToSet
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from bot_globals import calculate_scores
from models.server_model import Server
from models.user_model import DisplayInformation, Scores, Submissions, User

load_dotenv()

async def create_user(server_id: int, user_id: int, leetcode_username: str, name: str, rank: int, url_bool: bool, easy: int, medium: int, hard: int):
    display_information = DisplayInformation(
        server_id=server_id, name=name, url=url_bool)

    total_score = calculate_scores(easy, medium, hard)

    submissions = Submissions(
        easy=easy, medium=medium, hard=hard, total_score=total_score)

    scores = Scores(start_of_week_total_score=total_score,
                    start_of_day_total_score=total_score)

    user = User(id=user_id, leetcode_username=leetcode_username, rank=rank, display_information=[
                display_information], submissions=submissions, scores=scores)

    await Server.find_one(Server.id == server_id).update(AddToSet({Server.users: user}))
    server = await Server.get(server_id)
    # link rule to create a new document for the new link
    await server.save(link_rule=WriteRules.WRITE)

async def init_mongodb_conn(server_id: int, number_of_users: int) -> None:
    mongodb_client = AsyncIOMotorClient(os.environ["MONGODB_URI"])

    await init_beanie(database=mongodb_client.bot,
                      document_models=[Server, User])

    for i in range(number_of_users):
        user_id = i
        leetcode_username = f"user {i}"
        name = f"user {i}"
        rank = i
        url_bool = False
        # Multiply by random numbers to add variety to the scores
        easy = i * randint(0, 10)
        medium = i * randint(0, 5)
        hard = i * randint(0, 2)
        await create_user(server_id, user_id, leetcode_username, name, rank, url_bool, easy, medium, hard)

if __name__ == "__main__":
    import asyncio

    # The server you want to add the dummy users to
    server_id = int(input("Server ID: "))
    # The number of dummy users you want to be added
    number_of_users = int(input("Number of dummy users to generate: "))
    asyncio.run(init_mongodb_conn(server_id, number_of_users))