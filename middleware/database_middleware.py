from datetime import datetime
from functools import wraps
from typing import Callable

import discord
from beanie.odm.operators.update.general import Set

from database.models.analytics_model import Analytics
from database.models.server_model import Server
from database.models.user_model import User
from embeds.users_embeds import preferences_update_prompt_embeds
from views.user_settings_view import UserPreferencesPrompt


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


async def update_user_preferences_prompt(interaction: discord.Interaction, reminder: bool = False) -> None:
    user = await User.find_one(
        User.id == interaction.user.id)

    display_information = next(
        (di for di in user.display_information if di.server_id == interaction.guild.id), None)

    if not display_information:
        return

    if reminder and display_information.last_updated and (display_information.last_updated - datetime.utcnow()).days <= 30:
        return

    pages, end_embed = preferences_update_prompt_embeds()

    view = UserPreferencesPrompt(pages, end_embed)
    await interaction.followup.send(embed=pages[0].embed, view=view, ephemeral=True)
    await view.wait()

    await User.find_one(User.id == interaction.user.id, User.display_information.server_id == interaction.guild.id).update(Set({"display_information.$.last_updated": datetime.utcnow()}))
