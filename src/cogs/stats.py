from enum import Enum
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from constants import MILESTONE_ROLES, StatsCardExtensions
from database.models import Profile, User
from middleware import defer_interaction
from ui.embeds.stats import account_hidden_embed, stats_embed
from ui.embeds.users import account_not_found_embed
from utils.roles import get_highest_tier_info

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


class StatsCog(commands.Cog):
    class StatsCardExtensionsField(Enum):
        Activity = StatsCardExtensions.ACTIVITY
        Heatmap = StatsCardExtensions.HEATMAP
        Contest = StatsCardExtensions.CONTEST
        Default = StatsCardExtensions.NONE

    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot

    @app_commands.command(name="stats")
    @defer_interaction()
    async def stats(
        self,
        interaction: discord.Interaction,
        extension: StatsCardExtensionsField,
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

        profile = await Profile.find_one(
            Profile.user_id == user_id, Profile.server_id == interaction.guild.id
        )

        if not profile or (
            user.id != interaction.user.id and not profile.preference.url
        ):
            await interaction.followup.send(embed=account_hidden_embed())
            return

        # Fetch user's score
        user_score = user.stats.submissions.score

        # Determine the milestone role based on user's score
        milestone_info = get_highest_tier_info(MILESTONE_ROLES, user_score)
        milestone_filename = f"{milestone_info.title}.png"
        milestone_icon_file = discord.File(
            milestone_info.icon_path, filename=milestone_filename
        )

        # Create the embed with the title as the display name
        embed, statscard_file = await stats_embed(
            self.bot,
            user.leetcode_id,
            profile.preference.name,
            profile.preference.url,
            extension.value,
        )

        # Set the footer with the rank and the icon
        embed.set_footer(
            text=milestone_info.role_name,
            icon_url=f"attachment://{milestone_filename}",
        )

        files = list(filter(None, [statscard_file, milestone_icon_file]))
        await interaction.followup.send(embed=embed, files=files)


async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(StatsCog(bot))
