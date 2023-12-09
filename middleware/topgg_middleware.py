from datetime import datetime
from functools import wraps
from typing import Callable

import discord

from database.models.user_model import User
from embeds.topgg_embeds import topgg_not_voted


def topgg_vote_required(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs) -> Callable | None:
        user = await User.find_one(User.id == interaction.user.id)

        if not user.votes.last_voted or (user.votes.last_voted and (datetime.utcnow() - user.votes.last_voted).days > 30):
            embed = topgg_not_voted()
            await interaction.followup.send(embed=embed)
            return

        return await func(self, interaction, *args, **kwargs)

    return wrapper
