import discord


def daily_completed_embed(completed: bool) -> discord.Embed:
    embed = discord.Embed()

    if not completed:
        embed.title = "Your latest submission isn't the LeetCode daily!"
        embed.color = discord.Color.red()

    else:
        embed.title = "Successfully registered that you've completed the LeetCode daily today"
        embed.color = discord.Color.green()

    return embed
