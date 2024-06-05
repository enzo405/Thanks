import discord
from discord.ui import *
from discord import app_commands
from discord.ext import commands

from bot.database import TableName

class Leaderboard(commands.Cog):
    def __init__(self,bot:commands.Bot) -> None:
        self.bot = bot
        self.db = self.bot.db

    @app_commands.command(name="leaderboard_thanks",description="See the leaderboard of thanks")
    async def leaderboard_thanks(self,interaction:discord.Interaction):
        try:
            users = self.db.select(TableName.POINTS.value, limit=10, order_by="points DESC")
            embed = discord.Embed(title="Top 10 Thanker", description=f"", color=0x1e1f22)
            for i, user in enumerate(users):
                member = interaction.guild.get_member(user["discord_user_id"])
                if member is None:
                    continue
                embed.description += f"{i+1}. {member.mention} - {user['points']} thanks\n"
            
            await interaction.response.send_message(embed=embed)
        except discord.errors.HTTPException as e:
            print(e)
    

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))