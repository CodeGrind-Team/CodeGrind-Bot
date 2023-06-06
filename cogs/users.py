import asyncio
import json
import os
import random
import string

import discord
from discord.ext import commands
from cogs.stats import get_problems_solved_and_rank

from bot_globals import DIFFICULTY_SCORE, logger


class Users(commands.Cog):
    def __init__(self, client):
        self.client = client

    @discord.app_commands.command(
        name="add",
        description="Adds a user to the leaderboard. Answer with 'yes' to link your LeetCode profile to the leaderboard."
    )
    async def add(self, interaction: discord.Interaction, username: str, link: str = "yes"):
        if os.path.exists(f"{interaction.guild.id}_leetcode_stats.json"):
            with open(f"{interaction.guild.id}_leetcode_stats.json", "r", encoding="UTF-8") as file:
                existing_data = json.load(file)
            if username in existing_data:
                embed = discord.Embed(
                    title="Error!",
                    description="You have already added your LeetCode account!",
                    color=discord.Color.red())
                embed.add_field(name="Remove your LeetCode username",
                                value="Use the `/remove` command to remove your LeetCode username.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        else:
            existing_data = {}

        generated_string = ''.join(random.choices(string.ascii_letters, k=8))
        embed = discord.Embed(title="Profile Update Required",
                              color=discord.Color.red())
        embed.add_field(name="Generated Sequence",
                        value=f"{generated_string}",
                        inline=False)
        embed.add_field(name="Username", value=f"{username}", inline=False)
        embed.add_field(
            name="Instructions",
            value="Please change your LeetCode Profile Name to the generated sequence.",
            inline=False)
        embed.add_field(
            name="Profile Name Change",
            value="You can do this by clicking [here](https://leetcode.com/profile/) and changing your Name.",
            inline=False)
        embed.add_field(
            name="Time Limit",
            value="You have 60 seconds to change your name, otherwise, you will have to restart the process.",
            inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

        profile_name = None
        for _ in range(12):
            stats = get_problems_solved_and_rank(username)

            if stats is None:
                break

            rank = stats["profile"]["realName"]

            profile_name = stats["profile"]["realName"]

            if profile_name == generated_string:
                break

            await asyncio.sleep(5)

        if profile_name == generated_string:
            stats = get_problems_solved_and_rank(username)

            rank = stats["profile"]["ranking"]
            easy_completed = stats["submitStatsGlobal"]["acSubmissionNum"]["Easy"]
            medium_completed = stats["submitStatsGlobal"]["acSubmissionNum"]["Medium"]
            hard_completed = stats["submitStatsGlobal"]["acSubmissionNum"]["Hard"]
            total_questions_done = stats["submitStatsGlobal"]["acSubmissionNum"]["All"]

            total_score = easy_completed * DIFFICULTY_SCORE['easy'] + medium_completed * \
                DIFFICULTY_SCORE['medium'] + \
                hard_completed * DIFFICULTY_SCORE['hard']

            discord_username = interaction.user.name

            existing_data[username] = {
                "rank": rank,
                "easy": easy_completed,
                "medium": medium_completed,
                "hard": hard_completed,
                "total_questions_done": total_questions_done,
                "total_score": total_score,
                "week_score": 0,
                "discord_username": discord_username,
                "link_yes_no": link,
                "discord_id": interaction.user.id,
                "history": {},
                "weeklies_ranking": {}
            }

            with open(f"{interaction.guild.id}_leetcode_stats.json", "w", encoding="UTF-8") as file:
                json.dump(existing_data, file)
            embed = discord.Embed(title="Profile Added",
                                  color=discord.Color.green())
            embed.add_field(name="Username:",
                            value=f"{username}", inline=False)
            await interaction.edit_original_response(embed=embed)

            return
        else:
            embed = discord.Embed(title="Profile Not Added",
                                  color=discord.Color.red())
            embed.add_field(name="Username:",
                            value=f"{username}", inline=False)
            await interaction.edit_original_response(embed=embed)
            return

    @discord.app_commands.command(name="delete", description="Delete your profile from the leaderboard.")
    async def delete(self, interaction: discord.Interaction):
        # Check if the file exists
        if os.path.exists(f"{interaction.guild.id}_leetcode_stats.json"):
            logger.debug("File exists")
            # Open the file
            with open(f"{interaction.guild.id}_leetcode_stats.json", "r", encoding="UTF-8") as file:
                data = json.load(file)

                # Iterate through the data points
                for username, stats in data.items():
                    if stats["discord_id"] == interaction.user.id:
                        # Found the data point with matching discord_id
                        # Delete the data point
                        del data[username]
                        # Save the updated data
                        with open(f"{interaction.guild.id}_leetcode_stats.json", "w", encoding="UTF-8") as file:
                            json.dump(data, file)
                        # Send a message to the user
                        embed = discord.Embed(title="Profile Deleted",
                                              color=discord.Color.green())
                        embed.add_field(name="Username:",
                                        value=f"{username}", inline=False)
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        break
                else:
                    # No matching data point found
                    embed = discord.Embed(title="Profile Not Found",
                                          color=discord.Color.red())
                    await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            # File does not exist
            embed = discord.Embed(title="Profile Not Found",
                                  color=discord.Color.red())
            # This server does not have a leaderboard yet
            embed.add_field(name="Error:",
                            value="This server does not have a leaderboard yet.",
                            inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client):
    await client.add_cog(Users(client))
