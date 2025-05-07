from bot.cogs.stats import setup
from bot.cogs.admin.channels import setup
from bot.cogs.leaderboard import setup
from bot.cogs.admin.autorole import setup

import discord

cogs = [
    "bot.cogs.stats",
    "bot.cogs.admin.channels",
    "bot.cogs.leaderboard",
    "bot.cogs.admin.autorole",
]


async def load_cogs(bot: discord.Client, cog_list: list):
    for cog in cog_list:
        try:
            await bot.load_extension(cog)
            print(f"Cog loaded: {cog}")
        except Exception as e:
            print(f"Error loading cog {cog}: {e}")
