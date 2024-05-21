import io
import os

import discord
import requests
from discord.ext import commands

from constants import StatsCardExtensions
from embeds.misc import error_embed
from utils.common import to_thread


@to_thread
def stats_embed(
    bot: commands.Bot,
    leetcode_id: str,
    display_name: str,
    extension: StatsCardExtensions,
) -> tuple[discord.Embed, discord.File | None]:
    embed = discord.Embed(
        title=display_name,
        url=f"https://leetcode.com/{leetcode_id}",
        colour=discord.Colour.orange(),
    )

    width = 500
    height = 200
    if extension in (StatsCardExtensions.ACTIVITY, StatsCardExtensions.CONTEST):
        height = 400
    elif extension == StatsCardExtensions.HEATMAP:
        height = 350

    url = f"""https://leetcard.jacoblin.cool/{leetcode_id}?theme=dark&animation=false&
    width={width}&height={height}&ext={extension.value}"""

    # Making sure the website is reachable before running hti.screenshot()
    # as the method will stall if url isn't reachable.
    try:
        response = requests.get(url)
        response.raise_for_status()

    except requests.exceptions.RequestException:
        return error_embed(), None

    paths = bot.html2image.screenshot(url=url, size=(width, height))

    with open(paths[0], "rb") as f:
        # read the file contents
        data = f.read()
        # create a BytesIO object from the data
        image_binary = io.BytesIO(data)
        # move the cursor to the beginning
        image_binary.seek(0)

        file = discord.File(fp=image_binary, filename=f"{leetcode_id}.png")

    os.remove(paths[0])

    embed.set_image(url=f"attachment://{leetcode_id}.png")

    return embed, file


def invalid_username_embed() -> discord.Embed:
    return discord.Embed(
        title="Error",
        description="The username you entered is invalid",
        colour=discord.Colour.red(),
    )


def account_hidden_embed() -> discord.Embed:
    return discord.Embed(
        title="Cannot access data",
        description="""The chosen user has their LeetCode details hidden as their
          `include_url` setting is set to OFF""",
        colour=discord.Colour.red(),
    )
