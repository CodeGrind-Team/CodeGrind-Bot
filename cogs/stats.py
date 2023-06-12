import json
import os
from datetime import datetime, timedelta

import discord
import requests
from discord.ext import commands

from bot_globals import DIFFICULTY_SCORE, logger
from utils.run_blocking import to_thread


def get_problems_solved_and_rank(leetcode_username: str):
    logger.info(
        "file: cogs/stats.py ~ get_problems_solved_and_rank ~ run ~ leetcode_username: %s", leetcode_username)

    url = 'https://leetcode.com/graphql'

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'operationName': 'getProblemsSolvedAndRank',
        'query':
        '''query getProblemsSolvedAndRank($username: String!) {
            matchedUser(username: $username) {
                profile {
                    realName
                    ranking
                }
                submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
            }
        }
        ''',
        'variables': {'username': leetcode_username}
    }

    # Example data:
    # {
    #     "data": {
    #         "matchedUser": {
    #             "profile": { "ranking": 552105 , "realName": "XYZ"},
    #             "submitStatsGlobal": {
    #                 "acSubmissionNum": [
    #                 { "difficulty": "All", "count": 118 },
    #                 { "difficulty": "Easy", "count": 43 },
    #                 { "difficulty": "Medium", "count": 63 },
    #                 { "difficulty": "Hard", "count": 12 }
    #                 ]
    #             }
    #         }
    #     }
    # }

    logger.info(
        "file: cogs/stats.py ~ get_problems_solved_and_rank ~ data requesting ~ https://leetcode.com/%s", leetcode_username)

    response = requests.post(
        url, json=data, headers=headers, timeout=10)
    response_data = response.json()
    if response_data["data"]["matchedUser"] is None:
        logger.warning(
            "file: cogs/stats.py ~ get_problems_solved_and_rank ~ user not found ~ https://leetcode.com/%s", leetcode_username)
        return None

    logger.info(
        "file: cogs/stats.py ~ get_problems_solved_and_rank ~ data requested successfully ~ https://leetcode.com/%s", leetcode_username)

    stats = response_data["data"]["matchedUser"]

    questionsCompleted = {}

    for dic in stats["submitStatsGlobal"]["acSubmissionNum"]:
        questionsCompleted[dic["difficulty"]] = dic["count"]

    stats["submitStatsGlobal"]["acSubmissionNum"] = questionsCompleted

    return stats


@to_thread
def update_stats(client, now: datetime, weekly_reset: bool = False):
    logger.info("file: cogs/stats.py ~ update_stats ~ run ~ now: %s | weekly reset: %s",
                weekly_reset, now.strftime("%d/%m/%Y, %H:%M:%S"))
    # retrieve every server the bot is in
    server_ids = [guild.id for guild in client.guilds]
    logger.info(
        'file: cogs/stats.py ~ update_stats ~ server IDs: %s', server_ids)

    # for each server, retrieve the leaderboard
    for server_id in server_ids:
        logger.info(
            'file: cogs/stats.py ~ update_stats ~ current server ID: %s', server_ids)
        # retrieve the keys from the json file
        if os.path.exists(f"data/{server_id}_leetcode_stats.json"):
            with open(f'data/{server_id}_leetcode_stats.json', 'r', encoding="UTF-8") as f:
                data = json.load(f)

            sorted_data = sorted(data["users"].items(),
                                 key=lambda x: x[1]["week_score"],
                                 reverse=True)

            for place, (discord_id, stats) in enumerate(sorted_data):
                leetcode_username = stats["leetcode_username"]

                submissions_and_rank = get_problems_solved_and_rank(
                    leetcode_username)

                if submissions_and_rank is None:
                    continue

                rank = submissions_and_rank["profile"]["ranking"]

                easy_completed = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Easy"]
                medium_completed = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Medium"]
                hard_completed = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["Hard"]
                total_questions_done = submissions_and_rank["submitStatsGlobal"]["acSubmissionNum"]["All"]

                total_score = easy_completed * \
                    DIFFICULTY_SCORE["easy"] + medium_completed * \
                    DIFFICULTY_SCORE["medium"] + \
                    hard_completed * DIFFICULTY_SCORE["hard"]

                # Due to this field is added after some users have already been added,
                # it needs to be created and set to an empty dictionary
                # TODO: replace this with a function to automatically fill in missing fields
                if "history" not in stats:
                    data["users"][discord_id]["history"] = {}

                if "week_score" not in stats:
                    data["users"][discord_id]["week_score"] = 0

                if "weeklies_ranking" not in stats:
                    data["users"][discord_id]["weeklies_ranking"] = {}

                if weekly_reset:
                    data["users"][discord_id]["weeklies_ranking"][str(now.strftime(
                        "%d/%m/%Y"))] = place + 1

                start_of_week = now - timedelta(days=now.weekday() % 7)

                while start_of_week <= now:
                    start_of_week_date = start_of_week.strftime("%d/%m/%Y")
                    if str(start_of_week_date) not in stats["history"]:
                        start_of_week += timedelta(days=1)
                        continue

                    start_of_week_easy_completed = stats["history"][str(
                        start_of_week_date)]['easy']
                    start_of_week_medium_completed = stats["history"][str(
                        start_of_week_date)]['medium']
                    start_of_week_hard_completed = stats["history"][str(
                        start_of_week_date)]['hard']

                    start_of_week_score = start_of_week_easy_completed * \
                        DIFFICULTY_SCORE["easy"] + start_of_week_medium_completed * \
                        DIFFICULTY_SCORE["medium"] + \
                        start_of_week_hard_completed * \
                        DIFFICULTY_SCORE["hard"]
                    week_score = total_score - start_of_week_score

                    data["users"][discord_id]["week_score"] = week_score
                    break

                today = now.strftime("%d/%m/%Y")

                if str(today) in stats["history"]:
                    today_easy_completed = stats["history"][str(today)]['easy']
                    today_medium_completed = stats["history"][str(
                        today)]['medium']
                    today_hard_completed = stats["history"][str(today)]['hard']

                    start_of_day_points = today_easy_completed * \
                        DIFFICULTY_SCORE["easy"] + today_medium_completed * \
                        DIFFICULTY_SCORE["medium"] + \
                        today_hard_completed * \
                        DIFFICULTY_SCORE["hard"]

                    today_score = total_score - start_of_day_points
                else:
                    today_score = 0

                data["users"][discord_id]["rank"] = rank
                data["users"][discord_id]["easy"] = easy_completed
                data["users"][discord_id]["medium"] = medium_completed
                data["users"][discord_id]["hard"] = hard_completed
                data["users"][discord_id]["total_questions_done"] = total_questions_done
                data["users"][discord_id]["total_score"] = total_score
                data["users"][discord_id]["today_score"] = today_score

                if str(now.strftime("%d/%m/%Y")) not in stats["history"]:
                    data["users"][discord_id]["history"][str(now.strftime("%d/%m/%Y"))] = {
                        "easy": easy_completed, "medium": medium_completed, "hard": hard_completed}

                data["last_updated"] = now.strftime("%d/%m/%Y %H:%M:%S")

                # update the json file
                with open(f"data/{server_id}_leetcode_stats.json", "w", encoding="UTF-8") as f:
                    json.dump(data, f, indent=4)
                    logger.info(
                        'file: cogs/stats.py ~ update_stats ~ user stats updated successfully: %s', leetcode_username)


class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client

    @discord.app_commands.command(name="stats", description="Prints the stats of a user")
    async def stats(self, interaction: discord.Interaction, leetcode_username: str = None):
        logger.info(
            'file: cogs/stats.py ~ stats ~ run ~ leetcode_username: %s', leetcode_username)

        discord_user = interaction.user

        if leetcode_username is None:
            with open(f"data/{interaction.guild.id}_leetcode_stats.json", "r", encoding="UTF-8") as file:
                data = json.load(file)

            if str(discord_user.id) in data["users"]:
                leetcode_username = data["users"][str(discord_user.id)]["leetcode_username"]
            else:
                logger.info(
                    'file: cogs/stats.py ~ stats ~ user not found: %s', leetcode_username)

                embed = discord.Embed(
                    title="Error!",
                    description="You have not added your LeetCode username yet!",
                    color=discord.Color.red())
                embed.add_field(name="Add your LeetCode username",
                                value="Use the `/add <username>` command to add your LeetCode username.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        stats = get_problems_solved_and_rank(leetcode_username)

        if stats is not None:
            rank = stats["profile"]["ranking"]
            easy_completed = stats["submitStatsGlobal"]["acSubmissionNum"]["Easy"]
            medium_completed = stats["submitStatsGlobal"]["acSubmissionNum"]["Medium"]
            hard_completed = stats["submitStatsGlobal"]["acSubmissionNum"]["Hard"]
            total_questions_done = stats["submitStatsGlobal"]["acSubmissionNum"]["All"]

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
                name=f"{leetcode_username}'s LeetCode Stats",
                icon_url="https://repository-images.githubusercontent.com/98157751/7e85df00-ec67-11e9-98d3-684a4b66ae37"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="Error!",
                description="The username you entered is invalid or LeetCode timed out. Try Again!",
                color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client):
    await client.add_cog(Stats(client))
