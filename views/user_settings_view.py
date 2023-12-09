from dataclasses import dataclass
from typing import List

import discord
from beanie.odm.operators.update.general import Set

from database.models.user_model import User


@dataclass
class EmbedAndField:
    embed: discord.Embed
    field: str


class UserSettingsPrompt(discord.ui.View):
    def __init__(self, pages: List[EmbedAndField], page_num: int = 0, *, timeout=180):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.curr_embed = self.pages[page_num].embed
        self.curr_field = self.pages[page_num].field
        self.page_num = page_num

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.blurple)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await User.find_one(User.id == interaction.user.id, User.display_information.server_id == interaction.guild.id).update(Set({f"display_information.$.{self.curr_field}": True}))
        await self.increment_page(interaction)

    @discord.ui.button(label='No', style=discord.ButtonStyle.gray)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await User.find_one(User.id == interaction.user.id, User.display_information.server_id == interaction.guild.id).update(Set({f"display_information.$.{self.curr_field}": False}))
        await self.increment_page(interaction)

    async def increment_page(self, interaction: discord.Interaction):
        self.page_num += 1

        if self.page_num == len(self.pages):
            # TODO: send finished embed
            self.stop()
            return

        self.curr_embed = self.pages[self.page_num].embed
        self.curr_field = self.pages[self.page_num].field

        self.curr_embed.set_footer(
            text=f"Question {self.page_num+1} of {len(self.pages)}")

        await interaction.response.edit_message(embed=self.pages[self.page_num].embed, view=self)
