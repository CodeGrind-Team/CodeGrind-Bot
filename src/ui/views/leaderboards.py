import discord

from src.ui.embeds.general import not_creator_embed


class LeaderboardPagination(discord.ui.View):
    def __init__(
        self,
        user_id: int | None,
        pages: list[discord.Embed],
        page: int = 0,
        *,
        timeout=180
    ):
        super().__init__(timeout=timeout)
        self.page = page
        self.user_id = user_id

        if pages is None:
            self.pages = []
        else:
            self.pages = pages

        self.max_page = len(self.pages) - 1

        if self.page == 0:
            self.previous.disabled, self.previous.style = True, discord.ButtonStyle.gray
            self.start.disabled, self.start.style = True, discord.ButtonStyle.gray

        if self.page == self.max_page:
            self.next.disabled, self.next.style = True, discord.ButtonStyle.gray
            self.end.disabled, self.end.style = True, discord.ButtonStyle.gray

    @discord.ui.button(label="<<", style=discord.ButtonStyle.blurple)
    async def start(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if (
            self.user_id is None
            or interaction.user.id != self.user_id
            or interaction.message is None
        ):
            embed = not_creator_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        self.page = 0
        await interaction.message.edit(embed=self.pages[self.page])

        button.disabled, button.style = True, discord.ButtonStyle.gray
        self.previous.disabled, self.previous.style = True, discord.ButtonStyle.gray
        self.next.disabled, self.next.style = False, discord.ButtonStyle.blurple
        self.end.disabled, self.end.style = False, discord.ButtonStyle.blurple

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="<", style=discord.ButtonStyle.blurple)
    async def previous(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if (
            self.user_id is None
            or interaction.user.id != self.user_id
            or interaction.message is None
        ):
            embed = not_creator_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if self.page - 1 >= 0:
            self.page -= 1
            await interaction.message.edit(embed=self.pages[self.page])

            if self.page == 0:
                button.disabled, button.style = True, discord.ButtonStyle.gray
                self.start.disabled, self.start.style = True, discord.ButtonStyle.gray

        self.next.disabled, self.next.style = False, discord.ButtonStyle.blurple
        self.end.disabled, self.end.style = False, discord.ButtonStyle.blurple

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label=">", style=discord.ButtonStyle.blurple)
    async def next(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if (
            self.user_id is None
            or interaction.user.id != self.user_id
            or interaction.message is None
        ):
            embed = not_creator_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if self.page + 1 <= self.max_page:
            self.page += 1
            await interaction.message.edit(embed=self.pages[self.page])

            if self.page == self.max_page:
                button.disabled, button.style = True, discord.ButtonStyle.gray
                self.end.disabled, self.end.style = True, discord.ButtonStyle.gray

        self.previous.disabled, self.previous.style = False, discord.ButtonStyle.blurple
        self.start.disabled, self.start.style = False, discord.ButtonStyle.blurple

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.blurple)
    async def end(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if (
            self.user_id is None
            or interaction.user.id != self.user_id
            or interaction.message is None
        ):
            embed = not_creator_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        self.page = self.max_page
        await interaction.message.edit(embed=self.pages[self.page])

        button.disabled, button.style = True, discord.ButtonStyle.gray
        self.next.disabled, self.next.style = False, discord.ButtonStyle.gray
        self.previous.disabled, self.previous.style = False, discord.ButtonStyle.blurple
        self.start.disabled, self.start.style = False, discord.ButtonStyle.blurple

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="🗑️", style=discord.ButtonStyle.red)
    async def delete(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user.id != self.user_id or interaction.message is None:
            embed = not_creator_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.message.delete()
