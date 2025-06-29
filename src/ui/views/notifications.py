from typing import TYPE_CHECKING, cast

import discord
from beanie.odm.operators.update.array import AddToSet, Pull

from src.constants import NotificationOptions
from src.database.models import Server
from src.ui.embeds.common import error_embed, failure_embed
from src.ui.embeds.notifications import (
    channel_receiving_all_notification_options_embed,
    channel_receiving_no_notification_options_embed,
    channel_remove_embed,
    channel_set_embed,
    set_channels_instructions_embed,
)
from src.utils.common import GuildInteraction

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot


class NotificationOptionSelect(discord.ui.Select):
    def __init__(
        self,
        selected_notification_options: set[NotificationOptions],
        available_notification_options: set[NotificationOptions],
        adding: bool,
    ):

        self.label_to_option = {
            "Maintenance": NotificationOptions.MAINTENANCE,
            "Daily Question": NotificationOptions.DAILY_QUESTION,
            "Leaderboard Winners": NotificationOptions.WINNERS,
        }
        self.selected_notification_options = selected_notification_options
        options = self._get_options(available_notification_options)

        super().__init__(
            placeholder=f"Select the notification types to "
            f"{'enable' if adding else 'disable'}",
            max_values=len(options),
            min_values=1,
            options=list(options),
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        # self.values stores the labels of the selected options
        selected_options = set(
            map(lambda label: self.label_to_option[label], self.values)
        )

        for notification_option in NotificationOptions:
            if notification_option in selected_options:
                self.selected_notification_options.add(notification_option)

    def _get_options(
        self, available_notification_options: set[NotificationOptions]
    ) -> set[discord.SelectOption]:
        """
        Get the options for the select menu.

        :param available_notification_options: The available notification types.
        """
        options = set()

        for notification_option in available_notification_options:
            if notification_option == NotificationOptions.MAINTENANCE:
                select_option = discord.SelectOption(
                    label="Maintenance", description="Get bot updates and downtime"
                )

                options.add(select_option)

            elif notification_option == NotificationOptions.DAILY_QUESTION:
                select_option = discord.SelectOption(
                    label="Daily Question",
                    description="Get the daily question every midnight (UTC)",
                )

                options.add(select_option)

            elif notification_option == NotificationOptions.WINNERS:
                select_option = discord.SelectOption(
                    label="Leaderboard Winners",
                    description="Display the daily and weekly leaderboard winners",
                )

                options.add(select_option)

        return options


class SaveButton(discord.ui.Button):
    def __init__(
        self,
        selected_notification_options: set[NotificationOptions],
        adding: bool,
        server_id: int,
        channel_id: int,
        channel_name: str,
    ):

        self.adding = adding
        self.server_id = server_id
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.selected_notification_options = selected_notification_options

        super().__init__(label="Save", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction) -> None:
        if not self.selected_notification_options:
            embed = failure_embed(
                title="No notification types selected",
                description=f"Use the dropdown menu to select the notification types "
                f"to {'enable' if self.adding else 'disable'}",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await self._save_channel_options(
            self.server_id,
            self.channel_id,
            self.adding,
            self.selected_notification_options,
        )

        if self.adding:
            embed = channel_set_embed(
                self.channel_name, self.selected_notification_options
            )
            await interaction.response.edit_message(embed=embed, view=None)

        else:
            embed = channel_remove_embed(
                self.channel_name, self.selected_notification_options
            )
            await interaction.response.edit_message(embed=embed, view=None)

    async def _save_channel_options(
        self,
        server_id: int,
        channel_id: int,
        adding: bool,
        selected_notification_options: set[NotificationOptions],
    ) -> None:
        """
        Save the selected options for the channel.

        :param server_id: The server ID.
        :param channel_id: The channel ID.
        :param adding: Whether the options are being added or removed.
        :param selected_notification_options: The selected options.
        """

        if adding:
            for notification_option in selected_notification_options:
                if notification_option == NotificationOptions.MAINTENANCE:
                    await Server.find_one(Server.id == server_id).update(
                        AddToSet(
                            {Server.channels.maintenance: channel_id}  # type: ignore
                        )
                    )

                elif notification_option == NotificationOptions.DAILY_QUESTION:
                    await Server.find_one(Server.id == server_id).update(
                        AddToSet(
                            {Server.channels.daily_question: channel_id}  # type: ignore
                        )
                    )

                elif notification_option == NotificationOptions.WINNERS:
                    await Server.find_one(Server.id == server_id).update(
                        AddToSet({Server.channels.winners: channel_id})  # type: ignore
                    )

        else:
            for notification_option in selected_notification_options:
                if notification_option == NotificationOptions.MAINTENANCE:
                    await Server.find_one(Server.id == server_id).update(
                        Pull({Server.channels.maintenance: channel_id})  # type: ignore
                    )

                elif notification_option == NotificationOptions.DAILY_QUESTION:
                    await Server.find_one(Server.id == server_id).update(
                        Pull(
                            {Server.channels.daily_question: channel_id}  # type: ignore
                        )
                    )

                elif notification_option == NotificationOptions.WINNERS:
                    await Server.find_one(Server.id == server_id).update(
                        Pull({Server.channels.winners: channel_id})  # type: ignore
                    )


class ChannelsSelectView(discord.ui.View):
    def __init__(
        self,
        server_id: int,
        channel_id: int,
        channel_name: str,
        available_notification_options: set[NotificationOptions],
        adding: bool,
        *,
        timeout=180,
    ):

        super().__init__(timeout=timeout)

        self.selected_notification_options = set()
        self.add_item(
            NotificationOptionSelect(
                self.selected_notification_options,
                available_notification_options,
                adding,
            )
        )
        self.add_item(
            SaveButton(
                self.selected_notification_options,
                adding,
                server_id,
                channel_id,
                channel_name,
            )
        )


class SelectOperatorView(discord.ui.View):
    def __init__(
        self, bot: "DiscordBot", channel: discord.TextChannel, *, timeout=180
    ) -> None:
        self.bot = bot
        self.channel = channel
        self.field_to_option = {
            "maintenance": NotificationOptions.MAINTENANCE,
            "daily_question": NotificationOptions.DAILY_QUESTION,
            "winners": NotificationOptions.WINNERS,
        }
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.blurple)
    async def enable(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        guild_interaction = cast(GuildInteraction, interaction)
        await guild_interaction.response.defer()

        server_id = guild_interaction.guild_id

        if not (db_server := await Server.find_one(Server.id == server_id)):
            await guild_interaction.edit_original_response(embed=error_embed())
            return

        if all(self.channel.id in channel_id for _, channel_id in db_server.channels):
            embed = channel_receiving_all_notification_options_embed()
            await guild_interaction.edit_original_response(embed=embed, view=None)
            return

        available_notification_options = {
            self.field_to_option[field]
            for field, channel_id in db_server.channels
            if self.channel.id not in channel_id
        }

        embed = set_channels_instructions_embed(self.channel.id, adding=True)
        await guild_interaction.edit_original_response(
            embed=embed,
            view=ChannelsSelectView(
                server_id,
                self.channel.id,
                self.channel.name,
                available_notification_options,
                adding=True,
            ),
        )

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        guild_interaction = cast(GuildInteraction, interaction)
        await guild_interaction.response.defer()

        server_id = guild_interaction.guild_id

        if not (db_server := await Server.find_one(Server.id == server_id)):
            await guild_interaction.edit_original_response(embed=error_embed())
            return

        if all(
            self.channel.id not in channel_id for _, channel_id in db_server.channels
        ):
            await guild_interaction.edit_original_response(
                embed=channel_receiving_no_notification_options_embed()
            )
            return

        available_notification_options = {
            self.field_to_option[field]
            for field, channel_id in db_server.channels
            if self.channel.id in channel_id
        }

        embed = set_channels_instructions_embed(self.channel.id, adding=False)
        await guild_interaction.edit_original_response(
            embed=embed,
            view=ChannelsSelectView(
                server_id,
                self.channel.id,
                self.channel.name,
                available_notification_options,
                adding=False,
            ),
        )
