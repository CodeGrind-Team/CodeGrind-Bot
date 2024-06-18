import discord

from ui.constants import CommandCategory
from ui.embeds.common import error_embed
from ui.embeds.general import help_embed


class CommandCategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=CommandCategory.HOME.value,
                emoji="🏠",
                description="Return to main page",
            ),
            discord.SelectOption(
                label=CommandCategory.ACCOUNT.value,
                emoji="👤",
                description="Account commands",
            ),
            discord.SelectOption(
                label=CommandCategory.LEADERBOARD.value,
                emoji="📈",
                description="Leaderboard commands",
            ),
            discord.SelectOption(
                label=CommandCategory.STATISTICS.value,
                emoji="📊",
                description="Statistics commands",
            ),
            discord.SelectOption(
                label=CommandCategory.LEETCODE_PROBLEMS.value,
                emoji="📝",
                description="LeetCode Problems commands",
            ),
            discord.SelectOption(
                label=CommandCategory.NEETCODE_SOLUTIONS.value,
                emoji="💡",
                description="NeetCode Solutions commands",
            ),
            discord.SelectOption(
                label=CommandCategory.ROLES.value,
                emoji="🎭",
                description="CodeGrind roles commands",
            ),
            discord.SelectOption(
                label=CommandCategory.ADMIN.value,
                emoji="🔒",
                description="Admin commands",
            ),
            discord.SelectOption(
                label=CommandCategory.CODEGRIND_TEAM.value,
                emoji="👨‍💻",
                description="The CodeGrind Team",
            ),
        ]

        super().__init__(
            placeholder="Select command category",
            max_values=1,
            min_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        try:
            category = CommandCategory(self.values[0])
            embed = help_embed(category)
        except ValueError:
            await interaction.response.send_message(embed=error_embed(), ephemeral=True)
            return

        await interaction.response.edit_message(embed=embed)


class CommandCategorySelectView(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

        self.add_item(CommandCategorySelect())
