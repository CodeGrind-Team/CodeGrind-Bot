from enum import Enum
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from constants import StatsCardExtensions, MILESTONE_ROLES, RANK_IMAGES
from database.models import Profile, User
from middleware import defer_interaction
from ui.embeds.stats import account_hidden_embed, stats_embed
from ui.embeds.users import account_not_found_embed

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
        current_milestone_role = "No Rank"  # Default role if no match is found
        for milestone, (role_name, _) in MILESTONE_ROLES.items():
            if user_score >= milestone:
                current_milestone_role = role_name.split(" (")[0]  # Extract the word before the bracket

        # Get the image URL for the current milestone role
        rank_image_url = RANK_IMAGES.get(current_milestone_role, None)

        # Create the embed with the title as the display name
        embed, file = await stats_embed(
            self.bot,
            user.leetcode_id,
            member.display_name,  # Just the display name
            (profile.preference.url if profile else False),
            extension.value,
        )

        if not file:
            await interaction.followup.send(embed=embed)
            return

        # Set the footer with the rank and the icon
        embed.set_footer(
            text=f"Milestone Rank: {current_milestone_role}",
            icon_url=rank_image_url if rank_image_url else discord.Embed.Empty  # Set icon_url if available
        )

        await interaction.followup.send(embed=embed, file=file)


async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(StatsCog(bot))
