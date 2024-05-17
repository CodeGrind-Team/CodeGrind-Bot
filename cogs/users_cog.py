import discord
from discord.ext import commands

from database.models.user_model import User
from embeds.users_embeds import (
    account_not_found_embed,
    account_permanently_deleted_embed,
    account_removed_embed,
)
from middleware import defer_interaction, ensure_server_document, track_analytics
from middleware.database_middleware import update_user_preferences_prompt
from views.register_or_login_view import RegisterOrLoginView


class UsersCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command(
        name="add", description="Connect your LeetCode account to this server"
    )
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @track_analytics
    async def add(self, interaction: discord.Interaction) -> None:
        """
        Adds a user to the server in the system.

        :param interaction: The Discord interaction.
        """
        await interaction.followup.send(
            embed=discord.Embed(
                title="Connect LeetCode Account",
                description="Press the following button to start the process:",
                colour=discord.Colour.blurple(),
            ),
            view=RegisterOrLoginView(self.bot),
        )

    @discord.app_commands.command(
        name="update", description="Update your profile on this server's leaderboards"
    )
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @track_analytics
    async def update(self, interaction: discord.Interaction) -> None:
        """
        Initiates the preference updater prompt.

        :param interaction: The Discord interaction.
        """
        user_id = interaction.user.id

        user = await User.find_one(User.id == user_id)

        if user:
            await update_user_preferences_prompt(interaction)
            return

        embed = account_not_found_embed()
        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(
        name="remove", description="Remove your profile from this server's leaderboard"
    )
    @defer_interaction(ephemeral_default=True)
    @ensure_server_document
    @track_analytics
    async def remove(
        self, interaction: discord.Interaction, permanently_delete: bool = False
    ) -> None:
        """
        Removes (or permanently deletes) a user from the system for the selected server.

        :param interaction: The Discord interaction.
        """
        server_id = interaction.guild.id
        user_id = interaction.user.id

        user = await User.find_one(User.id == user_id)

        if not user:
            await interaction.followup.send(embed=account_not_found_embed())
            return

        if permanently_delete:
            await delete_user(user_id)
            # ! TODO
            # await Server.find_one(Server.id == server_id).update(
            #     Pull({Server.users: {"$id": user_id}})
            # )

            # await Server.find_one(Server.id == GLOBAL_LEADERBOARD_ID).update(
            #     Pull({Server.users: {"$id": user_id}})
            # )
            # await user.delete()
            await interaction.followup.send(embed=account_permanently_deleted_embed())
            return

        await unlink_user(user_id, server_id)
        # ! TODO
        # await user.update(Pull({User.display_information: {"server_id": server_id}}))
        # await Server.find_one(Server.id == server_id).update(
        #     Pull({Server.users: {"$id": user_id}})
        # )

        await interaction.followup.send(embed=account_removed_embed())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UsersCog(bot))
