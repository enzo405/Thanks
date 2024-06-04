import discord
from discord.ui import *
from discord import app_commands
from discord.ext import commands
from typing import Union
from datetime import datetime

from bot.database import db, TableName

class ChannelPerm(commands.Cog):
    def __init__(self,bot:commands.Bot) -> None:
        self.bot = bot
        self.db = self.bot.db

    @app_commands.command(name="rank_thanks",description="Get your rank")
    async def rank_thanks(self,interaction:discord.Interaction, target: Union[discord.Member, discord.User] = None):
        try:
            if target is None:
                target = interaction.user
            
            date_now = datetime.now()

            user = self.db.select(TableName.POINTS.value, where={"guild_id": interaction.guild.id, "discord_user_id": target.id})
            embed = discord.Embed(title="Rank", description=f"{target.mention} has {user[0]['points']} points", color=0x00ff00)
            embed.add_field(name="", value=f"{target.mention} has thanked {user[0]['num_of_thanks']} times", inline=False)
            embed.set_footer(text=f"Ranking system - {date_now.strftime('%Y-%m-%d %H:%M:%S')}")
            embed.set_author(name=target.display_name, icon_url=target.avatar.url)
            
            await interaction.response.send_message(embed=embed)
        except discord.errors.HTTPException as e:
            await interaction.response.send_message(e, ephemeral=True)
    

async def setup(bot):
    await bot.add_cog(ChannelPerm(bot))