import asyncio
import random
import string

import discord
from discord.ext import commands

from bot_globals import calculate_scores, logger
from embeds.users_embeds import (connect_account_instructions, profile_added,
                                 synced_existing_user, user_already_added_in_server)
from models.projections import IdProjection
from models.server_model import Server
from models.user_model import DisplayInformation, Submissions, User
from utils.io_handling import read_file, write_file
from utils.middleware import ensure_server_document
from utils.questions import get_problems_solved_and_rank
from beanie.odm.operators.update.array import Push


class Users(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(
        name="add",
        description="Adds a user to the leaderboard. Answer with 'yes' to link your LeetCode profile to the leaderboard."
    )
    @ensure_server_document
    async def add(self, interaction: discord.Interaction, leetcode_username: str, include_hyperlink: str = "yes", displayed_name: str | None = None) -> None:
        logger.info(
            'file: cogs/users.py ~ add ~ run ~ leetcode_username: %s, include_hyperlink: %s, displayed_name: %s', leetcode_username, include_hyperlink, displayed_name)

        if not interaction.guild:
            return

        hyperlink_bool = include_hyperlink.lower() in ("yes", "true", "t", "1")
        if displayed_name is None:
            displayed_name = interaction.user.name

        server_id = interaction.guild.id
        user_id = interaction.user.id

        server = await Server.get(server_id)

        if not server:
            await interaction.response.defer()

        display_information = DisplayInformation(
            server_id=server_id, name=displayed_name, hyperlink=hyperlink_bool)

        user_exists = await User.find_one(User.id == user_id).project(IdProjection)

        if user_exists:
            display_information_exists = await User.find_one(User.id == user_id, User.display_information.server_id == server_id)

            if display_information_exists:
                logger.info(
                    'file: cogs/users.py ~ add ~ user has already been added in the server ~ leetcode_username: %s', leetcode_username)

                # User has already been added in the server
                embed = user_already_added_in_server()
                await interaction.response.send_message(embed=embed, ephemeral=True)

            else:
                logger.info(
                    'file: cogs/users.py ~ add ~ add user\' display information for this server ~ leetcode_username: %s', leetcode_username)

                # Add user's display information for this server
                await User.find_one(User.id == user_id).update(Push({User.display_information: display_information}))

                embed = synced_existing_user()
                await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            # Generate a random string for account linking
            generated_string = ''.join(
                random.choices(string.ascii_letters, k=8))

            embed = connect_account_instructions(
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

                user = User(id=user_id, leetcode_username=leetcode_username,
                            rank=rank, display_information=[display_information], submissions=submissions)

                await user.create()

                logger.info(
                    'file: cogs/users.py ~ add ~ user has been added successfully ~ leetcode_username: %s', leetcode_username)

                embed = profile_added(leetcode_username)
                await interaction.edit_original_response(embed=embed)
            else:
                logger.info(
                    'file: cogs/users.py ~ add ~ user has not been added ~ leetcode_username: %s', leetcode_username)

                embed = profile_added(leetcode_username, added=False)
                await interaction.edit_original_response(embed=embed)

    @discord.app_commands.command(name="delete", description="Delete your profile from the leaderboard.")
    async def delete(self, interaction: discord.Interaction) -> None:
        """
        Command to delete the user's profile from the leaderboard.

        Args:
            interaction (discord.Interaction): The interaction object representing the user command.

        Returns:
            None
        """

        logger.info(
            'file: cogs/users.py ~ delete ~ run')

        if not interaction.guild:
            await interaction.response.defer()
            return

        discord_user = interaction.user
        server_id = interaction.guild.id

        data = await read_file(f"data/{server_id}_leetcode_stats.json")

        if data is not None:
            logger.info(
                'file: cogs/users.py ~ delete ~ discord_user.id: %s', discord_user.id)

            # Iterate through the data points
            if str(discord_user.id) in data["users"]:
                leetcode_username = data["users"][str(
                    discord_user.id)]["leetcode_username"]
                # Found the data point with matching discord_user.id
                # Delete the data point
                del data["users"][str(discord_user.id)]
                # Save the updated data
                await write_file(f"data/{server_id}_leetcode_stats.json", data)

                # Send a message to the user
                embed = discord.Embed(title="Profile Deleted",
                                      color=discord.Color.green())
                embed.add_field(name="Username:",
                                value=f"{leetcode_username}", inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)

            else:
                # No matching data point found
                embed = discord.Embed(title="Profile Not Found",
                                      color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            logger.info(
                "file: cogs/users.py ~ delete ~ file not found: data/%s_leetcode_stats.json", interaction.guild.id)

            # File does not exist
            embed = discord.Embed(title="Profile Not Found",
                                  color=discord.Color.red())
            # This server does not have a leaderboard yet
            embed.add_field(name="Error:",
                            value="This server does not have a leaderboard yet.",
                            inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(Users(client))
