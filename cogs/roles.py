import discord
from discord import app_commands
from discord.ext import commands

from bot import DiscordBot
from middleware import defer_interaction, ensure_server_document
from views.roles import RolesView


class RolesCog(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    @app_commands.command(name="roles")
    @commands.has_permissions(administrator=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    async def roles(self, interaction: discord.Interaction) -> None:
        """
        Admins only: enable/disable CodeGrind roles
        """
        # TODO: complete
        await interaction.followup.send(
            embed=discord.Embed(title="test"), view=RolesView()
        )


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(RolesCog(bot))
