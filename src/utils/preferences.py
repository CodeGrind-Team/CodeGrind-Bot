from datetime import UTC, datetime

from src.database.models import Profile
from src.ui.embeds.preferences import preferences_update_prompt_embeds
from src.ui.views.preferences import UserPreferencesPromptView
from src.utils.common import GuildInteraction

PREFERENCE_PROMPT_INTERVAL_DAYS = 365


async def update_user_preferences_prompt(
    interaction: GuildInteraction, reminder: bool = False
) -> None:
    """
    Sends a prompt to update user preferences if certain conditions are met.

    Checks if a user's preference needs updating, considering whether
    it's a reminder and the last time the preference was updated. If the conditions are
    met, it sends an interactive prompt to the user.

    :param reminder: Indicates if this is a reminder prompt. If `True`, the prompt is
    sent only if the preference has not been updated in over 30 days.
    """

    db_profile = await Profile.find_one(
        Profile.user_id == interaction.user.id,
        Profile.server_id == interaction.guild_id,
    )

    if not db_profile:
        return

    if (
        reminder
        and db_profile.preference.last_updated
        and (
            datetime.now(UTC) - db_profile.preference.last_updated.astimezone(UTC)
        ).days
        <= PREFERENCE_PROMPT_INTERVAL_DAYS
    ):
        return

    pages, end_embed = preferences_update_prompt_embeds()

    view = UserPreferencesPromptView(pages, end_embed)
    await interaction.followup.send(embed=pages[0].embed, view=view, ephemeral=True)
    await view.wait()

    db_profile.preference.last_updated = datetime.now(UTC)
    await db_profile.save_changes()
