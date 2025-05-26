import asyncio
import random
import string
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Awaitable, Callable, Optional

import discord

from src.constants import GLOBAL_LEADERBOARD_ID
from src.database.models import Preference, Profile, Record, Stats, Submissions, User
from src.ui.embeds.users import (
    connect_account_instructions_embed,
    profile_added_embed,
    synced_existing_user_embed,
    user_already_added_in_server_embed,
)
from src.utils.common import convert_to_score
from src.utils.problems import fetch_problems_solved_and_rank
from src.utils.roles import give_verified_role

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot


async def register(
    bot: "DiscordBot",
    guild: discord.Guild,
    member: discord.Member,
    send_message: Callable[..., Awaitable[discord.InteractionCallbackResponse]],
    edit_original_response: Callable[..., Awaitable[discord.InteractionMessage]],
    leetcode_id: str,
) -> None:
    """
    Registers a user to the system for the selected server.

    :param send_message: The webhook to send messages.
    :param server_id: The ID of the server to register the user into.
    :param user: The user to register.
    :param leetcode_id: The LeetCode ID of the user.
    """
    user_id = member.id
    server_id = guild.id

    matched = await linking_process(bot, send_message, leetcode_id)

    if not matched:
        embed = profile_added_embed(leetcode_id, added=False)
        await edit_original_response(embed=embed)
        return

    stats = await fetch_problems_solved_and_rank(bot, leetcode_id)

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
        timestamp=datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0),
        user_id=user_id,
        submissions=Submissions(
            easy=stats.submissions.easy,
            medium=stats.submissions.medium,
            hard=stats.submissions.hard,
            score=score,
        ),
    )

    profile_server = Profile(
        user_id=user_id,
        server_id=server_id,
        preference=Preference(
            # Use server username.
            name=member.display_name,
        ),
    )

    profile_global = Profile(
        user_id=user_id,
        server_id=GLOBAL_LEADERBOARD_ID,
        preference=Preference(
            # User account username.
            name=member.name,
            url=False,
        ),
    )

    await user.save()
    await record.create()
    await profile_server.create()
    await profile_global.create()

    await give_verified_role(guild, member)

    await edit_original_response(embed=profile_added_embed(leetcode_id))


async def login(
    guild: discord.Guild,
    member: discord.Member,
    send_message: Callable[..., Awaitable[Optional[discord.WebhookMessage]]],
) -> None:
    """
    Logs in a user to a server if user already exists.

    :param send_message: The webhook to send messages.
    :param user_id: The user to log in.
    :param server_id: The ID of the server to log the user into.
    :param user_display_name: The display name of the user.
    """
    user_id = member.id
    server_id = guild.id

    await give_verified_role(guild, member)

    db_profile = await Profile.find_one(
        Profile.user_id == user_id,
        Profile.server_id == server_id,
    )

    if db_profile:
        # User has already been added to the server.
        embed = user_already_added_in_server_embed()
        await send_message(embed=embed)
    else:
        # Add user's profile for this server.
        db_profile = Profile(
            user_id=user_id,
            server_id=server_id,
            preference=Preference(
                name=member.display_name,
            ),
        )

        await db_profile.create()

        embed = synced_existing_user_embed()
        await send_message(embed=embed)


async def linking_process(
    bot: "DiscordBot",
    send_message: Callable[..., Awaitable[discord.InteractionCallbackResponse]],
    leetcode_id: str,
) -> bool:
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

    # Check if the profile name matches the generated string
    for _ in range(duration // check_interval):
        stats = await fetch_problems_solved_and_rank(
            bot,
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
    await Profile.find_many(
        Profile.user_id == user_id, Profile.server_id == server_id
    ).delete()


async def delete_user(user_id: int) -> None:
    """
    Deletes all of user's stored information.

    :param user_id: The user's id.
    """
    await Profile.find_many(Profile.user_id == user_id).delete()
    await Record.find_many(Record.user_id == user_id).delete()
    await User.find_one(User.id == user_id).delete()
