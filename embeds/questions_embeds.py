import discord

def daily_problem_unsuccessful_embed() -> discord.Embed:
    embed = discord.Embed(title="Daily problem",
                          color=discord.Color.red())

    embed.description = "Daily problem could not be retrieved"

    return embed

def question_embed(question_id: str, question_content: str, question_constraints: str, question_difficulty: str, question_title: str, rating_text: str, question_link: str, question_total_accepted, question_total_submission, question_ac_rate, daily_question: bool = False) -> discord.Embed:
    if daily_question:
        question_title = "Daily Question: " + question_title

    color_dict = {"Easy": discord.Color.green(),
                  "Medium": discord.Color.orange(),
                  "Hard":  discord.Color.red()}

    color = color_dict[question_difficulty] if question_difficulty in color_dict else discord.Color.blue()

    embed = discord.Embed(title=f"{question_id}. {question_title}", url=question_link, description=question_content, color=color)
    
    embed.add_field(name='Constraints: ', value=question_constraints, inline=False)

    embed.add_field(name='Difficulty: ', value=question_difficulty, inline=True)

    if rating_text != "Doesn't exist":
        embed.add_field(name="Zerotrac Rating: ", value=rating_text, inline=True)

    embed.set_footer(text=f"Accepted: {question_total_accepted}  |  Submissions: {question_total_submission}  |  Acceptance Rate: {question_ac_rate}")

    return embed

def question_rating_embed(question_title: str, rating_text: str) -> discord.Embed:
    embed = discord.Embed(title="Zerotrac Rating",
                          color=discord.Color.magenta())

    embed.add_field(name="Question Name",
                    value=question_title.title(), inline=False)
    embed.add_field(name="Rating", value=rating_text, inline=False)

    return embed

def question_has_no_rating_embed() -> discord.Embed:
    embed = discord.Embed(title="Zerotrac Rating",
                          color=discord.Color.red())

    embed.description = "This question doesn't have a Zerotrac rating"

    return embed
