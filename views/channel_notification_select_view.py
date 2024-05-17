import discord
from beanie.odm.operators.update.array import AddToSet, Pull

from constants import NotificationOptions
from database.models.server_model import Server
from embeds.channels_embeds import channel_remove_embed, channel_set_embed


class NotificationOptionselect(discord.ui.Select):
    def __init__(
        self,
        selected_notification_options: list[discord.SelectOption],
        available_notification_options: list[str],
    ):

        self.selected_notification_options = selected_notification_options
        self.label_to_option = {
            "maintenance": NotificationOptions.MAINTENANCE,
            "daily question": NotificationOptions.DAILY_QUESTION,
            "leaderboard winners": NotificationOptions.WINNERS,
        }

        options = self._get_options(available_notification_options)

        super().__init__(
            placeholder="Select notification types",
            max_values=len(options),
            min_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        for label, notification_option in self.label_to_option.items():
            if label in self.values:
                self.selected_notification_options.append(notification_option)

    def _get_options(
        self, available_notification_options: list[str]
    ) -> list[discord.SelectOption]:
        """
        Get the options for the select menu.

        :param available_notification_options: The available notification types.
        """
        options = []

        for notification_option in available_notification_options:
            if notification_option == NotificationOptions.MAINTENANCE:
                select_option = discord.SelectOption(
                    label="maintenance", description="Get bot updates and downtime"
                )

                options.append(select_option)

            elif notification_option == NotificationOptions.DAILY_QUESTION:
                select_option = discord.SelectOption(
                    label="daily question",
                    description="Get the daily question every midnight (UTC)",
                )

                options.append(select_option)

            elif notification_option == NotificationOptions.WINNERS:
                select_option = discord.SelectOption(
                    label="leaderboard winners",
                    description="Display the daily and weekly leaderboard winners",
                )

                options.append(select_option)

        return options


class SaveButton(discord.ui.Button):
    def __init__(
        self,
        selected_notification_options: list[str],
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

        super().__init__(label="save", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction) -> None:
        if not self.selected_notification_options:
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
        server_id: int,
        channel_id: int,
        adding: bool,
        selected_notification_options: list[str],
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
                if notification_option in NotificationOptions.MAINTENANCE:
                    await Server.find_one(Server.id == server_id).update(
                        AddToSet({Server.channels.maintenance: channel_id})
                    )

                elif notification_option in NotificationOptions.DAILY_QUESTION:
                    await Server.find_one(Server.id == server_id).update(
                        AddToSet({Server.channels.daily_question: channel_id})
                    )

                elif notification_option in NotificationOptions.WINNERS:
                    await Server.find_one(Server.id == server_id).update(
                        AddToSet({Server.channels.winners: channel_id})
                    )

        else:
            for notification_option in selected_notification_options:
                if notification_option in NotificationOptions.MAINTENANCE:
                    await Server.find_one(Server.id == server_id).update(
                        Pull({Server.channels.maintenance: channel_id})
                    )

                elif notification_option in NotificationOptions.DAILY_QUESTION:
                    await Server.find_one(Server.id == server_id).update(
                        Pull({Server.channels.daily_question: channel_id})
                    )

                elif notification_option in NotificationOptions.WINNERS:
                    await Server.find_one(Server.id == server_id).update(
                        Pull({Server.channels.winners: channel_id})
                    )


class ChannelsSelectView(discord.ui.View):
    def __init__(
        self,
        server_id: int,
        channel_id: int,
        channel_name: str,
        available_notification_options: list[str],
        adding: bool,
        *,
        timeout=180
    ):

        super().__init__(timeout=timeout)

        self.selected_notification_options = []
        self.add_item(
            NotificationOptionselect(
                self.selected_notification_options, available_notification_options
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
