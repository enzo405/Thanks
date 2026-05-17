import discord
from discord import app_commands
from discord.ext import commands
from typing import Union

from bot.database import TableName

_ADMIN_ONLY_MSG = "Only server administrator can use this command"


class Channel(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = self.bot.db

    @app_commands.command(
        name="channel_whitelist",
        description="Remove the channel from the blacklisted channels, allowing the bot to interact in it",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def channel_whitelist(
        self,
        interaction: discord.Interaction,
        channel: Union[discord.TextChannel, discord.ForumChannel],
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(_ADMIN_ONLY_MSG, ephemeral=True)
            return

        if channel.id not in [
            channel["channel_id"]
            for channel in self.bot.guilds_config[channel.guild.id][
                "blacklisted_channel"
            ]
        ]:
            await interaction.response.send_message(
                content="The channel is already whitelisted", ephemeral=True
            )
            return

        try:
            self.db.delete(
                TableName.CHANNELS.value,
                {"guild_id": channel.guild.id, "channel_id": channel.id},
            )
            self.bot.fetch_guilds_config()
            await interaction.response.send_message(
                content=f"The channel <#{channel.id}> will now check users message and give points when someone thanks another member.",
                ephemeral=True,
            )
        except discord.errors.HTTPException as e:
            await interaction.response.send_message(e, ephemeral=True)

    @app_commands.command(
        name="channel_blacklist",
        description="Add the channel to the blacklisted channels, preventing the bot from interacting in it",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def channel_blacklist(
        self,
        interaction: discord.Interaction,
        channel: Union[discord.TextChannel, discord.ForumChannel],
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(_ADMIN_ONLY_MSG, ephemeral=True)
            return

        if channel.id in [
            channel["channel_id"]
            for channel in self.bot.guilds_config[channel.guild.id][
                "blacklisted_channel"
            ]
        ]:
            await interaction.response.send_message(
                content="The channel is already blacklisted", ephemeral=True
            )
            return

        try:
            self.db.insert(
                TableName.CHANNELS.value,
                {"guild_id": channel.guild.id, "channel_id": channel.id},
            )
            self.bot.fetch_guilds_config()
            await interaction.response.send_message(
                content=f"The channel <#{channel.id}> will no longer check users message and give points when someone thanks another member.",
                ephemeral=True,
            )
        except discord.errors as e:
            await interaction.response.send_message(e, ephemeral=True)

    @app_commands.command(
        name="show_blacklisted_channels",
        description="Show all blacklisted channels for the server",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def show_blacklisted_channels(
        self,
        interaction: discord.Interaction,
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(_ADMIN_ONLY_MSG, ephemeral=True)
            return

        blacklisted_ids = {
            c["channel_id"]
            for c in self.bot.guilds_config[interaction.guild.id]["blacklisted_channel"]
        }

        embed = discord.Embed(
            title="Blacklisted Channels",
            description="Here are the blacklisted channels for this server:",
            color=discord.Color.blue(),
        )
        if not blacklisted_ids:
            embed.add_field(
                name="No blacklisted channels",
                value="There are no blacklisted channels for this server.",
                inline=False,
            )
        else:
            embed.description = "Here are the blacklisted channels for this server:\n\n"
            for channel_id in blacklisted_ids:
                embed.description += f"<#{channel_id}>\n"

        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.errors.HTTPException as e:
            await interaction.response.send_message(e, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Channel(bot))
