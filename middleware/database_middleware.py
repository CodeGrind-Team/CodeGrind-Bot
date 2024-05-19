from datetime import UTC, datetime
from functools import wraps
from typing import Callable

import discord

from database.models.preference_model import Preference
from database.models.server_model import Server
from embeds.users_embeds import preferences_update_prompt_embeds
from views.preferences_views import UserPreferencesPrompt


def ensure_server_document(func: Callable) -> Callable:
    """
    Ensures that a server document exists in the database before executing the given
    function.

    If the server document does not exist, it creates a new one. This is used
    as a decorator for functions interacting with server-specific data.

    :param func: The function to wrap.

    :return: The wrapped function that ensures the server document exists.
    """

    @wraps(func)
    async def wrapper(
        self, interaction: discord.Interaction, *args, **kwargs
    ) -> Callable | None:
        server_id = interaction.guild.id
        server = await Server.get(server_id)

        if not server:
            server = Server(id=server_id)
            await server.create()

        return await func(self, interaction, *args, **kwargs)

    return wrapper


async def update_user_preferences_prompt(
    interaction: discord.Interaction, reminder: bool = False
) -> None:
    """
    Sends a prompt to update user preferences if certain conditions are met.

    This function checks if a user's preference needs updating, considering whether
    it's a reminder and the last time the preference was updated. If the conditions are
    met, it sends an interactive prompt to the user.

    :param interaction: The Discord interaction that triggered the function.
    :param reminder: Indicates if this is a reminder prompt. If `True`, the prompt is
    sent only if the preference has not been updated in over 30 days.

    :return: None.
    """

    preference = await Preference.find_one(
        Preference.user_id == interaction.user.id,
        Preference.server_id == interaction.guild.id,
    )

    if not preference:
        return

    if (
        reminder
        and preference.last_updated
        and (datetime.now(UTC) - preference.last_updated.astimezone(UTC)).days <= 30
    ):
        return

    pages, end_embed = preferences_update_prompt_embeds()

    view = UserPreferencesPrompt(pages, end_embed)
    await interaction.followup.send(embed=pages[0].embed, view=view, ephemeral=True)
    await view.wait()

    preference.last_updated = datetime.now(UTC)
    await preference.save_changes()
