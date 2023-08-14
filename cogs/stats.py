import discord
from discord.ext import commands

from bot_globals import logger
from embeds.misc_embeds import error_embed
from embeds.stats_embeds import stats_embed, account_hidden_embed
from embeds.users_embeds import account_not_found_embed
from models.user_model import User
from utils.middleware import track_analytics


class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client

    @discord.app_commands.command(name="stats", description="Displays a user's stats")
    @track_analytics
    async def stats(self, interaction: discord.Interaction, user: discord.Member | None = None, display_publicly: bool = True) -> None:
        logger.info('file: cogs/stats.py ~ stats ~ run')

        await interaction.response.defer(ephemeral=not display_publicly)

        if not interaction.guild:
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user:
            user_id = user.id
        else:
            user_id = interaction.user.id

        user = await User.find_one(User.id == user_id)

        if not user:
            embed = account_not_found_embed()
            await interaction.followup.send(embed=embed)
            return

        display_information = next(
            (di for di in user.display_information if di.server_id == interaction.guild.id), None)

        if user.id != interaction.user.id and not display_information.url:
            embed = account_hidden_embed()
            await interaction.followup.send(embed=embed)
            return

        # Needed because if user already has connected their account to the bot
        # but hasn't connected their account to the corresponding server,
        # then display_information is None.
        embed, file = await stats_embed(user.leetcode_username, user.leetcode_username if display_information is None else display_information.name)

        if file is None:
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(embed=embed, file=file)


async def setup(client: commands.Bot):
    await client.add_cog(Stats(client))
