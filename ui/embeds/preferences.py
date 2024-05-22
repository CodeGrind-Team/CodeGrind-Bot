import discord

from ui.constants import PreferenceField
from ui.embeds.common import success_embed
from ui.views.preferences import EmbedAndField


def preferences_update_prompt_embeds() -> tuple[list[EmbedAndField], discord.Embed]:
    pages = [
        EmbedAndField(
            embed=discord.Embed(
                title="Update your profile preferences",
                description="Would you like your Discord username to be visible on "
                "the global leaderboards?",
                colour=discord.Colour.teal(),
            ),
            field=PreferenceField.GLOBAL_ANONYMOUS,
        ),
        EmbedAndField(
            embed=discord.Embed(
                title="Update your profile preferences",
                description="Would you like your LeetCode profile URL to be visible "
                "on this server's leaderboards?",
                colour=discord.Colour.teal(),
            ),
            field=PreferenceField.LOCAL_URL,
        ),
        EmbedAndField(
            embed=discord.Embed(
                title="Update your profile preferences",
                description="Would you like your LeetCode profile URL to be visible "
                "on the global leaderboards?",
                colour=discord.Colour.teal(),
            ),
            field=PreferenceField.GLOBAL_URL,
        ),
    ]

    end_embed = success_embed(description="Your profile preferences have been updated")

    return pages, end_embed
