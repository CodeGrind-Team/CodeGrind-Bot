import discord


def stats_embed(leetcode_username: str, rank: int, easy: int, medium: int, hard: int, total_questions_done: int, total_score: int) -> discord.Embed:
    embed = discord.Embed(
        title=f"Rank: {rank}", color=discord.Color.blue())

    embed.add_field(name="**Easy**",
                    value=f"{easy}", inline=True)

    embed.add_field(name="**Medium**",
                    value=f"{medium}", inline=True)

    embed.add_field(name="**Hard**",
                    value=f"{hard}", inline=True)

    embed.set_footer(
        text=f"Total: {total_questions_done} | Score: {total_score}")

    embed.set_author(
        name=f"{leetcode_username}'s LeetCode Stats",
    )

    return embed


def invalid_username_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Error",
        description="The username you entered is invalid",
        color=discord.Color.red())

    return embed


def account_hidden_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Cannot access data",
        description="The chosen user has their LeetCode details hidden as their `include_url` setting is set to OFF",
        color=discord.Color.red())

    return embed
