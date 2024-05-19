import discord

from views.preferences_views import EmbedAndField


def synced_existing_user_embed() -> discord.Embed:
    embed = discord.Embed(title="Account synced", colour=discord.Colour.green())

    embed.description = "Your account has been synced and your preferences for this server have been saved successefully"

    return embed


def user_already_added_in_server_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Account already added to this server", colour=discord.Colour.blurple()
    )

    embed.description = "You have already added your account to this server"

    return embed


def connect_account_instructions_embed(
    generated_string: str, leetcode_id: str
) -> discord.Embed:
    embed = discord.Embed(title="Instructions", colour=discord.Colour.orange())
    embed.description = "Please temorarily change your LeetCode Account **Name** to the following generated sequence:"

    embed.add_field(
        name="Generated Sequence", value=f"{generated_string}", inline=False
    )

    embed.add_field(name="Username", value=f"{leetcode_id}", inline=False)

    embed.add_field(
        name="Account Name Change",
        value="You can do this by clicking [here](https://leetcode.com/profile/) and changing your **Name** (not your **LeetCode ID**).",
        inline=False,
    )

    embed.add_field(
        name="Time Limit",
        value="You have 60 seconds to change your name, otherwise, you will have to restart the process.",
        inline=False,
    )

    return embed


def profile_added_embed(leetcode_id: str, added: bool = True) -> discord.Embed:
    embed = discord.Embed(
        title=f"LeetCode account {'' if added else 'not '}added",
        colour=discord.Colour.green() if added else discord.Colour.red(),
    )
    embed.description = f"**LeetCode ID**: {leetcode_id}\n\nYou can now revert or change your LeetCode Name to whatever you desire."

    return embed


def account_removed_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Your account has been removed from this server",
        colour=discord.Colour.green(),
    )

    return embed


def account_permanently_deleted_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Your account has been permanently deleted", colour=discord.Colour.green()
    )

    return embed


def account_not_found_embed() -> discord.Embed:
    embed = discord.Embed(title="Account not found", colour=discord.Colour.red())

    embed.description = "The user hasn't linked their LeetCode account to this server yet! To connect to the bot use </add:1115756888185917542>"

    return embed


def preferences_update_prompt_embeds() -> tuple[list[EmbedAndField], discord.Embed]:
    pages = [
        EmbedAndField(
            discord.Embed(
                title="Update your profile preferences",
                description="Do you want your LeetCode profile url be visible on the leaderboards in this server?",
                colour=discord.Colour.teal(),
            ),
            "url",
            False,
        ),
        EmbedAndField(
            discord.Embed(
                title="Update your profile preferences",
                description="Do you want your LeetCode profile url be visible on the Global leaderboards?",
                colour=discord.Colour.teal(),
            ),
            "url",
            True,
        ),
        EmbedAndField(
            discord.Embed(
                title="Update your profile preferences",
                description="Do you want your Discord username be visible on the Global leaderboards?",
                colour=discord.Colour.teal(),
            ),
            "visible",
            True,
        ),
    ]

    end_embed = discord.Embed(
        title="Successfully updated your profile preferences",
        colour=discord.Colour.green(),
    )

    return pages, end_embed
