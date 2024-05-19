import discord
from discord.ext import commands

from constants import StatsCardExtensions
from database.models.preference_model import Preference
from database.models.user_model import User
from embeds.stats_embeds import account_hidden_embed, stats_embed
from embeds.users_embeds import account_not_found_embed
from middleware import defer_interaction


class StatsCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @discord.app_commands.command(name="stats", description="Displays a user's stats")
    @defer_interaction()
    async def stats(
        self,
        interaction: discord.Interaction,
        option: StatsCardExtensions,
        member: discord.Member | None = None,
    ) -> None:
        """
        Command to display a user's stats.

        :param option: The stats card option to select.
        :param member: The member whose stats to display.
        """
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
            option,
        )

        if not file:
            await interaction.followup.send(embed=embed)
            return

        await interaction.followup.send(embed=embed, file=file)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StatsCog(bot))
