from typing import List

import discord


def channel_receiving_all_notification_types_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Denied",
        color=discord.Color.red())

    embed.description = "This channel is already receiving every type of notification"

    return embed


def channel_receiving_no_notification_types_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Denied",
        color=discord.Color.red())

    embed.description = "This channel is not receiving any type of notification yet"

    return embed


def set_channels_instructions_embed(channel_name: str, adding: bool) -> discord.Embed:
    embed = discord.Embed(title="Instructions", color=discord.Color.orange())

    embed.description = f"**#{channel_name}** channel can receive regular messages from the bot.\nHere are the message types:"

    embed.add_field(
        name="Bot maintenance and updates",
        value="Receive messages of when the bot is down and back up as well as a summary of any major updates to the bot",
        inline=False)

    embed.add_field(
        name="LeetCode daily question",
        value="Receive LeetCode's daily question at midnight (UTC)",
        inline=False)

    embed.add_field(
        name="Leaderboard daily and weekly winners",
        value="Receive the winners of the daily and weekly leaderboards at midnight (UTC)",
        inline=False)

    embed.add_field(
        name=f"Select which notification types the channel should {'start' if adding else 'stop'} receiving:", value="", inline=False)

    embed.set_footer(text="Note: please press the 'save' button twice")

    return embed


def channel_set_embed(channel_name: str, selected_options: List[str]) -> discord.Embed:
    embed = discord.Embed(title="Success", color=discord.Color.green())

    embed.description = f"**#{channel_name}** will now receive **{'**,** '.join(selected_options)}** notifications"

    return embed


def channel_remove_embed(channel_name: str, selected_options: List[str]) -> discord.Embed:
    embed = discord.Embed(title="Success", color=discord.Color.green())

    embed.description = f"**#{channel_name}** will now stop receiving **{'**,** '.join(selected_options)}** notifications"

    return embed
