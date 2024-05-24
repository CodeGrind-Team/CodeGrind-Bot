from datetime import UTC, datetime

import discord

from database.models import Preference
from ui.embeds.preferences import preferences_update_prompt_embeds
from ui.views.preferences import UserPreferencesPromptView


async def update_user_preferences_prompt(
    interaction: discord.Interaction, reminder: bool = False
) -> None:
    """
    Sends a prompt to update user preferences if certain conditions are met.

    Checks if a user's preference needs updating, considering whether
    it's a reminder and the last time the preference was updated. If the conditions are
    met, it sends an interactive prompt to the user.

    :param reminder: Indicates if this is a reminder prompt. If `True`, the prompt is
    sent only if the preference has not been updated in over 30 days.
    """

    preference = await Preference.find_one(
        Preference.user_id == interaction.user.id,
        Preference.server_id == interaction.guild.id,
    )

    if not preference:
        return

    if (
        reminder
        and preference.last_updated
        and (datetime.now(UTC) - preference.last_updated.astimezone(UTC)).days <= 30
    ):
        return

    pages, end_embed = preferences_update_prompt_embeds()

    view = UserPreferencesPromptView(pages, end_embed)
    await interaction.followup.send(embed=pages[0].embed, view=view, ephemeral=True)
    await view.wait()

    preference.last_updated = datetime.now(UTC)
    await preference.save_changes()
