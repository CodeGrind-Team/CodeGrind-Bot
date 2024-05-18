from typing import Dict

import discord

from embeds.general_embeds import help_embed
from embeds.misc_embeds import error_embed


class CommandCategorySelect(discord.ui.Select):
    def __init__(self, command_categories: Dict[str, str]):
        self.command_categories = command_categories

        options = [
            discord.SelectOption(
                label="Home", emoji="🏠", description="Return to main page"
            ),
            discord.SelectOption(
                label="Account", emoji="👤", description="Account commands"
            ),
            discord.SelectOption(
                label="Leaderboard", emoji="📈", description="Leaderboard commands"
            ),
            discord.SelectOption(
                label="Statistics", emoji="📊", description="Statistics commands"
            ),
            discord.SelectOption(
                label="LeetCode Questions",
                emoji="📝",
                description="LeetCode Questions commands",
            ),
            discord.SelectOption(
                label="Roles", emoji="🎭", description="CodeGrind roles"
            ),
            discord.SelectOption(
                label="Admin", emoji="🔒", description="Admin commands"
            ),
            discord.SelectOption(
                label="CodeGrind Team",
                emoji="👨‍💻",
                description="CodeGrind Team commands",
            ),
        ]

        super().__init__(
            placeholder="Select command category",
            max_values=1,
            min_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.values[0] in [
            "Home",
            "Account",
            "Leaderboard",
            "Statistics",
            "LeetCode Questions",
            "Roles",
            "Admin",
            "CodeGrind Team",
        ]:
            embed = help_embed(self.command_categories[self.values[0]])

        else:
            embed = error_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.edit_message(embed=embed)


class CommandCategorySelectView(discord.ui.View):
    def __init__(self, command_categories, *, timeout=180):
        super().__init__(timeout=timeout)

        self.add_item(CommandCategorySelect(command_categories))
