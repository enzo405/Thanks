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

        if (
            role.permissions.administrator
            or role.permissions.moderate_members
            or role.permissions.manage_roles
            or role.permissions.manage_channels
        ):
            await interaction.response.send_message(
                "You cannot assign an autorole to a role with manages permissions (roles, channels, members).",
                ephemeral=True,
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
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred: {e}", ephemeral=True
            )

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

    @app_commands.command(
        name="show_autoroles",
        description="Show all autoroles for the server",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def show_autoroles(
        self,
        interaction: discord.Interaction,
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Only server administrator can use this command", ephemeral=True
            )
            return

        server_autoroles = self.db.select(
            TableName.AUTOROLES.value,
            where={"guild_id": interaction.guild.id},
            order_by="threshold DESC",
        )

        # Build the response embed
        embed = discord.Embed(
            title="Autoroles",
            description="Here are the autoroles for this server:",
            color=discord.Color.blue(),
        )
        if not server_autoroles:
            embed.add_field(
                name="No autoroles",
                value="There are no autoroles set up for this server.",
                inline=False,
            )
        else:
            embed.description = "Here are the autoroles for this server:\n\n"
            for autorole in server_autoroles:
                print(autorole)
                role_id = autorole["role_id"]
                threshold = autorole["threshold"]
                embed.description += f"<@&{role_id}>: {threshold} points\n"

        try:
            await interaction.response.send_message(embed=embed)
        except discord.errors.HTTPException as e:
            await interaction.response.send_message(e, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Autorole(bot))
