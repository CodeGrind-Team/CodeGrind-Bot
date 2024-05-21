import discord


def roles_created_embed() -> discord.Embed:
    return discord.Embed(
        title="Success",
        description="The roles have been created",
        colour=discord.Colour.green(),
    )


def roles_removed_embed() -> discord.Embed:
    return discord.Embed(
        title="Success",
        description="The roles have been removed",
        colour=discord.Colour.green(),
    )


def missing_manage_roles_permission_embed() -> discord.Embed:
    return discord.Embed(
        title="Error",
        description="""CodeGrind Bot does not have `manage roles` permission.\nPlease
          enable this permission in the bot's role.""",
        colour=discord.Colour.red(),
    )
