import discord


def synced_existing_user() -> discord.Embed:
    embed = discord.Embed(title="Account synced",
                          color=discord.Color.green())

    embed.description = "Your account has been synced and your preferences for this server have been saved successefully"

    return embed


def user_already_added_in_server() -> discord.Embed:
    embed = discord.Embed(title="Account already added to this server",
                          color=discord.Color.blurple())

    embed.description = "You have already added your account to this server"

    return embed


def connect_account_instructions(generated_string: str, leetcode_username: str) -> discord.Embed:
    embed = discord.Embed(title="Instructions",
                          color=discord.Color.orange())
    embed.description = "Please change your LeetCode Profile Name to the generated sequence:"

    embed.add_field(name="Generated Sequence",
                    value=f"{generated_string}",
                    inline=False)

    embed.add_field(name="Username",
                    value=f"{leetcode_username}", inline=False)

    embed.add_field(
        name="Profile Name Change",
        value="You can do this by clicking [here](https://leetcode.com/profile/) and changing your Name.",
        inline=False)

    embed.add_field(
        name="Time Limit",
        value="You have 60 seconds to change your name, otherwise, you will have to restart the process.",
        inline=False)

    return embed


def profile_added(leetcode_username: str, added: bool = True) -> discord.Embed:
    embed = discord.Embed(title=f"Profile {'' if added else 'not'} added",
                          color=discord.Color.green() if added else discord.Color.red())
    embed.add_field(name="Username:",
                    value=f"{leetcode_username}", inline=False)

    return embed
