from typing import Awaitable, Callable, cast

import discord

from src.ui.embeds.roles import roles_created_embed, roles_removed_embed
from src.utils.common import GuildInteraction
from src.utils.roles import create_roles, remove_roles, update_roles


class RolesView(discord.ui.View):
    @discord.ui.button(label="Enable", style=discord.ButtonStyle.blurple)
    async def enable(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        guild_interaction = cast(GuildInteraction, interaction)

        async def modify_roles() -> None:
            await create_roles(guild_interaction.guild)
            await update_roles(guild_interaction.guild, guild_interaction.guild_id)

        await self.toggle(guild_interaction, modify_roles, roles_created_embed)

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        guild_interaction = cast(GuildInteraction, interaction)

        async def modify_roles() -> None:
            await remove_roles(guild_interaction.guild)

        await self.toggle(guild_interaction, modify_roles, roles_removed_embed)

    async def toggle(
        self,
        guild_interaction: GuildInteraction,
        modify_roles: Callable[[], Awaitable[None]],
        return_embed: Callable[[], discord.Embed],
    ) -> None:
        await guild_interaction.response.defer()
        message = await guild_interaction.original_response()

        self.enable.disabled, self.disable.disabled = True, True
        await guild_interaction.followup.edit_message(message.id, view=self)

        await modify_roles()

        await guild_interaction.followup.edit_message(
            message.id, embed=return_embed(), view=None
        )
