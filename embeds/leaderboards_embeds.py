import discord
import pytz

from bot_globals import DIFFICULTY_SCORE
from models.server_model import Server


class Pagination(discord.ui.View):
    def __init__(self, user_id: int | None = None, pages: list[discord.Embed] | None = None, page: int = 0):
        super().__init__()
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
            await interaction.response.defer()
            return

        if self.page - 1 >= 0:
            self.page -= 1
            await interaction.message.edit(embed=self.pages[self.page])

            if self.page == 0:
                button.style = discord.ButtonStyle.gray
                button.disabled = True

        # if self.page < self.max_page:
        self.next.style = discord.ButtonStyle.blurple
        self.next.disabled = False

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='>', style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self.user_id is None or interaction.user.id != self.user_id or interaction.message is None:
            await interaction.response.defer()
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
            await interaction.response.defer()
            return

        await interaction.message.delete()


def empty_leaderboard_embed() -> discord.Embed:
    embed = discord.Embed(
            title=f"Leaderboard is empty",
            description="No one has added their LeetCode username yet",
            color=discord.Color.red())
    
    return embed

def leaderboard_embed(server: Server, page_i: int, page_count: int, title: str, leaderboard: str) -> discord.Embed:
    embed = discord.Embed(title=title,
                            color=discord.Color.yellow())

    embed.description = "\n".join(leaderboard)

    last_updated = pytz.timezone("UTC").localize(
        server.last_updated).astimezone(pytz.timezone(server.timezone)).strftime("%d/%m/%Y %H:%M %Z")

    embed.set_footer(
        text=f"Easy: {DIFFICULTY_SCORE['easy']} point, Medium: {DIFFICULTY_SCORE['medium']} points, Hard: {DIFFICULTY_SCORE['hard']} points\nUpdated on {last_updated}\nPage {page_i + 1}/{page_count}")
    
    return embed