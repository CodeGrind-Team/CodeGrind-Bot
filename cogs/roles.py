from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from middleware import defer_interaction, ensure_server_document
from ui.embeds.roles import roles_menu_embed
from ui.views.roles import RolesView

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


class RolesCog(commands.Cog):
    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot

    @app_commands.command(name="roles")
    @commands.has_permissions(administrator=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    async def roles(self, interaction: discord.Interaction) -> None:
        """
        Admins only: Enable or disable CodeGrind roles
        """
        await interaction.followup.send(embed=roles_menu_embed(), view=RolesView())


async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(RolesCog(bot))
