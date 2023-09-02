import discord
import pytz
from bot_globals import DIFFICULTY_SCORE
from models.server_model import Server


def empty_leaderboard_embed() -> discord.Embed:
    embed = discord.Embed(
        title=f"Leaderboard is empty",
        description="No one has added their LeetCode username yet",
        color=discord.Color.red())

    return embed


def leaderboard_embed(server: Server, page_i: int, page_count: int, title: str, leaderboard: str) -> discord.Embed:
    embed = discord.Embed(title=title,
                          color=discord.Color.yellow())

    embed.description = "\n".join(leaderboard)

    last_updated = pytz.timezone("UTC").localize(
        server.last_updated).astimezone(pytz.timezone(server.timezone)).strftime("%d/%m/%Y %H:%M %Z")

    embed.set_footer(
        text=f"Easy: {DIFFICULTY_SCORE['easy']} point, Medium: {DIFFICULTY_SCORE['medium']} points, Hard: {DIFFICULTY_SCORE['hard']} points\nUpdated on {last_updated}\nPage {page_i + 1}/{page_count}")

    return embed
