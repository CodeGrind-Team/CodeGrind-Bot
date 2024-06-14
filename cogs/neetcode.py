from typing import TYPE_CHECKING
from enum import Enum

import discord
from beanie.odm.operators.update.general import Set
from discord import app_commands
from discord.ext import commands
from constants import Language
from ui.modals.problems import ProblemSearchModal
from ui.embeds.neetcode import search_neetcode_embed
from functools import partial

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot

class NeetcodeCog(commands.Cog):
    class LanguageField(Enum):
        Python = Language.PYTHON3
        Java = Language.JAVA
        CPP = Language.CPP
        JavaScript = Language.JAVASCRIPT
        TypeScript = Language.TYPESCRIPT
        Go = Language.GO
        Swift = Language.SWIFT
        CSharp = Language.CSHARP
        Rust = Language.RUST
        Kotlin = Language.KOTLIN
        Ruby = Language.RUBY
        C = Language.C
        Scala = Language.SCALA
        Dart = Language.DART    
    
    def __init__(self, bot:"DiscordBot") -> None:
        self.bot = bot

    @app_commands.command(name="neetcode")
    async def neetcode(self, interaction: discord.Interaction, language: LanguageField = LanguageField.Python) -> None:
        """
        Get neetcode solution of leetcode problem
        """                                                         
        await interaction.response.send_modal(ProblemSearchModal(self.bot, partial(search_neetcode_embed, language=language.value)))

async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(NeetcodeCog(bot))
