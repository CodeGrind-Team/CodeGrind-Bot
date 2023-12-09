from dataclasses import dataclass
from typing import List

import discord
from beanie.odm.operators.update.general import Set

from database.models.user_model import User


@dataclass
class EmbedAndField:
    embed: discord.Embed
    field: str
    to_global_server: bool


class UserPreferencesPrompt(discord.ui.View):
    def __init__(self, pages: List[EmbedAndField], end_embed: discord.Embed, page_num: int = 0, *, timeout=180):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.curr_embed = self.pages[page_num].embed
        self.curr_field = self.pages[page_num].field
        self.to_global_server = self.pages[page_num].to_global_server
        self.end_embed = end_embed
        self.page_num = page_num

        self.curr_embed.set_footer(
            text=f"Question {page_num+1} of {len(self.pages)}")

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.blurple)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        guild_id = interaction.guild.id if not self.to_global_server else 0

        await User.find_one(User.id == interaction.user.id, User.display_information.server_id == guild_id).update(Set({f"display_information.$.{self.curr_field}": True}))
        await self.increment_page(interaction)

    @discord.ui.button(label='No', style=discord.ButtonStyle.gray)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        guild_id = interaction.guild.id if not self.to_global_server else 0

        await User.find_one(User.id == interaction.user.id, User.display_information.server_id == guild_id).update(Set({f"display_information.$.{self.curr_field}": False}))
        await self.increment_page(interaction)

    async def increment_page(self, interaction: discord.Interaction):
        self.page_num += 1

        if self.page_num == len(self.pages):
            await interaction.response.edit_message(embed=self.end_embed, view=None)
            # Stopped in case this view needs to be waited in the future.
            self.stop()
            return

        self.curr_embed = self.pages[self.page_num].embed
        self.curr_field = self.pages[self.page_num].field
        self.to_global_server = self.pages[self.page_num].to_global_server

        self.curr_embed.set_footer(
            text=f"Question {self.page_num+1} of {len(self.pages)}")

        await interaction.response.edit_message(embed=self.pages[self.page_num].embed, view=self)
