from typing import List

import discord
from beanie.odm.operators.update.array import AddToSet, Pull

from models.server_model import Server


def get_options(available_types: List[str]) -> List[discord.SelectOption]:
    options = []

    if "maintenance" in available_types:
        select_option = discord.SelectOption(label="maintenance",
                                             description="Get bot updates and downtime")

        options.append(select_option)

    if "daily_question" in available_types:
        select_option = discord.SelectOption(label="daily question",
                                             description="Get the daily question every midnight (UTC)")

        options.append(select_option)

    if "winners" in available_types:
        select_option = discord.SelectOption(label="leaderboard winners",
                                             description="Display the daily and weekly leaderboard winners")

        options.append(select_option)

    return options


async def save_channel_options(server_id: int, channel_id: int, adding: bool, selected_options: List[str]) -> None:
    if adding:
        if "maintenance" in selected_options:
            await Server.find_one(Server.id == server_id).update(AddToSet({Server.channels.maintenance: channel_id}))

        if "daily_question" in selected_options:
            await Server.find_one(Server.id == server_id).update(AddToSet({Server.channels.daily_question: channel_id}))

        if "winners" in selected_options:
            await Server.find_one(Server.id == server_id).update(AddToSet({Server.channels.winners: channel_id}))

    else:
        if "maintenance" in selected_options:
            await Server.find_one(Server.id == server_id).update(Pull({Server.channels.maintenance: channel_id}))

        if "daily_question" in selected_options:
            await Server.find_one(Server.id == server_id).update(Pull({Server.channels.daily_question: channel_id}))

        if "winners" in selected_options:
            await Server.find_one(Server.id == server_id).update(Pull({Server.channels.winners: channel_id}))
