import asyncio
import random
import string
from datetime import datetime

import discord
from beanie.odm.fields import WriteRules
from beanie.odm.operators.update.array import AddToSet, Pull
from bson import DBRef
from discord.ext import commands

from constants import GLOBAL_LEADERBOARD_ID
from database.models.preference_model import Preference
from database.models.projections import IdProjection
from database.models.record_model import Record
from database.models.server_model import Server
from database.models.user_model import Stats, Submissions, User
from embeds.users_embeds import (account_not_found_embed,
                                 account_permanently_deleted_embed,
                                 account_removed_embed,
                                 connect_account_instructions_embed,
                                 profile_added_embed,
                                 synced_existing_user_embed,
                                 user_already_added_in_server_embed)
from middleware import (defer_interaction, ensure_server_document,
                        track_analytics)
from middleware.database_middleware import update_user_preferences_prompt
from utils.questions_utils import get_problems_solved_and_rank
from utils.roles_utils import give_verified_role
from views.register_modal import RegisterModal


class UsersCog(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @discord.app_commands.command(
        name="add", description="Connect your LeetCode account to this server"
    )
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @track_analytics
    async def add(self, interaction: discord.Interaction) -> None:
        """
        Adds a user to the server in the system.

        :param interaction: The Discord interaction.
        """
        server_id = interaction.guild.id
        user_id = interaction.user.id

        user = await User.get(User.id == user_id)

        if user:
            self._login(interaction.followup.send, user, server_id)
        else:
            register_modal = RegisterModal()
            await interaction.response.send_modal(register_modal)
            self._register(interaction, interaction.followup.send, server_id,
                           user, register_modal.answer)

        await update_user_preferences_prompt(interaction)

    @discord.app_commands.command(
        name="update", description="Update your profile on this server's leaderboards"
    )
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @track_analytics
    async def update(self, interaction: discord.Interaction) -> None:
        """
        Initiates the preference updater prompt.

        :param interaction: The Discord interaction.
        """
        user_id = interaction.user.id

        user = await User.find_one(User.id == user_id)

        if user:
            await update_user_preferences_prompt(interaction)
            return

        embed = account_not_found_embed()
        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(
        name="remove", description="Remove your profile from this server's leaderboard"
    )
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @track_analytics
    async def remove(
        self, interaction: discord.Interaction, permanently_delete: bool = False
    ) -> None:
        """
        Removes (or permanently deletes) a user from the system for the selected server.

        :param interaction: The Discord interaction.
        """
        server_id = interaction.guild.id
        user_id = interaction.user.id

        user_exists = await User.find_one(User.id == user_id).project(IdProjection)

        if user_exists:
            # delete the user
            if permanently_delete:
                await Server.find_one(Server.id == server_id).update(
                    Pull({Server.users: {"$id": user_id}})
                )

                await Server.find_one(Server.id == GLOBAL_LEADERBOARD_ID).update(
                    Pull({Server.users: {"$id": user_id}})
                )
                await User.find_one(User.id == user_id).delete()
                embed = account_permanently_deleted_embed()
                await interaction.followup.send(embed=embed)
                return

            # unlink user from server(interaction, user_id)
            # TODO: this is getting the entire user.
            display_information = await User.find_one(
                User.id == user_id, User.display_information.server_id == server_id
            )

            if display_information:
                await User.find_one(User.id == user_id).update(
                    Pull({User.display_information: {"server_id": server_id}})
                )

                await Server.find_one(Server.id == server_id).update(
                    Pull({Server.users: {"$id": user_id}})
                )

                embed = account_removed_embed()
                await interaction.followup.send(embed=embed)
                return

        embed = account_not_found_embed()
        await interaction.followup.send(embed=embed)

    async def _login(
        self,
        send_message: discord.Webhook,
        user: discord.User,
        server_id: int,
        user_display_name: str,
    ):
        """
        Logs in a user to a server if user already exists.

        :param send_message: The webhook to send messages.
        :param user: The user to log in.
        :param server_id: The ID of the server to log the user into.
        :param user_display_name: The display name of the user.
        """
        await give_verified_role(user, server_id)

        preference = await Preference.find_one(
            Preference.user == user, Preference.server == DBRef(
                "servers", server_id)
        )

        if preference:
            # User has already been added to the server.
            embed = user_already_added_in_server_embed()
            await send_message(embed=embed)
        else:
            # Add user's preferences for this server.
            preference = Preference(
                user=user,
                server=DBRef("servers", server_id),
                name=user_display_name,
            )

            await Server.find_one(Server.id == server_id).update(
                AddToSet({Server.users: DBRef("users", user.id)})
            )

            embed = synced_existing_user_embed()
            await send_message(embed=embed)

    async def _register(
        self,
        interaction: discord.Interaction,
        send_message: discord.Webhook,
        server_id: int,
        user: discord.User,
        leetcode_id: str
    ):
        """
        Registers a user to the system for the selected server.

        :param interaction: The Discord interaction.
        :param send_message: The webhook to send messages.
        :param server_id: The ID of the server to register the user into.
        :param user: The user to register.
        :param leetcode_id: The LeetCode ID of the user.
        """

        matched = await self._linking_process(send_message, leetcode_id)

        if not matched:
            embed = profile_added_embed(leetcode_id, added=False)
            await interaction.edit_original_response(embed=embed)
            return

        stats = await get_problems_solved_and_rank(self.client.session, leetcode_id)
        # ?! await clientSession.close()

        if not stats:
            return

        user = User(
            id=user.id,
            leetcode_id=leetcode_id,
            stats=Stats(submissions=Submissions(
                easy=stats.submissions.easy,
                medium=stats.submissions.medium,
                hard=stats.submissions.hard
            ))
        )

        record = Record(
            timestamp=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            user=user,
            submissions=Submissions(
                easy=stats.submissions.easy,
                medium=stats.submissions.medium,
                hard=stats.submissions.hard
            ))

        preference_server = Preference(
            user=user,
            server=DBRef("servers", server_id),
            # Use server username.
            name=interaction.user.display_name,
        )

        preference_global = Preference(
            user=user,
            server=DBRef("servers", GLOBAL_LEADERBOARD_ID),
            # User account username.
            name=interaction.user.name,
        )

        await Server.find_one(Server.id == server_id).update(
            AddToSet({Server.users: user})
        )
        server = await Server.get(server_id)
        # ! Check how to do this properly
        # ! Maybe issues with writeruling the user the using the user object in record
        # ! preference_server and preference_global
        # Link rule to create a new document for the new user link.
        await server.save(link_rule=WriteRules.WRITE)
        await record.save()
        await preference_server.save()
        await preference_global.save()

        # Add to the global leaderboard.
        await Server.find_one(Server.id == GLOBAL_LEADERBOARD_ID).update(
            AddToSet({Server.users: user})
        )

        await give_verified_role(interaction.user, interaction.guild.id)

        await interaction.edit_original_response(embed=profile_added_embed(leetcode_id))

    async def _linking_process(self,
                               send_message: discord.Webhook,
                               leetcode_id: str) -> None:
        """
        Initiates the account linking process.

        :param send_message: The webhook to send messages.
        :param leetcode_id: The LeetCode ID of the user.
        """

        # Generate a random string for account linking
        generated_string = "".join(random.choices(string.ascii_letters, k=8))

        await send_message(embed=connect_account_instructions_embed(
            generated_string, leetcode_id))

        profile_name = None

        # TODO: Use self.config
        duration = 60  # seconds
        check_interval = 5  # seconds

        # Check if the profile name matches the generated string
        for _ in range(duration // check_interval):
            stats = await get_problems_solved_and_rank(
                # TODO: add clientsession
                self.clientsession,
                leetcode_id,
            )

            if not stats:
                break

            profile_name = stats.real_name

            if profile_name == generated_string:
                break

            await asyncio.sleep(check_interval)

        return profile_name == generated_string


async def setup(client: commands.Bot) -> None:
    await client.add_cog(UsersCog(client))
