import discord
from discord.ext import commands

from bot_globals import logger
from embeds.general_embeds import help_embed


class General(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="help", description="Displays the help menu")
    async def help(self, interaction: discord.Interaction) -> None:
        logger.info("file: cogs/help.py ~ help ~ run")

        is_admin = isinstance(
            interaction.user, discord.Member) and interaction.user.guild_permissions.administrator

        embed = help_embed(is_admin)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # command for voting
    @discord.app_commands.command(name="vote", description="Vote for the bot on top.gg")
    async def vote(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(title="Vote for the bot on top.gg: ",
                              description="https://top.gg/bot/1059122559066570885/vote",
                              color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(General(client))
