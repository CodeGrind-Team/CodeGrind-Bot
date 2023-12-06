from beanie.odm.operators.update.array import AddToSet

from bot_globals import client, logger
from database.models.server_model import Server
from database.models.user_model import DisplayInformation, User


async def link_all_users_to_server():
    """Run at the end of on_ready client event."""
    async for user in User.all():
        logger.info(user.id)
        await link_user_to_server(user)


async def link_user_to_server(user: User, server_id: int = 0) -> None:
    if user.id < 100:
        return

    discord_user = await client.fetch_user(user.id)

    if discord_user is None:
        return

    display_information = DisplayInformation(
        server_id=server_id, name=discord_user.name, url=False)

    await User.find_one(User.id == user.id).update(AddToSet({User.display_information: display_information}))
    await Server.find_one(Server.id == server_id).update(AddToSet({Server.users: DBRef("users",  user.id)}))
