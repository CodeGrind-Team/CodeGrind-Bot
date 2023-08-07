import asyncio
import random
import string

import discord
from beanie.odm.fields import WriteRules
from beanie.odm.operators.update.array import AddToSet, Pull
from beanie.odm.operators.update.general import Set
from discord.ext import commands

from bot_globals import calculate_scores, logger
from embeds.misc_embeds import error_embed
from embeds.users_embeds import (account_not_found_embed,
                                 account_removed_embed,
                                 connect_account_instructions_embed,
                                 profile_added_embed,
                                 profile_details_updated_embed,
                                 synced_existing_user_embed,
                                 user_already_added_in_server_embed)
from models.projections import IdProjection
from models.server_model import Server
from models.user_model import DisplayInformation, Scores, Submissions, User
from utils.middleware import ensure_server_document, track_analytics
from utils.questions import get_problems_solved_and_rank


class Users(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(
        name="add",
        description="Connect your LeetCode account to this server"
    )
    @ensure_server_document
    @track_analytics
    async def add(self, interaction: discord.Interaction, leetcode_username: str, include_url: bool = True) -> None:
        logger.info(
            'file: cogs/users.py ~ add ~ run ~ leetcode_username: %s, include_url: %s', leetcode_username, include_url)

        if not interaction.guild:
            return

        server_id = interaction.guild.id
        user_id = interaction.user.id

        server_exists = await Server.find_one(Server.id == server_id).project(IdProjection)

        if not server_exists:
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        display_information = DisplayInformation(
            server_id=server_id, name=interaction.user.display_name, url=include_url)

        user_exists = await User.find_one(User.id == user_id).project(IdProjection)

        if user_exists:
            display_information_exists = await User.find_one(User.id == user_id, User.display_information.server_id == server_id)

            if display_information_exists:
                logger.info(
                    'file: cogs/users.py ~ add ~ user has already been added in the server ~ leetcode_username: %s', leetcode_username)

                # User has already been added in the server
                embed = user_already_added_in_server_embed()
                await interaction.response.send_message(embed=embed, ephemeral=True)

            else:
                logger.info(
                    'file: cogs/users.py ~ add ~ add user\' display information for this server ~ leetcode_username: %s', leetcode_username)

                # Add user's display information for this server
                await User.find_one(User.id == user_id).update(AddToSet({User.display_information: display_information}))

                await Server.find_one(Server.id == server_id).update(AddToSet({Server.users: user_id}))
                # Have to fetch and save document in order to convert user_id to a reference
                # TODO: ask on beanie repo for the correct method of doing this
                server = await Server.get(server_id)
                await server.save()

                embed = synced_existing_user_embed()
                await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            # Generate a random string for account linking
            generated_string = ''.join(
                random.choices(string.ascii_letters, k=8))

            embed = connect_account_instructions_embed(
                generated_string, leetcode_username)
            await interaction.response.send_message(embed=embed, ephemeral=True)

            profile_name = None
            check_interval = 5  # seconds

            # Check if the profile name matches the generated string
            for _ in range(60 // check_interval):
                stats = get_problems_solved_and_rank(leetcode_username)

                if not stats:
                    break

                rank = stats["profile"]["realName"]
                profile_name = stats["profile"]["realName"]

                if profile_name == generated_string:
                    break

                await asyncio.sleep(check_interval)

            if profile_name == generated_string:
                stats = get_problems_solved_and_rank(leetcode_username)

                if not stats:
                    return

                rank = stats["profile"]["ranking"]
                easy = stats["submitStatsGlobal"]["acSubmissionNum"]["Easy"]
                medium = stats["submitStatsGlobal"]["acSubmissionNum"]["Medium"]
                hard = stats["submitStatsGlobal"]["acSubmissionNum"]["Hard"]

                total_score = calculate_scores(easy, medium, hard)

                submissions = Submissions(
                    easy=easy, medium=medium, hard=hard, total_score=total_score)

                scores = Scores(start_of_week_total_score=total_score,
                                start_of_day_total_score=total_score)

                user = User(id=user_id, leetcode_username=leetcode_username, rank=rank, display_information=[
                            display_information], submissions=submissions, scores=scores)

                await Server.find_one(Server.id == server_id).update(AddToSet({Server.users: user}))
                server = await Server.get(server_id)
                # link rule to create a new document for the new link
                await server.save(link_rule=WriteRules.WRITE)

                logger.info(
                    'file: cogs/users.py ~ add ~ user has been added successfully ~ leetcode_username: %s', leetcode_username)

                embed = profile_added_embed(leetcode_username)
                await interaction.edit_original_response(embed=embed)
            else:
                logger.info(
                    'file: cogs/users.py ~ add ~ user has not been added ~ leetcode_username: %s', leetcode_username)

                embed = profile_added_embed(leetcode_username, added=False)
                await interaction.edit_original_response(embed=embed)

    @discord.app_commands.command(name="update", description="Update your profile on this server's leaderboards")
    @ensure_server_document
    @track_analytics
    async def update(self, interaction: discord.Interaction, include_url: bool = True) -> None:
        logger.info(
            'file: cogs/users.py ~ update ~ run ~ include_url: %s', include_url)

        if not interaction.guild:
            return

        server_id = interaction.guild.id
        user_id = interaction.user.id

        server_exists = await Server.find_one(Server.id == server_id).project(IdProjection)

        if not server_exists:
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        user = await User.find_one(User.id == user_id)

        if user:
            await User.find_one(User.id == user.id, User.display_information.server_id == server_id).update(Set({"display_information.$.url": include_url}))
            embed = profile_details_updated_embed()

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        logger.info(
            'file: cogs/users.py ~ remove ~ profile not found in this server ~ user_id: %s', user_id)

        embed = account_not_found_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.command(name="remove", description="Remove your profile from this server's leaderboard")
    @ensure_server_document
    @track_analytics
    async def remove(self, interaction: discord.Interaction) -> None:
        logger.info(
            'file: cogs/users.py ~ remove ~ run')

        if not interaction.guild:
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        server_id = interaction.guild.id
        user_id = interaction.user.id

        server_exists = await Server.find_one(Server.id == server_id).project(IdProjection)

        if not server_exists:
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        logger.info(
            'file: cogs/users.py ~ remove ~ user_id: %s', user_id)

        user_exists = await User.find_one(User.id == user_id).project(IdProjection)

        if user_exists:
            display_information = await User.find_one(
                User.id == user_id, User.display_information.server_id == server_id)

            if display_information:
                await User.find_one(
                    User.id == user_id).update(Pull({User.display_information: {"server_id": server_id}}))

                await Server.find_one(Server.id == server_id).update(Pull({Server.users: {"$id": user_id}}))

                logger.info(
                    'file: cogs/users.py ~ remove ~ profile removed - references removed from User and Server documents ~ user_id: %s', user_id)

                embed = account_removed_embed()
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        logger.info(
            'file: cogs/users.py ~ remove ~ profile not found in this server ~ user_id: %s', user_id)

        embed = account_not_found_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(Users(client))
