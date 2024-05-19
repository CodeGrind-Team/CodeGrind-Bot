import discord
from discord.ext import commands

from middleware import admins_only, defer_interaction, ensure_server_document
from views.roles_views import RolesView


class RolesCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command(
        name="roles",
        # description="Admins only: enable or disable CodeGrind roles",
    )
    @discord.app_commands.checks.bot_has_permissions(manage_roles=True)
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @admins_only
    async def roles(self, interaction: discord.Interaction) -> None:
        """
        Command to enable or disable CodeGrind roles assignment.
        """
        await interaction.followup.send(
            embed=discord.Embed(title="test"), view=RolesView()
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RolesCog(bot))
