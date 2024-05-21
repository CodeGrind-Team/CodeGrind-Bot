import discord

from constants import NotificationOptions


def channel_receiving_all_notification_options_embed() -> discord.Embed:
    return discord.Embed(
        title="Denied",
        description="This channel is already receiving every type of notification",
        colour=discord.Colour.red(),
    )


def channel_receiving_no_notification_options_embed() -> discord.Embed:
    return discord.Embed(
        title="Denied",
        description="This channel is not receiving any type of notification yet",
        colour=discord.Colour.red(),
    )


def set_channels_instructions_embed(channel_id: int, adding: bool) -> discord.Embed:
    embed = discord.Embed(
        title="Instructions",
        description=f"""<#{channel_id}> channel can receive regular messages from the
          bot.\nHere are the message types:""",
        colour=discord.Colour.orange(),
    )

    embed.add_field(
        name="Bot maintenance and updates",
        value="""Receive messages of when the bot is down and back up as well as a
          summary of any major updates to the bot""",
        inline=False,
    )

    embed.add_field(
        name="LeetCode daily question",
        value="Receive LeetCode's daily question at midnight (UTC)",
        inline=False,
    )

    embed.add_field(
        name="Leaderboard daily and weekly winners",
        value="""Receive the winners of the daily and weekly leaderboards at midnight
          (UTC)""",
        inline=False,
    )

    embed.add_field(
        name=f"""Select which notification types the channel should
          {'start' if adding else 'stop'} receiving:""",
        value="",
        inline=False,
    )

    embed.set_footer(text="Note: please press the 'save' button twice!")

    return embed


def channel_set_embed(
    channel_name: str, selected_options: list[NotificationOptions]
) -> discord.Embed:
    embed = discord.Embed(title="Success", colour=discord.Colour.green())
    embed.description = f"**#{channel_name}** will now receive **{'**,** '.join(map(lambda option: option.value, selected_options))}** notifications"

    return embed


def channel_remove_embed(
    channel_name: str, selected_options: list[NotificationOptions]
) -> discord.Embed:
    return discord.Embed(
        title="Success",
        description=f"""**#{channel_name}** will now stop receiving
          **{'**,** '.join(map(lambda option: option.value, selected_options))}**
            notifications""",
        colour=discord.Colour.green(),
    )
