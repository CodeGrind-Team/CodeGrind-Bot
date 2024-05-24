import asyncio
import random
import string
from datetime import datetime
from typing import TYPE_CHECKING

import aiohttp
import discord
from beanie.odm.operators.update.array import AddToSet, Pull
from bson import DBRef

from constants import GLOBAL_LEADERBOARD_ID
from database.models import Preference, Record, Server, Stats, Submissions, User
from ui.embeds.users import (
    connect_account_instructions_embed,
    profile_added_embed,
    synced_existing_user_embed,
    user_already_added_in_server_embed,
)
from utils.common import convert_to_score
from utils.problems import fetch_problems_solved_and_rank
from utils.roles import give_verified_role

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


async def register(
    bot: "DiscordBot",
    interaction: discord.Interaction,
    send_message: discord.Webhook,
    server_id: int,
    user_id: int,
    leetcode_id: str,
) -> None:
    """
    Registers a user to the system for the selected server.

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
        url=False,
    )

    await user.save()
    await record.create()
    await preference_server.create()
    await preference_global.create()

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
    bot: "DiscordBot", send_message: discord.Webhook, leetcode_id: str
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


async def unlink_user_from_server(user_id: int, server_id: int) -> None:
    """
    Removes user's profile for specified server.

    :param send_message: The webhook to send messages.
    :param leetcode_id: The LeetCode ID of the user.
    """
    await Preference.find_many(
        Preference.user_id == user_id, Preference.server_id == server_id
    ).delete()

    await Server.find_one(Server.id == server_id).update(
        Pull({Server.users: {"$id": user_id}})
    )


async def delete_user(user_id: int) -> None:
    """
    Deletes all of user's stored information.

    :param user_id: The user's id.
    """
    async for preference in Preference.find_many(Preference.user_id == user_id):
        await Server.find_one(Server.id == preference.server_id).update(
            Pull({Server.users: {"$id": user_id}})
        )

    await Preference.find_many(Preference.user_id == user_id).delete()
    await Record.find_many(Record.user_id == user_id).delete()
    await User.find_one(User.id == user_id).delete()
