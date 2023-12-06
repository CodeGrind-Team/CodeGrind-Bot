import io
import os
from typing import Tuple

import discord
import requests

from bot_globals import hti
from embeds.misc_embeds import error_embed
from utils.common_utils import to_thread


@to_thread
def stats_embed(leetcode_username: str, display_name: str, extension: str | None = None) -> Tuple[discord.Embed, discord.File | None]:
    embed = discord.Embed(title=display_name,
                          url=f"https://leetcode.com/{leetcode_username}", color=discord.Color.orange())

    width = 500
    height = 200
    if extension is not None:
        if extension == "activity":
            height = 400
        elif extension == "heatmap":
            height = 350

    url = f"https://leetcard.jacoblin.cool/{leetcode_username}?theme=dark&animation=false&width={width}&height={height}&ext={extension}"

    # Making sure the website is reachable before running hti.screenshot()
    # as the method will stall if url isn't reachable.
    try:
        response = requests.get(url)

        if response.status_code != 200:
            return error_embed(), None

    except requests.exceptions.RequestException as e:
        return error_embed(), None

    paths = hti.screenshot(url=url, size=(width, height))

    with open(paths[0], "rb") as f:
        # read the file contents
        data = f.read()
        # create a BytesIO object from the data
        image_binary = io.BytesIO(data)
        # move the cursor to the beginning
        image_binary.seek(0)

        file = discord.File(
            fp=image_binary, filename=f"{leetcode_username}.png")

    os.remove(paths[0])

    embed.set_image(url=f"attachment://{leetcode_username}.png")

    return embed, file


def invalid_username_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Error",
        description="The username you entered is invalid",
        color=discord.Color.red())

    return embed


def account_hidden_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Cannot access data",
        description="The chosen user has their LeetCode details hidden as their `include_url` setting is set to OFF",
        color=discord.Color.red())

    return embed
