import os
from datetime import datetime, timedelta

import discord

from bot_globals import (DIFFICULTY_SCORE, RANK_EMOJI, TIMEFRAME_TITLE,
                         TIMEZONE, client, logger)
from utils.io_handling import read_file

class Pagination(discord.ui.View):
    def __init__(self, user_id: int | None = None, pages: list[discord.Embed] | None = None, page: int = 0):
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
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self.user_id is None or interaction.user.id != self.user_id or interaction.message is None:
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

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='>', style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self.user_id is None or interaction.user.id != self.user_id or interaction.message is None:
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

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='🗑️', style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.user_id or interaction.message is None:
            await interaction.response.defer()
            return

        await interaction.message.delete()


async def display_leaderboard(send_message, server_id, user_id=None, timeframe: str = "alltime", page: int = 1, winners_only: bool = False, users_per_page: int = 10):
    logger.info(
        "file: cogs/leaderboards.py ~ display_leaderboard ~ run ~ guild id: %s", server_id)

    if not os.path.exists(f"data/{server_id}_leetcode_stats.json"):
        embed = discord.Embed(
            title=f"{TIMEFRAME_TITLE[timeframe]['title']} Leaderboard",
            description="No one has added their LeetCode username yet.",
            color=discord.Color.red())
        await send_message(embed=embed)
        return

    data = await read_file(f"data/{server_id}_leetcode_stats.json")

    last_updated = data["last_updated"]

    sorted_data = sorted(data["users"].items(),
                         key=lambda x: x[1][TIMEFRAME_TITLE[timeframe]['field']],
                         reverse=True)

    if winners_only:
        sorted_data = sorted_data[:3]

    pages = []
    page_count = -(-len(sorted_data)//users_per_page)

    for i in range(page_count):
        leaderboard = []

        for j, (
            _,
            stats,
        ) in enumerate(sorted_data[i * users_per_page: i * users_per_page + users_per_page], start=i * users_per_page + 1):
            leetcode_username = stats["leetcode_username"]

            profile_link = f"https://leetcode.com/{leetcode_username}"
            # Get the discord_username from the stats data in the JSON file
            discord_username = stats["discord_username"]
            # Get the hyperlink from the stats data in the JSON file
            hyperlink = stats["hyperlink"]
            if discord_username:
                number_rank = f"{j}\."
                discord_username_with_link = f"[{discord_username}]({profile_link})"

                wins = 0

                if timeframe == "daily":
                    wins = sum(
                        rank == 1 for rank in stats['daily_rankings'].values())
                    if winners_only and j == 1:
                        wins += 1

                elif timeframe == "weekly":
                    wins = sum(
                        rank == 1 for rank in stats['weekly_rankings'].values())
                    if winners_only and j == 1:
                        wins += 1

                wins_text = f"({str(wins)} wins) "
                # wins won't be displayed for alltime timeframe as wins !> 0
                leaderboard.append(
                    f"**{RANK_EMOJI[j] if j in RANK_EMOJI else number_rank} {discord_username_with_link if hyperlink else discord_username}** {wins_text if  wins > 0 else ''}- **{stats[TIMEFRAME_TITLE[timeframe]['field']]}** pts"
                )

        title = f"{TIMEFRAME_TITLE[timeframe]['title']} Leaderboard"
        if winners_only:
            if timeframe == "daily":
                title = f"{TIMEFRAME_TITLE[timeframe]['title']} Winners: {(datetime.now(TIMEZONE) - timedelta(days=1)).strftime('%d/%m/%Y')}"

            elif timeframe == "weekly":
                title = f"{TIMEFRAME_TITLE[timeframe]['title']} Winners: {(datetime.now(TIMEZONE) - timedelta(days=7)).strftime('%d/%m/%Y')} - {(datetime.now(TIMEZONE) - timedelta(days=1)).strftime('%d/%m/%Y')}"

        embed = discord.Embed(title=title,
                              color=discord.Color.yellow())

        embed.description = "\n".join(leaderboard)
        # Score Methodology: Easy: 1, Medium: 3, Hard: 7
        embed.set_footer(
            text=f"Easy: {DIFFICULTY_SCORE['easy']} point, Medium: {DIFFICULTY_SCORE['medium']} points, Hard: {DIFFICULTY_SCORE['hard']} points\nUpdated on {last_updated}\nPage {i + 1}/{page_count}")
        # Score Equation: Easy * 1 + Medium * 3 + Hard * 7 = Total Score
        pages.append(embed)

    page = page - 1 if page > 0 else 0
    view = None if winners_only else Pagination(user_id, pages, page)
    await send_message(embed=pages[page], view=view)


async def send_leaderboard_winners(timeframe: str) -> None:
    for filename in os.listdir("./data"):
        if filename.endswith(".json"):
            server_id = int(filename.split("_")[0])

            data = await read_file(f"data/{server_id}_leetcode_stats.json")

            if "channels" in data:
                for channel_id in data["channels"]:
                    channel = client.get_channel(channel_id)

                    if not isinstance(channel, discord.TextChannel):
                        continue

                    await display_leaderboard(channel.send, server_id, timeframe=timeframe, winners_only=True, users_per_page=3)

    logger.info(
        "file: utils/leaderboards.py ~ send_leaderboard_winners ~ %s winners leaderboard sent to channels", timeframe)
