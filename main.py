import asyncio
import json
import logging
import os
import random
import string
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import json

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from dotenv import load_dotenv

from keep_alive import keep_alive

logging.basicConfig(filename="logs.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

logger = logging.getLogger()

load_dotenv()

session = requests.Session()
intents = discord.Intents().all()
client = commands.Bot(command_prefix=',', intents=intents)

DIFFICULTY_SCORE = {"easy": 1, "medium": 3, "hard": 7}
RANK_EMOJI = {1: "🥇", 2: "🥈", 3: "🥉"}
FIELD_TITLE_TIMEFRAME = {
    "total_score": "All-Time", "week_score": "Weekly"}


@client.tree.command(name="setdailychannel", description="Set where the daily problem will be sent")
async def setdailychannel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if channel is None:
        channel = interaction.channel
    # only allow this command to be used by users with the administrator permission
    if interaction.user.guild_permissions.administrator:
        # open the dailychannels.txt file in append mode
        # check if the channel is already in the file
        with open("dailychannels.txt", "r", encoding="UTF-8") as file:
            channels = file.readlines()
            logger.debug(channels)
            logger.debug(channel.id)
            if str(channel.id) + "\n" in channels or channel.id in channels:
                embed = discord.Embed(
                    title="Error!",
                    description="This channel is already set as the daily channel!",
                    color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            else:
                with open("dailychannels.txt", "a", encoding="UTF-8") as file:
                    file.write(f"{channel.id}\n")
                embed = discord.Embed(
                    title="Success!",
                    description="This channel has been set as the daily channel!",
                    color=discord.Color.green())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
    else:
        embed = discord.Embed(
            title="Error!",
            description="You do not have the administrator permission!",
            color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return


@client.tree.command(name="removedailychannel", description="Remove a daily channel")
async def removedailychannel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if channel is None:
        channel = interaction.channel
    # only allow this command to be used by users with the administrator permission
    if interaction.user.guild_permissions.administrator:
        # open the dailychannels.txt file in append mode
        # check if the channel is already in the file
        with open("dailychannels.txt", "r", encoding="UTF-8") as file:
            channels = file.readlines()
            logger.debug(channels)
            logger.debug(channel.id)
            if (str(channel.id) + "\n") in channels or channel.id in channels:
                with open("dailychannels.txt", "w", encoding="UTF-8") as file:
                    for line in channels:
                        if line.strip("\n") != str(channel.id):
                            file.write(line)
                embed = discord.Embed(
                    title="Success!",
                    description="This channel has been removed as the daily channel!",
                    color=discord.Color.green())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            else:
                embed = discord.Embed(
                    title="Error!",
                    description="This channel is not set as the daily channel!",
                    color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
    else:
        embed = discord.Embed(
            title="Error!",
            description="You do not have the administrator permission!",
            color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return


class Pagination(discord.ui.View):
    def __init__(self, user_id, pages=None, page=0):
        super().__init__()
        self.page = page
        self.user_id = user_id

        if pages is None:
            self.pages = []
        else:
            self.pages = pages

        self.max_page = len(self.pages) - 1

        if self.page == 0:
            self.previous.style = discord.ButtonStyle.gray
            self.previous.disabled = True

        if self.page == self.max_page:
            self.next.style = discord.ButtonStyle.gray
            self.next.disabled = True

    @discord.ui.button(label='<', style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer()
            return

        if self.page - 1 >= 0:
            self.page -= 1
            await interaction.message.edit(embed=self.pages[self.page])

            if self.page == 0:
                button.style = discord.ButtonStyle.gray
                button.disabled = True

        # if self.page < self.max_page:
        self.next.style = discord.ButtonStyle.blurple
        self.next.disabled = False

        logger.debug(self.page + 1)

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='>', style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer()
            return

        if self.page + 1 <= self.max_page:
            self.page += 1
            await interaction.message.edit(embed=self.pages[self.page])

            if self.page == self.max_page:
                button.style = discord.ButtonStyle.gray
                button.disabled = True

        self.previous.style = discord.ButtonStyle.blurple
        self.previous.disabled = False

        logger.debug(self.page + 1)

        await interaction.response.edit_message(view=self)



# @client.tree.command(name="graph", description="View the leaderboard graph")
# async def graph(interaction: discord.Interaction, page: int = 1):
#     # Read the JSON file
#     server_id = str(interaction.guild.id)
#     with open(f"{server_id}_leetcode_stats.json", "r") as file:
#         data = json.load(file)
    
#     # Extract the usernames and scores
#     sorted_data = sorted(data.items(), key=lambda x: x[1]["total_score"], reverse=True)
#     usernames = []
#     scores = []
#     for user, stats in sorted_data:
#         usernames.append(stats["discord_username"])
#         scores.append(stats["total_score"])
    
#     # Calculate pagination
#     items_per_page = 10
#     start_idx = (page - 1) * items_per_page
#     end_idx = start_idx + items_per_page
    
#     # Slice the data based on the page
#     usernames = usernames[start_idx:end_idx]
#     scores = scores[start_idx:end_idx]
    
#     # Create the graph
#     plt.figure(figsize=(10, 6))
#     plt.plot(usernames, scores, marker='o')
#     plt.xlabel("Usernames")
#     plt.ylabel("Total Scores")
#     plt.title("Leaderboard")
#     plt.xticks(rotation=45)
    
#     # Save the graph as an image
#     graph_filename = "leaderboard_graph.png"
#     plt.savefig(graph_filename)
#     plt.close()
    
#     # Send the graph image on Discord
#     embed = discord.Embed(
#         title=f"Leaderboard Graph (Page {page})",
#         description="Here is the leaderboard graph.",
#         color=discord.Color.blurple())
#     await interaction.response.send_message(embed=embed)
#     await interaction.channel.send(file=discord.File(graph_filename))



async def create_leaderboard(interaction: discord.Interaction, timeframe_field: str = "total_score", page: int = 1):
    logger.debug(interaction.guild.id)

    users_per_page = 10

    if not os.path.exists(f"{interaction.guild.id}_leetcode_stats.json"):
        embed = discord.Embed(
            title=f"{FIELD_TITLE_TIMEFRAME[timeframe_field]} Leaderboard",
            description="No one has added their LeetCode username yet.",
            color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    with open(f"{interaction.guild.id}_leetcode_stats.json", "r", encoding="UTF-8") as file:
        data = json.load(file)

    sorted_data = sorted(data.items(),
                         key=lambda x: x[1][timeframe_field],
                         reverse=True)

    pages = []
    page_count = -(-len(sorted_data)//users_per_page)

    for i in range(page_count):
        leaderboard = []

        for j, (
            username,
            stats,
        ) in enumerate(sorted_data[i * users_per_page: i * users_per_page + users_per_page], start=i * users_per_page + 1):
            profile_link = f"https://leetcode.com/{username}"
            # Get the discord_username from the stats data in the JSON file
            discord_username = stats.get("discord_username")
            # Get the link_yes_no from the stats data in the JSON file
            link_yes_no = stats.get("link_yes_no") == "yes"

            if discord_username:
                number_rank = f"{j}\."
                discord_username_with_link = f"[{discord_username}]({profile_link})"
                leaderboard.append(
                    f"**{RANK_EMOJI[j] if j in RANK_EMOJI else number_rank} {discord_username_with_link if link_yes_no else discord_username}**  {stats[timeframe_field]} points"
                )

        embed = discord.Embed(title=f"{FIELD_TITLE_TIMEFRAME[timeframe_field]} Leaderboard",
                              color=discord.Color.yellow())
        embed.description = "\n".join(leaderboard)
        # Score Methodology: Easy: 1, Medium: 3, Hard: 7
        embed.set_footer(
            text=f"Score Methodology: Easy: {DIFFICULTY_SCORE['easy']} point, Medium: {DIFFICULTY_SCORE['medium']} points, Hard: {DIFFICULTY_SCORE['hard']} points\n\nPage {i + 1}/{page_count}")
        # Score Equation: Easy * 1 + Medium * 3 + Hard * 7 = Total Score
        logger.debug(leaderboard)
        pages.append(embed)

    page = page - 1 if page > 0 else 0
    await interaction.response.send_message(embed=pages[page], view=Pagination(interaction.user.id, pages, page))


@client.tree.command(name="leaderboard", description="View the All-Time leaderboard")
async def leaderboard(interaction: discord.Interaction, timeframe_field: str = "total_score", page: int = 1):
    await create_leaderboard(interaction, timeframe_field, page)

@client.tree.command(name="weekly", description="View the Weekly leaderboard")
async def weekly(interaction: discord.Interaction, page: int = 1):
    await create_leaderboard(interaction, "week_score", page)




@client.tree.command(name="stats", description="Prints the stats of a user")
async def stats(interaction: discord.Interaction, username: str = None):
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


@client.tree.command(name="daily", description="Returns the daily problem")
async def daily(interaction: discord.Interaction):
    url = 'https://leetcode.com/graphql'

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'operationName':
        'daily',
        'query':
        '''
        query daily {
            challenge: activeDailyCodingChallengeQuestion {
                date
                link
                question {
                    difficulty
                    title
                }
            }
        }
    '''
    }

    response = requests.post(url, json=data, headers=headers, timeout=10)
    response_data = response.json()

    # Extract and print the link
    link = response_data['data']['challenge']['link']
    # Extract and print the title
    title = response_data['data']['challenge']['question']['title']
    # Extract and print the difficulty
    difficulty = response_data['data']['challenge']['question']['difficulty']
    # Extract and print the date
    # date = response_data['data']['challenge']['date']
    link = f"https://leetcode.com{link}"
    embed = discord.Embed(title=f"Daily Problem: {title}",
                          color=discord.Color.blue())
    embed.add_field(name="**Difficulty**", value=f"{difficulty}", inline=True)
    embed.add_field(name="**Link**", value=f"{link}", inline=False)

    await interaction.response.send_message(embed=embed)
    return


@client.tree.command(
    name="add",
    description="Adds a user to the leaderboard. Answer with 'yes' to link your LeetCode profile to the leaderboard."
)
async def add(interaction: discord.Interaction, username: str, link: str = "yes"):
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
            "history": {}
        }

        with open(f"{interaction.guild.id}_leetcode_stats.json", "w", encoding="UTF-8") as file:
            json.dump(existing_data, file)
        embed = discord.Embed(title="Profile Added",
                              color=discord.Color.green())
        embed.add_field(name="Username:", value=f"{username}", inline=False)
        await interaction.edit_original_response(embed=embed)

        return
    else:
        embed = discord.Embed(title="Profile Not Added",
                              color=discord.Color.red())
        embed.add_field(name="Username:", value=f"{username}", inline=False)
        await interaction.edit_original_response(embed=embed)
        return


@client.tree.command(name="delete", description="Delete your profile from the leaderboard.")
async def delete(interaction: discord.Interaction):
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


@client.tree.command(
    name="question",
    description="Request a question based on difficulty or at random")
async def question(interaction: discord.Interaction, difficulty: str = "random"):
    if difficulty == "easy":
        response = requests.get(
            "https://leetcode.com/api/problems/all/", timeout=10)
        # Check if the request was successful
        if response.status_code == 200:
            # Load the response data as a JSON object
            data = response.json()

            # Get a list of all easy questions from the data
            easy_questions = [
                question for question in data['stat_status_pairs']
                if question['difficulty']['level'] == 1
            ]

            # Select a random easy question from the list
            question = random.choice(easy_questions)

            # Extract the question title and link from the data
            title = question['stat']['question__title']
            link = f"https://leetcode.com/problems/{question['stat']['question__title_slug']}/"

            embed = discord.Embed(title="LeetCode Question",
                                  color=discord.Color.green())
            embed.add_field(name="Easy", value=title, inline=False)
            embed.add_field(name="Link", value=link, inline=False)

            await interaction.response.send_message(embed=embed)
        else:
            # If the request was not successful, send an error message to the Discord channel
            await interaction.response.send_message(
                "An error occurred while trying to get the question from LeetCode.")
        return
    elif difficulty == "medium":
        response = requests.get(
            "https://leetcode.com/api/problems/all/", timeout=10)
        # Check if the request was successful
        if response.status_code == 200:
            # Load the response data as a JSON object
            data = response.json()

            # Get a list of all medium questions from the data
            medium_questions = [
                question for question in data['stat_status_pairs']
                if question['difficulty']['level'] == 2
            ]

            # Select a random medium question from the list
            question = random.choice(medium_questions)
            title = question['stat']['question__title']
            link = f"https://leetcode.com/problems/{question['stat']['question__title_slug']}/"

            embed = discord.Embed(title="LeetCode Question",
                                  color=discord.Color.orange())
            embed.add_field(name="Medium", value=title, inline=False)
            embed.add_field(name="Link", value=link, inline=False)

            await interaction.response.send_message(embed=embed)
        else:
            # If the request was not successful, send an error message to the Discord channel
            await interaction.response.send_message(
                "An error occurred while trying to get the question from LeetCode.")
        return
    elif difficulty == "hard":
        response = requests.get(
            "https://leetcode.com/api/problems/all/", timeout=10)
        # Check if the request was successful
        if response.status_code == 200:
            # Load the response data as a JSON object
            data = response.json()

            # Get a list of all hard questions from the data
            hard_questions = [
                question for question in data['stat_status_pairs']
                if question['difficulty']['level'] == 3
            ]

            # Select a random hard question from the list
            question = random.choice(hard_questions)

            title = question['stat']['question__title']
            link = f"https://leetcode.com/problems/{question['stat']['question__title_slug']}/"

            embed = discord.Embed(title="LeetCode Question",
                                  color=discord.Color.red())
            embed.add_field(name="Hard", value=title, inline=False)
            embed.add_field(name="Link", value=link, inline=False)

            await interaction.response.send_message(embed=embed)
        else:
            # If the request was not successful, send an error message to the Discord channel
            await interaction.response.send_message(
                "An error occurred while trying to get the question from LeetCode.")
        return

    elif difficulty == "random":
        url = session.get(
            'https://leetcode.com/problems/random-one-question/all').url

        embed = discord.Embed(title="Random Question",
                              color=discord.Color.green())
        embed.add_field(name="URL", value=url, inline=False)

        await interaction.response.send_message(embed=embed)
        return
    else:
        await interaction.response.send_message(
            "Please enter a valid difficulty level. (easy, medium, hard, random)",
            ephemeral=True)
        return


@ client.tree.command(name="help", description="Displays the help menu")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="LeetCode Bot Help",
                          color=discord.Color.blue())
    embed.add_field(
        name="Adding Your Account to the Leaderboard",
        value="Use `/add {username}` to add your account to the leaderboard. Say 'yes' to link your LeetCode account to the leaderboard and 'no' to not link your LeetCode account to the leaderboard.",
        inline=False)
    embed.add_field(
        name="Getting Your Stats",
        value="Use `/stats` to get your LeetCode statistics, *or* use `/stats {username}` to get the LeetCode statistics of another user.",
        inline=False)
    embed.add_field(
        name="Server Leaderboard",
        value="Use `/leaderboard {page}` to see the leaderboard of this server.",
        inline=False)
    embed.add_field(
        name="Random Questions",
        value="Use `/question {difficulty}` to get a random question of that level, or random if you want a random question of any level.",
        inline=False)
    embed.add_field(
        name="Score Calculation",
        value=f"The score is calculated based on the amount of questions you have solved. Easy questions are worth {DIFFICULTY_SCORE['easy']} point, medium questions are worth {DIFFICULTY_SCORE['medium']} points, and hard questions are worth {DIFFICULTY_SCORE['hard']} points.",
        inline=False)
    # for adminstrators
    if interaction.user.guild_permissions.administrator:
        embed.add_field(
            name="Set Daily LeetCode Channel",
            value="Use `/setdailychannel` to set the channel where the daily LeetCode question will be sent.",
            inline=False)
        embed.add_field(
            name="Remove Daily LeetCode Channel",
            value="Use `/removedailychannel` to remove the channel where the daily LeetCode question will be sent.",
            inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


async def send_message_at_midnight():
    await client.wait_until_ready()
    while not client.is_closed():
        await asyncio.sleep(3600)  # sleep for a hour
        now = datetime.utcnow()

        logger.debug("%s %s", now.hour, now.minute)
        if now.hour == 0:
            # get the channel object
            # send the message
            url = 'https://leetcode.com/graphql'

            headers = {
                'Content-Type': 'application/json',
            }

            data = {
                'operationName':
                'daily',
                'query':
                '''
                query daily {
                    challenge: activeDailyCodingChallengeQuestion {
                        date
                        link
                        question {
                            difficulty
                            title
                        }
                    }
                }
            '''
            }

            response = requests.post(url, json=data, headers=headers)
            response_data = response.json()

            # Extract and print the link
            link = response_data['data']['challenge']['link']
            link = f"https://leetcode.com{link}"
            # Extract and print the title
            title = response_data['data']['challenge']['question']['title']
            # Extract and print the difficulty
            difficulty = response_data['data']['challenge']['question']['difficulty']
            # Extract and print the date
            embed = discord.Embed(title=f"Daily Problem: {title}",
                                  color=discord.Color.blue())
            embed.add_field(name="**Difficulty**",
                            value=f"{difficulty}", inline=True)
            embed.add_field(name="**Link**", value=f"{link}", inline=False)
            # import channels from dailychannels.txt
            with open('dailychannels.txt', 'r', encoding="UTF-8") as f:
                channels = f.readlines()
            channels = [channel.strip() for channel in channels]
            for channel_id in channels:
                channel = client.get_channel(int(channel_id))
                await channel.send(embed=embed)
                # Pin the message
                async for message in channel.history(limit=1):
                    await message.pin()

        if now.hour == 0 or now.hour == 6 or now.hour == 12 or now.hour == 18:
            update_stats(now)


def update_stats(now: datetime):
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
            for username in data.keys():
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


@client.event
async def on_ready():
    logger.info("%s %s", datetime.utcnow().hour,
                datetime.utcnow().time)
    logger.info("Logged in as a bot %s", client.user)
    server_ids = [guild.id for guild in client.guilds]
    logger.info('Server IDs: %s', server_ids)

    # ? updates stats on
    update_stats(datetime.now())
    logger.debug("Stats updated")

    try:
        synced = await client.tree.sync()
        logger.info("Synced %s commands", len(synced))
    except Exception as e:
        logger.exception(e)
    await send_message_at_midnight()

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logger.info("Logger is in DEBUG mode")

    my_secret = os.environ['TOKEN']
    keep_alive()
    client.run(my_secret)
