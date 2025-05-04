import discord
from discord import app_commands
from discord.ext import commands
from typing import Union

from bot.database import db, TableName


class Channel(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = self.bot.db

    @app_commands.command(
        name="channel_whitelist",
        description="Add the channel to the list of channel where the bot will interact",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def channel_whitelist(
        self,
        interaction: discord.Interaction,
        channel: Union[discord.TextChannel, discord.ForumChannel],
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Only server administrator can use this command", ephemeral=True
            )
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
        description="Remove the channel to the list of channel where the bot can interact",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def channel_blacklist(
        self,
        interaction: discord.Interaction,
        channel: Union[discord.TextChannel, discord.ForumChannel],
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Only server administrator can use this command", ephemeral=True
            )
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
                content="The channel <#"
                + str(channel.id)
                + "> will no longer check users message and give points when someone thanks another member.",
                ephemeral=True,
            )
        except discord.errors as e:
            await interaction.response.send_message(e, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Channel(bot))
