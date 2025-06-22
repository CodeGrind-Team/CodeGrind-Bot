from dataclasses import dataclass
from typing import cast

import discord
from beanie.odm.operators.update.general import Set

from src.constants import GLOBAL_LEADERBOARD_ID
from src.database.models import Profile
from src.ui.constants import PreferenceField
from src.utils.common import GuildInteraction


@dataclass
class EmbedAndField:
    embed: discord.Embed
    field: PreferenceField


class UserPreferencesPromptView(discord.ui.View):
    def __init__(
        self,
        pages: list[EmbedAndField],
        end_embed: discord.Embed,
        page_num: int = 0,
        *,
        timeout=180,
    ):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.curr_embed = self.pages[page_num].embed
        self.curr_field = self.pages[page_num].field
        self.end_embed = end_embed
        self.page_num = page_num

        self.curr_embed.set_footer(text=f"Question {page_num + 1} of {len(self.pages)}")

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.blurple)
    async def yes(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        guild_interaction = cast(GuildInteraction, interaction)

        await self._update_preference(
            guild_interaction.guild_id, guild_interaction.user.id, True
        )
        await self._increment_page(interaction)

    @discord.ui.button(label="No", style=discord.ButtonStyle.gray)
    async def no(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        guild_interaction = cast(GuildInteraction, interaction)

        await self._update_preference(
            guild_interaction.guild_id, guild_interaction.user.id, False
        )
        await self._increment_page(interaction)

    async def _update_preference(
        self, guild_id: int, user_id: int, value: bool
    ) -> None:
        if self.curr_field in (
            PreferenceField.GLOBAL_URL,
            PreferenceField.GLOBAL_ANONYMOUS,
        ):
            guild_id = GLOBAL_LEADERBOARD_ID

        if self.curr_field in (PreferenceField.LOCAL_URL, PreferenceField.GLOBAL_URL):
            await Profile.find_one(
                Profile.user_id == user_id,
                Profile.server_id == guild_id,
            ).update(
                Set({Profile.preference.url: value})
            )  # type: ignore

        elif self.curr_field == PreferenceField.GLOBAL_ANONYMOUS:
            await Profile.find_one(
                Profile.user_id == user_id,
                Profile.server_id == guild_id,
            ).update(
                Set({Profile.preference.anonymous: not value})
            )  # type: ignore

    async def _increment_page(self, interaction: discord.Interaction):
        self.page_num += 1

        if self.page_num == len(self.pages):
            await interaction.response.edit_message(embed=self.end_embed, view=None)
            # Stopped so that the view can be waited.
            self.stop()
            return

        self.curr_embed = self.pages[self.page_num].embed
        self.curr_field = self.pages[self.page_num].field

        self.curr_embed.set_footer(
            text=f"Question {self.page_num + 1} of {len(self.pages)}"
        )

        await interaction.response.edit_message(
            embed=self.pages[self.page_num].embed, view=self
        )
