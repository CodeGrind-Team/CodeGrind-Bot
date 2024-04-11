import asyncio
import random
import string

import aiohttp
import discord
from beanie.odm.fields import WriteRules
from beanie.odm.operators.update.array import AddToSet, Pull
from bson import DBRef
from discord.ext import commands

from database.models.projections import IdProjection
from database.models.server_model import Server
from database.models.preference_model import Preference
from database.models.user_model import Stats, User
from database.models.record_model import Record
from embeds.users_embeds import (
    account_not_found_embed,
    account_permanently_deleted_embed,
    account_removed_embed,
    connect_account_instructions_embed,
    profile_added_embed,
    synced_existing_user_embed,
    user_already_added_in_server_embed,
)
from middleware import defer_interaction, ensure_server_document, track_analytics
from middleware.database_middleware import update_user_preferences_prompt
from utils.common_utils import convert_to_score
from utils.questions_utils import get_problems_solved_and_rank
from utils.roles_utils import give_verified_role


class UsersCog(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @discord.app_commands.command(
        name="add", description="Connect your LeetCode account to this server"
    )
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @track_analytics
    async def add(self, interaction: discord.Interaction, leetcode_id: str) -> None:
        server_id = interaction.guild.id
        user_id = interaction.user.id

        user = await User.get(User.id == user_id)

        if user:
            self._login(interaction.followup.send, user, server_id)
        else:
            self._register(interaction.followup.send, user, leetcode_id)

        await update_user_preferences_prompt(interaction)

    @discord.app_commands.command(
        name="update", description="Update your profile on this server's leaderboards"
    )
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @track_analytics
    async def update(self, interaction: discord.Interaction) -> None:
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
        server_id = interaction.guild.id
        user_id = interaction.user.id

        user_exists = await User.find_one(User.id == user_id).project(IdProjection)

        if user_exists:
            # delete the user
            if permanently_delete:
                await Server.find_one(Server.id == server_id).update(
                    Pull({Server.users: {"$id": user_id}})
                )
                # Global leaderboard
                # TODO: create global_leaderboard_id enum
                await Server.find_one(Server.id == 0).update(
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
        await give_verified_role(user, server_id)

        preference = await Preference.find_one(
            Preference.user == user, Preference.server == DBRef("servers", server_id)
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
        self, send_message: discord.Webhook, user: discord.User, leetcode_id: str
    ):
        # Generate a random string for account linking
        generated_string = "".join(random.choices(string.ascii_letters, k=8))

        embed = connect_account_instructions_embed(generated_string, leetcode_id)
        await send_message(embed=embed)

        matched = await self._linking_process(leetcode_id)

        if matched:
            stats = await get_problems_solved_and_rank(self.client.session, leetcode_id)
            # ?! await clientSession.close()

            if not stats:
                return

            # TODO: dataclass
            rank = stats["profile"]["ranking"]
            easy = stats["submitStatsGlobal"]["acSubmissionNum"]["Easy"]
            medium = stats["submitStatsGlobal"]["acSubmissionNum"]["Medium"]
            hard = stats["submitStatsGlobal"]["acSubmissionNum"]["Hard"]

            total_score = convert_to_score(easy, medium, hard)

            user = User(
                id=user.id,
                leetcode_id=leetcode_id,
                rank=rank,
                stats=Stats(easy=easy, medium=medium, hard=hard),
            )

            record = Record()

            # display_information=[
            #         display_information,
            #         DisplayInformation(
            #             server_id=0,
            #             name=interaction.user.name,
            #         ),
            #     ],

            await Server.find_one(Server.id == server_id).update(
                AddToSet({Server.users: user})
            )
            server = await Server.get(server_id)
            # link rule to create a new document for the new link
            await server.save(link_rule=WriteRules.WRITE)

            # Add to the global leaderboard.
            await Server.find_one(Server.id == 0).update(
                AddToSet({Server.users: DBRef("users", user_id)})
            )

            await give_verified_role(interaction.user, interaction.guild.id)

            self.client.logger.info(
                "file: cogs/users.py ~ add ~ user has been added successfully \
                    ~ leetcode_username: %s",
                leetcode_username,
            )

            embed = profile_added_embed(leetcode_username)
            await interaction.edit_original_response(embed=embed)
        else:
            self.client.logger.info(
                "file: cogs/users.py ~ add ~ user has not been added \
                    ~ leetcode_username: %s",
                leetcode_username,
            )

            embed = profile_added_embed(leetcode_username, added=False)
            await interaction.edit_original_response(embed=embed)
            return

    async def _linking_process(self, generated_string: int, leetcode_id: str) -> None:
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

            profile_name = stats["profile"]["realName"]

            if profile_name == generated_string:
                break

            await asyncio.sleep(check_interval)

        return profile_name == generated_string


async def setup(client: commands.Bot) -> None:
    await client.add_cog(UsersCog(client))
