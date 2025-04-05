import discord

from src.ui.embeds.common import failure_embed, success_embed


def account_process_start_embed() -> discord.Embed:
    return discord.Embed(
        title="Connect LeetCode Account",
        description="Press the following button to start the process:",
        colour=discord.Colour.blurple(),
    )


def synced_existing_user_embed() -> discord.Embed:
    return success_embed(
        title="Account synced",
        description="Your account has been synced and your preferences for this "
        "server have been saved successfully",
    )


def user_already_added_in_server_embed() -> discord.Embed:
    return failure_embed(
        title="Account already added to this server",
        description="You have already added your account to this server",
    )


def connect_account_instructions_embed(
    generated_string: str, leetcode_id: str
) -> discord.Embed:
    embed = discord.Embed(
        title="Instructions",
        description="Please temporarily change your LeetCode Account **Name** to the "
        "following generated sequence:",
        colour=discord.Colour.orange(),
    )
    embed.add_field(
        name="Generated Sequence", value=f"{generated_string}", inline=False
    )

    embed.add_field(name="Username", value=f"{leetcode_id}", inline=False)

    embed.add_field(
        name="Account Name Change",
        value="You can do this by clicking [here](https://leetcode.com/profile/) and "
        "changing your **Name** (not your **LeetCode ID**).",
        inline=False,
    )

    embed.add_field(
        name="Time Limit",
        value="You have 60 seconds to change your name, otherwise, you will have to "
        "restart the process.",
        inline=False,
    )

    return embed


def profile_added_embed(leetcode_id: str, added: bool = True) -> discord.Embed:
    return discord.Embed(
        title=f"LeetCode account {'' if added else 'not '}added",
        description=f"**LeetCode ID**: {leetcode_id}\n\nYou can now revert or change "
        "your LeetCode Name to whatever you desire.",
        colour=discord.Colour.green() if added else discord.Colour.red(),
    )


def account_removed_embed() -> discord.Embed:
    return success_embed(
        title="Your account has been removed from this server",
    )


def account_permanently_deleted_embed() -> discord.Embed:
    return success_embed(title="Your account has been permanently deleted")


def account_not_found_embed() -> discord.Embed:
    return failure_embed(
        title="Account not found",
        description="The user hasn't linked their LeetCode account to this server yet! "
        "To connect to the bot use </add:1204499698933563422>",
    )
