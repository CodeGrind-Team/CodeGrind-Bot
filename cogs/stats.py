from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from constants import StatsCardExtensions
from database.models import Preference, User
from middleware import defer_interaction
from ui.embeds.stats import account_hidden_embed, stats_embed
from ui.embeds.users import account_not_found_embed

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


class StatsCog(commands.Cog):
    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot

    @app_commands.command(name="stats")
    @defer_interaction()
    async def stats(
        self,
        interaction: discord.Interaction,
        extension: StatsCardExtensions,
        user: discord.Member | None = None,
    ) -> None:
        """
        Display a user's stats.

        :param extension: The stats extension to add to the card.
        :param member: The user whose stats to display. Defaults to you.
        """
        member = user
        user_id = member.id if member else interaction.user.id
        user = await User.find_one(User.id == user_id)

        if not user:
            await interaction.followup.send(embed=account_not_found_embed())
            return

        preference = await Preference.find_one(
            Preference.user_id == user_id, Preference.server_id == interaction.guild.id
        )

        if user.id != interaction.user.id and not preference.url:
            await interaction.followup.send(embed=account_hidden_embed())
            return

        # Needed because if user already has connected their account to the bot
        # but hasn't connected their account to the corresponding server,
        # then display_information is None.
        embed, file = await stats_embed(
            self.bot,
            user.leetcode_id,
            (preference.name if preference else user.leetcode_id),
            extension,
        )

        if not file:
            await interaction.followup.send(embed=embed)
            return

        await interaction.followup.send(embed=embed, file=file)


async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(StatsCog(bot))
