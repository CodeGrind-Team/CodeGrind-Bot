import discord


class RegisterModal(discord.ui.Modal, title="Connect your LeetCode account to CodeGrind"):
    answer = discord.ui.TextInput(label="What is your LeetCode ID?",
                                  style=discord.TextStyle.short,
                                  required=True)
