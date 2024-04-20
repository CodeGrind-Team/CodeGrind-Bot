from beanie.odm.operators.update.array import Pull
from discord.ext import commands

from constants import GLOBAL_LEADERBOARD_ID
from database.models.preference_model import Preference
from database.models.server_model import Server
from database.models.user_model import User


async def remove_inactive_users(bot: commands.Bot) -> None:
    async for server in Server.all():
        if server.id == GLOBAL_LEADERBOARD_ID:
            continue

        # So that we can access user.id.
        await server.fetch_all_links()

        guild = bot.get_guild(server.id)

        delete_server = False
        # Delete server document if the bot isn't in the server anymore
        if not guild or guild not in bot.guilds:
            delete_server = True

        for user in server.users:
            # Unlink user if server was deleted or if bot is not in the server anymore
            # Or if the user is not in the server anymore.
            unlink_user = not guild or not guild.get_member(
                user.id) or delete_server

            if unlink_user:
                await Preference.find_one(
                    Preference.user == user,
                    Preference.server == server).delete()

                await Server.find_one(Server.id == server.id).update(
                    Pull({Server.users: {"$id": user.id}}))

                bot.logger.info(
                    "file: utils/notifications_utils.py ~ remove_inactive_users ~ user \
                        unlinked from server ~ user_id: %s, server_id: %s",
                    user.id,
                    server.id)

        if delete_server:
            await server.delete()

            bot.logger.info(
                "file: utils/notifications_utils.py ~ remove_inactive_users ~ server \
                    document deleted ~ id: %s", server.id)

    async for user in User.all():
        preferences = await Preference.find_one(Preference.user == user).count()
        # Delete user document if they're not in any server with the bot in it except
        # the global leaderboard.
        if preferences <= 1:
            await Server.find_one(Server.id == GLOBAL_LEADERBOARD_ID).update(
                Pull({Server.users: {"$id": user.id}}))

            await user.delete()

            bot.logger.info(
                "file: utils/notifications_utils.py ~ remove_inactive_users ~ \
                    user document deleted ~ id: %s", user.id)
