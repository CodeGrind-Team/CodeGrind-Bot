import discord
from discord.ext import commands

from embeds.general_embeds import COMMAND_CATEGORIES, help_embed
from middleware import defer_interaction, track_analytics
from views.commands_help_view import CommandTypeSelectView


class GeneralCog(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @discord.app_commands.command(name="help", description="Help with CodeGrind Bot")
    @defer_interaction(ephemeral_default=True)
    @track_analytics
    async def help(self, interaction: discord.Interaction) -> None:
        """
        Display help information.

        :param interaction: The interaction context.
        """
        embed = help_embed(COMMAND_CATEGORIES["Home"])
        embed.set_footer(text="Love our bot? Vote on top.gg using /vote")

        await interaction.followup.send(
            embed=embed, view=CommandTypeSelectView(COMMAND_CATEGORIES)
        )

    @discord.app_commands.command(
        name="vote", description="Vote for the CodeGrind Bot on top.gg"
    )
    @defer_interaction(ephemeral_default=True)
    @track_analytics
    async def vote(self, interaction: discord.Interaction) -> None:
        """
        Display voting information.

        :param interaction: The interaction context.
        """
        embed = discord.Embed(
            title="Vote for CodeGrind Bot on top.gg ",
            description="https://top.gg/bot/1059122559066570885/vote",
            color=discord.Color.purple(),
        )

        await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(GeneralCog(client))
