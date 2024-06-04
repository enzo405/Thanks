from bot.cogs.stats import *
from bot.cogs.admin.channels import *

cogs = [
    'bot.cogs.stats',
    'bot.cogs.admin.channels'
]

async def load_cogs(bot: discord.Client, cog_list: list):
    for cog in cog_list:
        try:
            await bot.load_extension(cog)
            print(f"Cog loaded: {cog}")
        except Exception as e:
            print(f"Error loading cog {cog}: {e}")