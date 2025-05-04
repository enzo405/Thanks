import discord
from discord import app_commands
from discord.ext import commands
from typing import Union

from bot.database import TableName


class StatsThank(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = self.bot.db

    @app_commands.command(name="stats_thanks", description="Get your merci stats")
    async def stats_thanks(
        self,
        interaction: discord.Interaction,
        target: Union[discord.Member, discord.User] = None,
    ):
        try:
            if target is None:
                target = interaction.user

            user = self.db.select(
                TableName.POINTS.value,
                where={"guild_id": interaction.guild.id, "discord_user_id": target.id},
            )

            if user:
                embed = discord.Embed(
                    title="",
                    description=f"{target.name} has {user[0]['points']} point(s) and has thanked {user[0]['num_of_thanks']} times",
                    color=0x1E1F22,
                )
            else:
                embed = discord.Embed(
                    title="",
                    description=f"{target.name} has 0 point and has thanked 0 times",
                    color=0x1E1F22,
                )
            embed.set_author(name=target.display_name, icon_url=target.avatar.url)

            await interaction.response.send_message(embed=embed, delete_after=120)
        except discord.errors.HTTPException as e:
            print(e)


async def setup(bot):
    await bot.add_cog(StatsThank(bot))
