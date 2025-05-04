import discord

from discord import app_commands
from discord.ext import commands

from bot.database import TableName


class Leaderboard(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = self.bot.db

    @app_commands.command(
        name="leaderboard_thanks", description="See the leaderboard of thanks"
    )
    async def leaderboard_thanks(self, interaction: discord.Interaction):
        try:
            users = self.db.select(
                TableName.POINTS.value,
                where={"guild_id": interaction.guild_id},
                limit=10,
                order_by="points DESC",
            )
            guild_name = interaction.guild.name
            embed = discord.Embed(
                title=f"{guild_name} Top 10 Helpers",
                description="",
                color=0x1E1F22,
            )
            if interaction.guild.icon:
                embed.set_thumbnail(url=interaction.guild.icon.url)
            for i, user in enumerate(users):
                rank = i+1
                member = interaction.guild.get_member(user["discord_user_id"])
                if member is None:
                    continue
                desc = f"helped {user['points']} times\n-# ​ ​ ​ ​ ◉ and has thanked {user["num_of_thanks"]} times\n"
                if rank == 1:
                    desc = f"🥇__{member.mention}__ - " + desc
                elif rank == 2:
                    desc = f"🥈__{member.mention}__ - " + desc
                elif rank == 3:
                    desc = f"🥉__{member.mention}__ - " + desc
                else:
                    desc = f"{member.mention} - "+ desc
                embed.description += f"{rank}. {desc}"

            await interaction.response.send_message(embed=embed)
        except discord.errors.HTTPException as e:
            print(e)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
