import discord
from discord.ui import *
from discord import app_commands
from discord.ext import commands
from typing import Union

from bot.database import db, TableName

class ChannelPerm(commands.Cog):
    def __init__(self,bot:commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="rank_thanks",description="Get your rank")
    async def rank_thanks(self,interaction:discord.Interaction, target: Union[discord.Member, discord.User] = None):
        try:
            await interaction.response.send_message(content="you are ranked")
        except discord.errors.HTTPException as e:
            await interaction.response.send_message(e, ephemeral=True)
    

async def setup(bot):
    await bot.add_cog(ChannelPerm(bot))