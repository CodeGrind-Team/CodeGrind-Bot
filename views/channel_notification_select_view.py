from typing import List

import discord

from embeds.channels_embeds import channel_remove_embed, channel_set_embed
from utils.channels_utils import get_options, save_channel_options


class NotificationTypeSelect(discord.ui.Select):
    def __init__(self, selected_options: List[discord.SelectOption], available_types: List[str]):
        self.selected_options = selected_options
        self.label_to_type = {"maintenance": "maintenance",
                              "daily question": "daily_question", "leaderboard winners": "winners"}

        options = get_options(available_types)

        super().__init__(placeholder="Select notification types",
                         max_values=len(options), min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        for label, notification_type in self.label_to_type.items():
            if label in self.values:
                self.selected_options.append(notification_type)


class SaveButton(discord.ui.Button):
    def __init__(self, selected_options: List[str], adding: bool, server_id: int, channel_id: int, channel_name: str):
        self.adding = adding
        self.server_id = server_id
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.selected_options = selected_options

        super().__init__(label="save", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction) -> None:
        if not self.selected_options:
            return

        await save_channel_options(self.server_id, self.channel_id, self.adding, self.selected_options)

        if self.adding:
            embed = channel_set_embed(self.channel_name, self.selected_options)
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = channel_remove_embed(
                self.channel_name, self.selected_options)
            await interaction.response.edit_message(embed=embed, view=None)


class ChannelsSelectView(discord.ui.View):
    def __init__(self, server_id: int, channel_id: int, channel_name: str, available_types: List[str], adding: bool, *, timeout=180):
        super().__init__(timeout=timeout)

        self.selected_options = []
        self.add_item(NotificationTypeSelect(
            self.selected_options, available_types))
        self.add_item(SaveButton(self.selected_options, adding,
                      server_id, channel_id, channel_name))
