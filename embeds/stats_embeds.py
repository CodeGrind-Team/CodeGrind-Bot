import io
import os
from typing import Tuple

import discord
import requests

from bot_globals import hti
from embeds.misc_embeds import error_embed
from utils.run_blocking import to_thread


@to_thread
def stats_embed(leetcode_username: str) -> Tuple[discord.Embed, discord.File | None]:
    embed = discord.Embed(title=leetcode_username,
                          url=f"https://leetcode.com/{leetcode_username}", color=discord.Color.orange())
    embed.set_footer(
        text="Credit to github.com/JacobLinCool/LeetCode-Stats-Card")

    url = f"https://leetcard.jacoblin.cool/{leetcode_username}?theme=dark&font=Overpass%20Mono&animation=false&width=500&ext=activity"

    # Making sure the website is reachable before running hti.screenshot()
    # as the method will stall if url isn't reachable.
    try:
        get = requests.get(url)

        if get.status_code != 200:
            return error_embed(), None

    except requests.exceptions.RequestException as e:
        return error_embed(), None

    paths = hti.screenshot(url=url, size=(500, 400))

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
