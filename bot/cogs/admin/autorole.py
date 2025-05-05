import discord
from discord import app_commands
from discord.ext import commands

from bot.database import TableName


class Autorole(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = self.bot.db

    @app_commands.command(
        name="add_autorole",
        description="Add an autorole for a certain threshold of thanks",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def add_autorole(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        threshold: int,
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Only server administrator can use this command", ephemeral=True
            )
            return

        try:
            self.db.insert(
                TableName.AUTOROLES.value,
                {
                    "guild_id": interaction.guild.id,
                    "role_id": role.id,
                    "threshold": threshold,
                },
            )
            await interaction.response.send_message(
                content=f"The role <@&{role.id}> will now be given to users with a total of {threshold} points.",
                ephemeral=True,
            )
        except discord.errors.HTTPException as e:
            await interaction.response.send_message(e, ephemeral=True)

    @app_commands.command(
        name="remove_autorole",
        description="Remove all autorole of a certain role",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_autorole(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Only server administrator can use this command", ephemeral=True
            )
            return

        try:
            self.db.delete(
                TableName.AUTOROLES.value,
                {
                    "guild_id": interaction.guild.id,
                    "role_id": role.id,
                },
            )
            await interaction.response.send_message(
                content=f"The role <@&{role.id}> isn't in the autoroles anymore.",
                ephemeral=True,
            )
        except discord.errors.HTTPException as e:
            await interaction.response.send_message(e, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Autorole(bot))
