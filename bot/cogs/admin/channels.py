import discord
from discord.ui import *
from discord import app_commands
from discord.ext import commands

from bot.database import db, TableName

class Channel(commands.Cog):
    def __init__(self,bot:commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="channel_whitelist",description="Add the channel to the list of channel where the bot can interact")
    async def channel_whitelist(self,interaction:discord.Interaction, channel: discord.TextChannel):
        try:
            await interaction.response.send_message(content="you are ranked")
        except discord.errors.HTTPException as e:
            await interaction.response.send_message(e, ephemeral=True)

    @app_commands.command(name="channel_blacklist",description="Remove the channel to the list of channel where the bot can interact")
    async def channel_blacklist(self,interaction:discord.Interaction, channel: discord.TextChannel):
        try:
            await interaction.response.send_message(content="you are ranked")
        except discord.errors.HTTPException as e:
            await interaction.response.send_message(e, ephemeral=True)
    

async def setup(bot):
    await bot.add_cog(Channel(bot))