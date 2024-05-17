import asyncio
import random
import string
from datetime import datetime

import aiohttp
import discord
from beanie.odm.fields import WriteRules
from beanie.odm.operators.update.array import AddToSet
from bson import DBRef

from constants import GLOBAL_LEADERBOARD_ID
from database.models.preference_model import Preference
from database.models.record_model import Record
from database.models.server_model import Server
from database.models.user_model import Stats, Submissions, User
from embeds.users_embeds import (
    connect_account_instructions_embed,
    profile_added_embed,
    synced_existing_user_embed,
    user_already_added_in_server_embed,
)
from utils.common_utils import convert_to_score
from utils.questions_utils import fetch_problems_solved_and_rank
from utils.roles_utils import give_verified_role
from discord.ext import commands


async def register(
    bot: commands.Bot,
    interaction: discord.Interaction,
    send_message: discord.Webhook,
    server_id: int,
    user_id: int,
    leetcode_id: str,
) -> None:
    """
    Registers a user to the system for the selected server.

    :param interaction: The Discord interaction.
    :param send_message: The webhook to send messages.
    :param server_id: The ID of the server to register the user into.
    :param user: The user to register.
    :param leetcode_id: The LeetCode ID of the user.
    """

    matched = await linking_process(bot, send_message, leetcode_id)

    if not matched:
        embed = profile_added_embed(leetcode_id, added=False)
        await interaction.edit_original_response(embed=embed)
        return

    async with aiohttp.ClientSession() as client_session:
        stats = await fetch_problems_solved_and_rank(bot, client_session, leetcode_id)

    if not stats:
        return

    score = convert_to_score(
        easy=stats.submissions.easy,
        medium=stats.submissions.medium,
        hard=stats.submissions.hard,
    )

    user = User(
        id=user_id,
        leetcode_id=leetcode_id,
        stats=Stats(
            submissions=Submissions(
                easy=stats.submissions.easy,
                medium=stats.submissions.medium,
                hard=stats.submissions.hard,
                score=score,
            )
        ),
    )

    record = Record(
        timestamp=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
        user_id=user_id,
        submissions=Submissions(
            easy=stats.submissions.easy,
            medium=stats.submissions.medium,
            hard=stats.submissions.hard,
            score=score,
        ),
    )

    preference_server = Preference(
        user_id=user_id,
        server_id=server_id,
        # Use server username.
        name=interaction.user.display_name,
    )

    preference_global = Preference(
        user_id=user_id,
        server_id=GLOBAL_LEADERBOARD_ID,
        # User account username.
        name=interaction.user.name,
    )

    await Server.find_one(Server.id == server_id).update(AddToSet({Server.users: user}))
    # ! Check how to do this properly
    # ! Maybe issues with writeruling the user the using the user object in record
    # ! preference_server and preference_global
    # Link rule to create a new document for the new user link.
    await (await Server.get(server_id)).save(link_rule=WriteRules.WRITE)
    await record.create()
    await preference_server.create()
    await preference_global.create()

    # Add to the global leaderboard.
    await Server.find_one(Server.id == GLOBAL_LEADERBOARD_ID).update(
        AddToSet({Server.users: user})
    )

    await give_verified_role(interaction.guild, interaction.user)

    await interaction.edit_original_response(embed=profile_added_embed(leetcode_id))


async def login(
    interaction: discord.Interaction,
    send_message: discord.Webhook,
    user_id: int,
    server_id: int,
    user_display_name: str,
) -> None:
    """
    Logs in a user to a server if user already exists.

    :interaction: The Discord interaction.
    :param send_message: The webhook to send messages.
    :param user_id: The user to log in.
    :param server_id: The ID of the server to log the user into.
    :param user_display_name: The display name of the user.
    """
    await give_verified_role(interaction.guild, interaction.user)

    preference = await Preference.find_one(
        Preference.user_id == user_id,
        Preference.server_id == server_id,
    )

    if preference:
        # User has already been added to the server.
        embed = user_already_added_in_server_embed()
        await send_message(embed=embed)
    else:
        # Add user's preferences for this server.
        preference = Preference(
            user_id=user_id,
            server_id=server_id,
            name=user_display_name,
        )

        await preference.create()

        await Server.find_one(Server.id == server_id).update(
            AddToSet({Server.users: DBRef("users", user_id)})
        )

        embed = synced_existing_user_embed()
        await send_message(embed=embed)


async def linking_process(
    bot: commands.Bot, send_message: discord.Webhook, leetcode_id: str
) -> None:
    """
    Initiates the account linking process.

    :param send_message: The webhook to send messages.
    :param leetcode_id: The LeetCode ID of the user.
    """

    # Generate a random string for account linking
    generated_string = "".join(random.choices(string.ascii_letters, k=8))

    await send_message(
        embed=connect_account_instructions_embed(generated_string, leetcode_id),
        ephemeral=True,
    )

    profile_name = None

    # TODO: Use self.config
    duration = 60  # seconds
    check_interval = 5  # seconds

    async with aiohttp.ClientSession() as client_session:
        # Check if the profile name matches the generated string
        for _ in range(duration // check_interval):
            stats = await fetch_problems_solved_and_rank(
                bot,
                client_session,
                leetcode_id,
            )

            if not stats:
                break

            profile_name = stats.real_name

            if profile_name == generated_string:
                break

            await asyncio.sleep(check_interval)

    return profile_name == generated_string


# async def remove_inactive_users(bot: commands.Bot) -> None:
#     """
#     Remove users and servers that are inactive.

#     :param bot: The Discord bot.
#     """
#     async for server in Server.all():
#         if server.id == GLOBAL_LEADERBOARD_ID:
#             continue

#         # So that we can access user.id.
#         await server.fetch_all_links()

#         guild = bot.get_guild(server.id)

#         delete_server = False
#         # Delete server document if the bot isn't in the server anymore
#         if not guild or guild not in bot.guilds:
#             delete_server = True

#         for user in server.users:
#             # Unlink user if server was deleted or if bot is not in the server anymore
#             # Or if the user is not in the server anymore.
#             unlink_user = not guild or not guild.get_member(
#                 user.id) or delete_server

#             if unlink_user:
#                 await Preference.find_one(
#                     Preference.user == user,
#                     Preference.server == server).delete()

#                 await Server.find_one(Server.id == server.id).update(
#                     Pull({Server.users: {"$id": user.id}}))

#                 bot.logger.info(
#                     "file: utils/notifications_utils.py ~ remove_inactive_users ~ user \
#                         unlinked from server ~ user_id: %s, server_id: %s",
#                     user.id,
#                     server.id)

#         if delete_server:
#             await server.delete()

#             bot.logger.info(
#                 "file: utils/notifications_utils.py ~ remove_inactive_users ~ server \
#                     document deleted ~ id: %s", server.id)

#     async for user in User.all():
#         preferences = await Preference.find_one(Preference.user == user).count()
#         # Delete user document if they're not in any server with the bot in it except
#         # the global leaderboard.
#         if preferences <= 1:
#             await Server.find_one(Server.id == GLOBAL_LEADERBOARD_ID).update(
#                 Pull({Server.users: {"$id": user.id}}))

#             await user.delete()

#             bot.logger.info(
#                 "file: utils/notifications_utils.py ~ remove_inactive_users ~ \
#                     user document deleted ~ id: %s", user.id)
