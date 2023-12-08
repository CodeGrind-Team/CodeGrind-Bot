from typing import List, Tuple

import discord
from beanie.odm.operators.update.general import Set

from database.models.user_model import User


class UserSettingsProcess(discord.ui.View):
    def __init__(self, pages: List[Tuple[discord.Embed, str]], page_num: int = 0, *, timeout=180):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.curr_embed = self.pages[page_num][0]
        self.curr_field = self.pages[page_num][1]
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
        self.curr_embed = self.pages[self.page_num][0]
        self.curr_field = self.pages[self.page_num][1]

        await interaction.message.edit(embed=self.pages[self.page_num])
        await interaction.response.edit_message(view=self)
