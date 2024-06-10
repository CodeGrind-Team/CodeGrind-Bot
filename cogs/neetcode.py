from typing import TYPE_CHECKING

import discord
import pytz
from beanie.odm.operators.update.general import Set
from discord import app_commands
from discord.ext import commands
from ui.modals.neetcode import NeetcodeSearchModal

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot

class NeetcodeCog(commands.Cog):
    
    def __init__(self, bot:"DiscordBot") -> None:
        self.bot = bot

    @app_commands.command(name="neetcode")
    async def neet(self, interaction: discord.Interaction) -> None:
        """
        Get neetcode solution of leetcode propblem
        """

        await interaction.response.send_modal(NeetcodeSearchModal(self.bot))

async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(NeetcodeCog(bot))
