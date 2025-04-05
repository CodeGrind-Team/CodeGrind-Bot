from functools import wraps
from typing import Callable

import discord

from src.database.models import Server
from src.ui.embeds.common import error_embed
from src.utils.preferences import update_user_preferences_prompt


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


def defer_interaction(
    *, ephemeral_default: bool = False, user_preferences_prompt: bool = False
) -> Callable:
    """
    Decorator that defers the Discord interaction response and optionally sends a user
    preferences prompt.

    This decorator is used to delay sending the response to an interaction, allowing
    for further processing or actions before providing a final response. It also checks
    if the interaction is valid (in a guild and by a member) and can send a user
    preferences prompt if specified.

    :param ephemeral_default: Whether the deferred response should be ephemeral by
    default.
    :param user_preferences_prompt: Whether to trigger a user preferences prompt upon
    completion.

    :return: A decorator that defers interaction responses and checks for user prompts.
    """

    def ephemeral_response(func: Callable) -> Callable:
        """
        Wrapper function that defers the response and handles error checking.

        This wrapper is applied to a function that handles a Discord interaction. It
        ensures the response is deferred (with optional ephemerality) and performs
        basic validation checks, sending an error message if the interaction is not
        in a valid state. Additionally, it may prompt the user to update their
        preferences if configured.

        :param func: The function to be wrapped.

        :return: The wrapped function that defers the interaction response.
        """

        @wraps(func)
        async def wrapper(
            self, interaction: discord.Interaction, *args, **kwargs
        ) -> Callable | None:
            display_publicly: bool | None = kwargs.get("display_publicly", None)

            # Determine if the response should be ephemeral
            ephemeral = (
                not display_publicly
                if display_publicly is not None
                else ephemeral_default
            )

            # Defer the interaction response
            await interaction.response.defer(ephemeral=ephemeral)

            # Basic validation to ensure the interaction is within a guild, channel,
            # and by a member
            if (
                not interaction.guild
                or not isinstance(
                    interaction.channel, (discord.TextChannel, discord.Thread)
                )
                or not isinstance(interaction.user, discord.Member)
            ):
                embed = error_embed()
                await interaction.followup.send(embed=embed)
                return

            # Execute the wrapped function
            ret = await func(self, interaction, *args, **kwargs)

            if user_preferences_prompt:
                await update_user_preferences_prompt(interaction, reminder=True)

            return ret

        return wrapper

    return ephemeral_response
