import json
import os
from datetime import datetime, timedelta

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

from bot_globals import DIFFICULTY_SCORE, logger


def update_stats(client, now: datetime, weekly_reset: bool = False):
    # retrieve every server the bot is in
    server_ids = [guild.id for guild in client.guilds]
    logger.debug('Server IDs: %s', server_ids)

    # for each server, retrieve the leaderboard
    for server_id in server_ids:
        logger.debug(server_id)
        # retrieve the keys from the json file
        if os.path.exists(f"{server_id}_leetcode_stats.json"):
            with open(f'{server_id}_leetcode_stats.json', 'r', encoding="UTF-8") as f:
                data = json.load(f)

            sorted_data = sorted(data.items(),
                                 key=lambda x: x[1]["week_score"],
                                 reverse=True)

            for place, (username, _) in enumerate(sorted_data):
                url = f"https://leetcode.com/{username}/"
                logger.debug(url)
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")

                rank_element = soup.find(
                    "span", class_="ttext-label-1 dark:text-dark-label-1 font-medium")
                rank = rank_element.text.strip() if rank_element else "N/A"

                span_elements = soup.find_all(
                    "span",
                    class_="mr-[5px] text-base font-medium leading-[20px] text-label-1 dark:text-dark-label-1"
                )

                numbers = [
                    span_element.text for span_element in span_elements]

                easy_completed = int(numbers[0])
                medium_completed = int(numbers[1])
                hard_completed = int(numbers[2])

                total_questions_done = easy_completed + medium_completed + hard_completed
                total_score = easy_completed * \
                    DIFFICULTY_SCORE["easy"] + medium_completed * \
                    DIFFICULTY_SCORE["medium"] + \
                    hard_completed * DIFFICULTY_SCORE["hard"]

                # Due to this field is added after some users have already been added,
                # it needs to be created and set to an empty dictionary
                # TODO: replace this with a function to automatically fill in missing fields
                if "history" not in data[username]:
                    data[username]["history"] = {}

                if "week_score" not in data[username]:
                    data[username]["week_score"] = 0

                if "weeklies_ranking" not in data[username]:
                    data[username]["weeklies_ranking"] = {}

                if weekly_reset:
                    data[username]["weeklies_ranking"][str(now.strftime(
                        "%d/%m/%Y"))] = place + 1

                start_of_week = now - timedelta(days=now.weekday() % 7)

                while start_of_week <= now:
                    start_of_week_date = start_of_week.strftime("%d/%m/%Y")
                    if str(start_of_week_date) not in data[username]["history"]:
                        start_of_week += timedelta(days=1)
                        continue

                    start_of_week_easy_completed = data[username]["history"][str(
                        start_of_week_date)]['easy']
                    start_of_week_medium_completed = data[username]["history"][str(
                        start_of_week_date)]['medium']
                    start_of_week_hard_completed = data[username]["history"][str(
                        start_of_week_date)]['hard']

                    start_of_week_score = start_of_week_easy_completed * \
                        DIFFICULTY_SCORE["easy"] + start_of_week_medium_completed * \
                        DIFFICULTY_SCORE["medium"] + \
                        start_of_week_hard_completed * \
                        DIFFICULTY_SCORE["hard"]
                    week_score = total_score - start_of_week_score

                    data[username]["week_score"] = week_score
                    break

                data[username]["rank"] = rank
                data[username]["easy"] = easy_completed
                data[username]["medium"] = medium_completed
                data[username]["hard"] = hard_completed
                data[username]["total_questions_done"] = total_questions_done
                data[username]["total_score"] = total_score

                if str(now.strftime("%d/%m/%Y")) not in data[username]["history"]:
                    data[username]["history"][str(now.strftime("%d/%m/%Y"))] = {
                        "easy": easy_completed, "medium": medium_completed, "hard": hard_completed}

                logger.debug(data[username])
                # update the json file
                with open(f"{server_id}_leetcode_stats.json", "w", encoding="UTF-8") as f:
                    json.dump(data, f, indent=4)


class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client

    @discord.app_commands.command(name="stats", description="Prints the stats of a user")
    async def stats(self, interaction: discord.Interaction, username: str = None):
        if username is None:
            with open(f"{interaction.guild.id}_leetcode_stats.json", "r", encoding="UTF-8") as file:
                data = json.load(file)

            for user, user_data in data.items():
                if user_data["discord_id"] == interaction.user.id:
                    username = user
                    break

            if username is None:
                embed = discord.Embed(
                    title="Error!",
                    description="You have not added your LeetCode username yet!",
                    color=discord.Color.red())
                embed.add_field(name="Add your LeetCode username",
                                value="Use the `/add <username>` command to add your LeetCode username.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        url = f"https://leetcode.com/{username}"
        logger.debug(url)
        response = requests.get(url, timeout=10)

        # Create a BeautifulSoup object to parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the <span> element with the specified class for rank
        rank_element = soup.find(
            "span", class_="ttext-label-1 dark:text-dark-label-1 font-medium")
        logger.debug(rank_element)

        rank = rank_element.text.strip() if rank_element else "N/A"
        logger.debug(rank)

        # Find all the <span> elements with the specified class for question counts
        span_elements = soup.find_all(
            "span",
            class_="mr-[5px] text-base font-medium leading-[20px] text-label-1 dark:text-dark-label-1"
        )
        logger.debug(span_elements)

        # Extract the text from each <span> element and store it in an array
        numbers = [span_element.text for span_element in span_elements]

        if len(numbers) == 3:
            easy_completed = int(numbers[0])
            medium_completed = int(numbers[1])
            hard_completed = int(numbers[2])
            logger.debug(numbers)

            total_questions_done = easy_completed + medium_completed + hard_completed
            total_score = easy_completed * DIFFICULTY_SCORE['easy'] + medium_completed * \
                DIFFICULTY_SCORE['medium'] + \
                hard_completed * DIFFICULTY_SCORE['hard']

            embed = discord.Embed(
                title=f"Rank: {rank}", color=discord.Color.green())
            embed.add_field(name="**Easy**",
                            value=f"{easy_completed}", inline=True)
            embed.add_field(name="**Medium**",
                            value=f"{medium_completed}", inline=True)
            embed.add_field(name="**Hard**",
                            value=f"{hard_completed}", inline=True)

            embed.set_footer(
                text=f"Total: {total_questions_done} | Score: {total_score}")

            embed.set_author(
                name=f"{username}'s LeetCode Stats",
                icon_url="https://repository-images.githubusercontent.com/98157751/7e85df00-ec67-11e9-98d3-684a4b66ae37"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            embed = discord.Embed(
                title="Error!",
                description="The username you entered is invalid or LeetCode timed out. Try Again!",
                color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return


async def setup(client):
    await client.add_cog(Stats(client))
