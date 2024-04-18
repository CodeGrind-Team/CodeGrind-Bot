from beanie.odm.operators.update.array import Pull

from bot_globals import bot, logger
from database.models.server_model import Server
from database.models.user_model import User


async def remove_inactive_users() -> None:
    async for server in Server.all():
        # Make exception for global leaderboard server.
        if server.id == 0:
            continue

        # So that we can access user.id
        await server.fetch_all_links()

        guild = bot.get_guild(server.id)

        delete_server = False
        # Delete server document if the bot isn't in the server anymore
        if not guild or guild not in bot.guilds:
            delete_server = True

        for user in server.users:
            # unlink user if server was deleted or if bot not in the server anymore
            unlink_user = not guild or not guild.get_member(
                user.id) or delete_server

            # Unlink user from server if they're not in the server anymore
            if unlink_user:
                await User.find_one(User.id == user.id).update(Pull({User.display_information: {"server_id": server.id}}))
                await Server.find_one(Server.id == server.id).update(Pull({Server.users: {"$id": user.id}}))

                logger.info(
                    "file: utils/notifications_utils.py ~ remove_inactive_users ~ user unlinked from server ~ user_id: %s, server_id: %s", user.id, server.id)

        if delete_server:
            await server.delete()

            logger.info(
                "file: utils/notifications_utils.py ~ remove_inactive_users ~ server document deleted ~ id: %s", server.id)

    async for user in User.all():
        # Delete user document if they're not in any server with the bot in it except the global leaderboard
        if len(user.display_information) == 1:
            await Server.find_one(Server.id == 0).update(Pull({Server.users: {"$id": user.id}}))
            await user.delete()

            logger.info(
                "file: utils/notifications_utils.py ~ remove_inactive_users ~ user document deleted ~ id: %s", user.id)
