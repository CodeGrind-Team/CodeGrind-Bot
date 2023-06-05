import asyncio
import json
import os
import random
import string

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands


from bot_globals import logger


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

        for _ in range(12):
            url = f"https://leetcode.com/{username}"
            logger.debug(url)
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            rank_element = soup.find(
                "span", class_="ttext-label-1 dark:text-dark-label-1 font-medium")
            rank = rank_element.text.strip() if rank_element else "N/A"

            profile_name_element = soup.find(
                "div",
                class_="text-label-1 dark:text-dark-label-1 break-all text-base font-semibold")
            profile_name = profile_name_element.text.strip(
            ) if profile_name_element else ""

            if profile_name == generated_string:
                break

            await asyncio.sleep(5)

        if profile_name == generated_string:
            url = f"https://leetcode.com/{username}"
            logger.debug(url)
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            rank_element = soup.find(
                "span", class_="ttext-label-1 dark:text-dark-label-1 font-medium")
            rank = rank_element.text.strip() if rank_element else "N/A"

            profile_name_element = soup.find(
                "div",
                class_="text-label-1 dark:text-dark-label-1 break-all text-base font-semibold")
            profile_name = profile_name_element.text.strip(
            ) if profile_name_element else ""

            span_elements = soup.find_all(
                "span",
                class_="mr-[5px] text-base font-medium leading-[20px] text-label-1 dark:text-dark-label-1"
            )

            numbers = [span_element.text for span_element in span_elements]

            easy_completed = int(numbers[0])
            medium_completed = int(numbers[1])
            hard_completed = int(numbers[2])

            total_questions_done = easy_completed + medium_completed + hard_completed
            total_score = easy_completed * 1 + medium_completed * 3 + hard_completed * 5
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
