from typing import Dict, List

import discord

from embeds.channels_embeds import channel_remove_embed, channel_set_embed
from embeds.general_embeds import help_embed, not_creator_embed
from embeds.misc_embeds import error_embed
from utils.channels import get_options, save_channel_options


class Pagination(discord.ui.View):
    def __init__(self, user_id: int | None = None, pages: list[discord.Embed] | None = None, page: int = 0, *, timeout=180):
        super().__init__(timeout=timeout)
        self.page = page
        self.user_id = user_id

        if pages is None:
            self.pages = []
        else:
            self.pages = pages

        self.max_page = len(self.pages) - 1

        if self.page == 0:
            self.previous.style = discord.ButtonStyle.gray
            self.previous.disabled = True

        if self.page == self.max_page:
            self.next.style = discord.ButtonStyle.gray
            self.next.disabled = True

    @discord.ui.button(label='<', style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self.user_id is None or interaction.user.id != self.user_id or interaction.message is None:
            embed = not_creator_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if self.page - 1 >= 0:
            self.page -= 1
            await interaction.message.edit(embed=self.pages[self.page])

            if self.page == 0:
                button.style = discord.ButtonStyle.gray
                button.disabled = True

        self.next.style = discord.ButtonStyle.blurple
        self.next.disabled = False

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='>', style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self.user_id is None or interaction.user.id != self.user_id or interaction.message is None:
            embed = not_creator_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if self.page + 1 <= self.max_page:
            self.page += 1
            await interaction.message.edit(embed=self.pages[self.page])

            if self.page == self.max_page:
                button.style = discord.ButtonStyle.gray
                button.disabled = True

        self.previous.style = discord.ButtonStyle.blurple
        self.previous.disabled = False

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='🗑️', style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.user_id or interaction.message is None:
            embed = not_creator_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.message.delete()


class NotificationTypeSelect(discord.ui.Select):
    def __init__(self, selected_options: List[discord.SelectOption], available_types: List[str]):
        self.selected_options = selected_options
        self.label_to_type = {"maintenance": "maintenance",
                              "daily question": "daily_question", "leaderboard winners": "winners"}

        options = get_options(available_types)

        super().__init__(placeholder="Select notification types",
                         max_values=len(options), min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
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


class CommandTypeSelect(discord.ui.Select):
    def __init__(self, command_categories: Dict[str, str]):
        self.command_categories = command_categories

        options = [
            discord.SelectOption(
                label="Home", emoji="🏠", description="Return to main page"),
            discord.SelectOption(
                label="Account", description="Account commands"),
            discord.SelectOption(label="Leaderboard",
                                 description="Leaderboard commands"),
            discord.SelectOption(label="Statistics",
                                 description="Statistics commands"),
            discord.SelectOption(label="LeetCode Questions",
                                 description="LeetCode Questions commands"),
            discord.SelectOption(label="Roles",
                                 description="CodeGrind roles"),
            discord.SelectOption(label="Admin", description="Admin commands")
        ]

        super().__init__(placeholder="Select command category",
                         max_values=1, min_values=1,  options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.values[0] in ["Home", "Account", "Leaderboard", "Statistics", "LeetCode Questions", "Roles", "Admin"]:
            embed = help_embed(self.command_categories[self.values[0]])

        else:
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.edit_message(embed=embed)


class CommandTypeSelectView(discord.ui.View):
    def __init__(self, command_categories, *, timeout=180):
        super().__init__(timeout=timeout)

        self.add_item(CommandTypeSelect(command_categories))
