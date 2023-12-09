from functools import wraps
from typing import Callable

import discord

from database.models.analytics_model import Analytics
from database.models.server_model import Server
from database.models.user_model import User
from views.user_settings_view import EmbedAndField, UserSettingsPrompt


def ensure_server_document(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs) -> Callable | None:
        server_id = interaction.guild.id
        server = await Server.get(server_id)

        if not server:
            server = Server(id=server_id)
            await server.create()

        return await func(self, interaction, *args, **kwargs)

    return wrapper


def track_analytics(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs) -> Callable | None:
        analytics = await Analytics.find_all().to_list()

        if not analytics:
            analytics = Analytics()
            await analytics.create()
        else:
            analytics = analytics[0]

        if interaction.user.id not in analytics.distinct_users_total:
            analytics.distinct_users_total.append(interaction.user.id)

        if interaction.user.id not in analytics.distinct_users_today:
            analytics.distinct_users_today.append(interaction.user.id)

        analytics.command_count_today += 1
        await analytics.save()

        return await func(self, interaction, *args, **kwargs)

    return wrapper


async def update_user_settings_prompt(interaction: discord.Interaction) -> None:
    user = await User.find_one(User.id == interaction.user.id)

    if not user:
        return

    pages = [
        EmbedAndField(discord.Embed(title="TEST 1: URL",
                                    description="TEST 1"), "url"),
        EmbedAndField(discord.Embed(title="TEST 2: PRIVATE",
                                    description="TEST 2"), "private")
    ]

    view = UserSettingsPrompt(pages)
    await interaction.followup.send(embed=pages[0].embed, view=view, ephemeral=True)
    await view.wait()

# async def update_user_settings_prompt(interaction: discord.Interaction) -> None:
#     user = await User.find_one(User.id == interaction.user.id)

#     if not user:
#         return

#     pages = [
#         EmbedAndField(discord.Embed(title="TEST 1: URL",
#                                     description="TEST 1"), "url"),
#         EmbedAndField(discord.Embed(title="TEST 2: PRIVATE",
#                                     description="TEST 2"), "private")
#     ]

#     view = UserSettingsPrompt(pages)
#     await interaction.followup.send(embed=pages[0].embed, view=view, ephemeral=True)
#     await view.wait()
